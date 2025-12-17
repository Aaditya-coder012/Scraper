import sys
import os
import io
import logging
import traceback
import pandas as pd
import requests
import re
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# --- ENVIRONMENT FIX ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- MODULE IMPORTS ---
try:
    from scraper import HTMLFetcher, HTMLParser, MetadataExtractor, WhoisLookup, crawl_site
except ImportError as e:
    logging.error(f"FATAL: Missing modules: {e}")
    # Fallback placeholders omitted for brevity; ensure scraper folder has __init__.py

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
CORS(app, resources={r"/*": {"origins": "*"}})

SERPER_API_KEY = "7a8e0ca2485bd022e521147b9d713577001f46a9"
logging.basicConfig(level=logging.INFO)

# --- ROUTES ---
@app.route("/")
def home():
    return render_template("UI.html")

@app.route("/templates/metadata.html")
def metadata_page():
    return render_template("metadata.html")

@app.route("/templates/pagecontent.html")
def pagecontent_page():
    return render_template("pagecontent.html")

@app.route("/api/crawl", methods=["POST"])
def api_crawl():
    try:
        data = request.get_json() or {}
        url = data.get("url")
        max_p = int(data.get("max_pages", 5))
        if not url: return jsonify({"error": "URL required"}), 400
        
        results = crawl_site(url, max_pages=min(max_p, 50))
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/scrape", methods=["POST"])
def scrape_route():
    data = request.get_json() or {}
    url = data.get("url")
    if not url: return jsonify({"error": "URL required"}), 400

    try:
        fetcher = HTMLFetcher(use_proxy=False)
        parser = HTMLParser()
        extractor = MetadataExtractor()
        whois = WhoisLookup()

        html = fetcher.fetch(url)
        if not html: return jsonify({"error": "Cloud block or timeout"}), 500
        
        soup = parser.parse(html)
        metadata = extractor.extract(soup, url)
        metadata["whois"] = whois.lookup(url)

        return jsonify(metadata)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)