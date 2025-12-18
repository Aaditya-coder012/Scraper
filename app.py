import io
import os
import re
import logging
import traceback
import pandas as pd
import requests
from flask import Flask, request, jsonify, send_file, render_template, Response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# --- APP CONFIGURATION ---
app = Flask(__name__)
# Ensures Render/Proxies pass the correct IP and Protocol
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
CORS(app)

# Use Environment Variables for Security (Set these in Render Dashboard)
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "7a8e0ca2485bd022e521147b9d713577001f46a9")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- IMPORT EXTERNAL UTILITIES ---
try:
    from scraper.email_crawler import crawl_site
    from scraper.fetcher import HTMLFetcher
    from scraper.parser import HTMLParser
    from scraper.metadata_extractor import MetadataExtractor
    from scraper.whois_lookup import WhoisLookup
except ImportError as e:
    logging.error(f"Module Import Error: {e}. Check folder structure.")
    # Fallback placeholders to prevent app crash
    def crawl_site(*args, **kwargs): return []
    class HTMLFetcher: 
        def fetch(self, url): return "Module Missing"

# --- FRONTEND NAVIGATION ---
@app.route("/")
def home():
    return render_template("UI.html")

@app.route("/metadata")
def metadata_page():
    return render_template("metadata.html")

@app.route("/extractor")
def extractor_page():
    return render_template("pagecontent.html")

# --- ENGINE 1: SEO & METADATA SCRAPER ---
@app.route("/scrape", methods=["POST"])
def scrape_route():
    data = request.get_json() or {}
    url = data.get("url")
    keyword = data.get("keyword")
    
    if not url:
        return jsonify({"error": "URL required"}), 400

    try:
        fetcher, parser, extractor, whois = HTMLFetcher(), HTMLParser(), MetadataExtractor(), WhoisLookup()
        html = fetcher.fetch(url)
        soup = parser.parse(html)
        metadata = extractor.extract(soup, url)
        
        # Add WHOIS data
        try:
            metadata["whois"] = whois.lookup(url)
        except:
            metadata["whois"] = "N/A"

        # Logic for Keyword Highlighting (Snippets)
        if keyword:
            text = soup.get_text(" ", strip=True)
            # Find snippets: 50 chars before and after the keyword
            matches = re.findall(rf'(.{{0,50}}{re.escape(keyword)}.{{0,50}})', text, re.IGNORECASE)
            metadata["keyword"] = {
                "term": keyword,
                "count": len(matches),
                "context": [m.strip() for m in matches[:5]] # Return top 5
            }

        return jsonify(metadata)
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# --- ENGINE 2: WEB SEARCH (SERPER) ---
@app.route("/search", methods=["POST"])
def search_route():
    data = request.get_json() or {}
    query = data.get("keyword") # Matches the ID in your search form
    
    if not query:
        return jsonify({"error": "Search query required"}), 400

    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    try:
        resp = requests.post("https://google.serper.dev/search", headers=headers, json={"q": query})
        resp.raise_for_status()
        organic_results = resp.json().get("organic", [])
        
        results = [{"title": i.get("title"), "link": i.get("link"), "snippet": i.get("snippet")} for i in organic_results]
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

# --- ENGINE 3: CONTACT EXTRACTOR (EMAIL CRAWLER) ---
@app.route("/api/crawl", methods=["POST"])
def api_crawl():
    try:
        data = request.get_json() or {}
        url = data.get("url")
        max_pages = int(data.get("max_pages", 1))
        
        if not url:
            return jsonify({"success": False, "error": "URL is required"}), 400

        results = crawl_site(start_url=url, max_pages=min(max_pages, 50))
        return jsonify({"success": True, "count": len(results), "results": results})
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

# --- UNIFIED DOWNLOAD SYSTEM ---
@app.route("/download_csv", methods=["POST"])
def download_csv():
    data_wrapper = request.get_json() or {}
    mode = data_wrapper.get('type') # 'search', 'scrape', or 'crawl'
    content = data_wrapper.get('content') or data_wrapper.get('results')

    if not content:
        return jsonify({"error": "No data to export"}), 400
    
    try:
        if mode == 'search' or mode == 'crawl':
            df = pd.DataFrame(content)
        else:
            # Audit Logic (Vertical Report)
            keyword_info = content.get("keyword", {})
            report_data = [
                ["SECTION", "FIELD", "VALUE"],
                ["SITE INFO", "Title", content.get("title")],
                ["SITE INFO", "URL", content.get("source_url")],
                ["SEO", "Description", content.get("description")],
                ["KEYWORD", "Term", keyword_info.get("term", "N/A")],
                ["KEYWORD", "Count", keyword_info.get("count", 0)]
            ]
            df = pd.DataFrame(report_data[1:], columns=report_data[0])

        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding="utf-8-sig")
        buffer.seek(0)
        return send_file(
            buffer, 
            as_attachment=True, 
            download_name=f"GrowthSwift_{mode}_Export.csv", 
            mimetype="text/csv"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- PRODUCTION STARTUP ---
if __name__ == '__main__':
    # Use Render's port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)