
import os
import io
import traceback
import pandas as pd
import requests
import json
import re
import logging
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# --- IMPORT EXTERNAL UTILITIES ---
try:
    # Ensure the 'scraper' directory has an __init__.py file
    from scraper.email_crawler import crawl_site
    from scraper.fetcher import HTMLFetcher
    from scraper.parser import HTMLParser
    from scraper.metadata_extractor import MetadataExtractor
    from scraper.whois_lookup import WhoisLookup
except ImportError as e:
    logging.error(f"FATAL WARNING: Could not import scraper modules: {e}")
    
    # Placeholders to prevent the app from crashing on startup
    class HTMLFetcher:
        def fetch(self, url): raise NotImplementedError("Fetcher module missing.")
    class HTMLParser:
        def parse(self, html): raise NotImplementedError("Parser module missing.")
    class MetadataExtractor:
        def extract(self, soup, url): raise NotImplementedError("Extractor module missing.")
    class WhoisLookup:
        def lookup(self, url): raise NotImplementedError("Whois module missing.")
    def crawl_site(*args, **kwargs): 
        raise NotImplementedError("Email Crawler module missing.")

# --- APP CONFIGURATION ---
app = Flask(__name__)
# Standard ProxyFix for handling headers if behind a proxy like Nginx
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
CORS(app)

# Configuration
SERPER_API_KEY = "7a8e0ca2485bd022e521147b9d713577001f46a9"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global state (Note: Use Redis/Database for production)
last_scraped_data = None  
last_mode = None          

# --- FRONTEND ROUTES ---
@app.route("/")
def home():
    # Points to the main control panel now
    return render_template("UI.html") 

@app.route("/templates/metadata.html")
def metadata_page():
    return render_template("metadata.html")

@app.route("/templates/pagecontent.html")
def pagecontent_page():
    return render_template("pagecontent.html")

# --- API ROUTES: EMAIL CRAWLER ---
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

@app.route("/api/download", methods=["POST"])
def api_download():
    try:
        data = request.get_json() or {}
        results = data.get("results", [])
        columns = ["source_page", "email", "first_name", "last_name", "designations"]
        df = pd.DataFrame(results, columns=columns)
        
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding="utf-8")
        buffer.seek(0)
        return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name="emails.csv")
    except Exception as e:
        return jsonify({"error": "Download failed"}), 500

# --- API ROUTES: METADATA & SEARCH ---
@app.route("/search", methods=["POST"])
def search_route():
    global last_scraped_data, last_mode
    data = request.get_json() or {}
    query = data.get("keyword")
    
    if not query:
        return jsonify({"error": "Keyword required"}), 400

    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    try:
        resp = requests.post("https://google.serper.dev/search", headers=headers, json={"q": query})
        resp.raise_for_status()
        search_results = [{"title": i.get("title"), "link": i.get("link"), "snippet": i.get("snippet")} 
                          for i in resp.json().get("organic", [])]
        
        last_scraped_data = search_results
        last_mode = 'search'
        return jsonify({"results": search_results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/scrape", methods=["POST"])
def scrape_route():
    global last_scraped_data, last_mode
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
        
        try:
            metadata["whois"] = whois.lookup(url)
        except:
            metadata["whois"] = "N/A"

        if keyword:
            text = soup.get_text(" ", strip=True)
            sentences = re.findall(r'([^.]*?' + re.escape(keyword) + r'[^.]*\.)', text, re.IGNORECASE)
            metadata["keyword"] = {"term": keyword, "count": len(sentences), "context": sentences[:5]}

        last_scraped_data = metadata
        last_mode = 'scrape'
        return jsonify(metadata)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download_csv")
def download_csv():
    global last_scraped_data, last_mode
    if not last_scraped_data:
        return jsonify({"error": "No data available"}), 400
    
    try:
        if last_mode == 'search':
            df = pd.DataFrame(last_scraped_data)
        else:
            rows = [{"Field": k, "Value": v} for k, v in last_scraped_data.items() if not isinstance(v, dict)]
            df = pd.DataFrame(rows)
            
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="report.csv", mimetype="text/csv")
    except Exception as e:
        return jsonify({"error": "Export failed"}), 500

# --- STARTUP ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)