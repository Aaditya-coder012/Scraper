import os
import logging
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Import your existing scraper modules
from scraper import HTMLFetcher, HTMLParser, MetadataExtractor, WhoisLookup, crawl_site

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
CORS(app, resources={r"/*": {"origins": "*"}})

SERPER_API_KEY = "7a8e0ca2485bd022e521147b9d713577001f46a9"

# --- NAVIGATION ROUTES (Match your existing file names) ---
@app.route("/")
def home():
    return render_template("UI.html")

@app.route("/templates/metadata.html")
def metadata_page():
    return render_template("metadata.html")

@app.route("/templates/pagecontent.html")
def pagecontent_page():
    return render_template("pagecontent.html")

# --- FIXED SEARCH ROUTE ---
@app.route("/api/search", methods=["POST"])
def api_search():
    try:
        data = request.get_json() or {}
        query = data.get("query")
        if not query: return jsonify({"error": "Query required"}), 400
        
        headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
        payload = {"q": query}
        response = requests.post('https://google.serper.dev/search', headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- EXISTING SCRAPE & CRAWL ROUTES ---
@app.route("/scrape", methods=["POST"])
def scrape_route():
    data = request.get_json() or {}
    url = data.get("url")
    try:
        fetcher = HTMLFetcher()
        html = fetcher.fetch(url)
        metadata = MetadataExtractor().extract(HTMLParser().parse(html), url)
        metadata["whois"] = WhoisLookup().lookup(url)
        return jsonify(metadata)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/crawl", methods=["POST"])
def api_crawl():
    data = request.get_json() or {}
    results = crawl_site(data.get("url"), max_pages=int(data.get("max_pages", 5)))
    return jsonify({"success": True, "results": results})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)