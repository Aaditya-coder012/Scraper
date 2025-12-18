import io
import os
import traceback
import pandas as pd
import requests
import json
import re
import logging
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# --- APP CONFIGURATION ---
app = Flask(__name__, template_folder="templates", static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
CORS(app)

# Use Environment Variables for Security
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "7a8e0ca2485bd022e521147b9d713577001f46a9")
logging.basicConfig(level=logging.INFO)

# --- IMPORT EXTERNAL UTILITIES ---
try:
    from scraper.email_crawler import crawl_site
    from scraper.fetcher import HTMLFetcher
    from scraper.parser import HTMLParser
    from scraper.metadata_extractor import MetadataExtractor
    from scraper.whois_lookup import WhoisLookup
except ImportError as e:
    logging.error(f"Module Import Error: {e}")
    # Placeholders kept to prevent crash
    def crawl_site(*args, **kwargs): return []

# --- ROUTES (FRONTEND) ---
@app.route("/")
def home():
    return render_template("UI.html")

@app.route("/metadata") # Removed /templates/ prefix for cleaner URLs
def metadata_page():
    return render_template("metadata.html")

@app.route("/pagecontent")
def pagecontent_page():
    return render_template("pagecontent.html")

# --- API ROUTES ---
@app.route("/api/crawl", methods=["POST"])
def api_crawl():
    try:
        data = request.get_json() or {}
        url = data.get("url")
        max_pages = int(data.get("max_pages", 1))
        if not url:
            return jsonify({"success": False, "error": "URL required"}), 400
        results = crawl_site(start_url=url, max_pages=min(max_pages, 50))
        return jsonify({"success": True, "count": len(results), "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/download_csv", methods=["POST"])
def download_csv():
    try:
        data_wrapper = request.get_json() or {}
        mode = data_wrapper.get('type')
        content = data_wrapper.get('content') or data_wrapper.get('results', [])

        if mode == 'search':
            df = pd.DataFrame(content)
        else:
            # Flatten logic for Scraper Audit
            df = pd.DataFrame([content]) # Simplified for safety

        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding="utf-8-sig")
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="GrowthSwift_Data.csv", mimetype="text/csv")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- PRODUCTION STARTUP ---
if __name__ == '__main__':
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)