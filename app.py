import io
import os
import pandas as pd
import logging
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# --- APP CONFIG ---
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
CORS(app)

# --- IMPORT UTILITIES ---
try:
    from scraper.email_crawler import crawl_site
    from scraper.fetcher import HTMLFetcher
    # Ensure cloudscraper is used inside your fetcher.py if needed
except ImportError as e:
    logging.error(f"Module Import Error: {e}")

# --- CLEAN ROUTES ---
@app.route("/")
def home():
    return render_template("UI.html")

@app.route("/metadata")
def metadata_page():
    return render_template("metadata.html")

@app.route("/extractor")
def extractor_page():
    return render_template("pagecontent.html")

# --- API ENDPOINTS ---
@app.route("/api/crawl", methods=["POST"])
def api_crawl():
    try:
        data = request.get_json() or {}
        url = data.get("url")
        max_pages = int(data.get("max_pages", 1))
        results = crawl_site(start_url=url, max_pages=min(max_pages, 20))
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/download", methods=["POST"])
def api_download():
    try:
        data = request.get_json() or {}
        results = data.get("results", [])
        df = pd.DataFrame(results)
        
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding="utf-8-sig")
        buffer.seek(0)
        return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name="leads.csv")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)