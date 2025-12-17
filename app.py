import os
import re
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Assuming your scraper.py has these classes
from scraper import HTMLFetcher, HTMLParser, MetadataExtractor, WhoisLookup, crawl_site

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("UI.html")

@app.route("/templates/metadata.html")
def metadata_page():
    return render_template("metadata.html")

@app.route("/templates/pagecontent.html")
def pagecontent_page():
    return render_template("pagecontent.html")

@app.route("/scrape", methods=["POST"])
def scrape_route():
    data = request.get_json() or {}
    url = data.get("url")
    target_keyword = data.get("keyword", "").strip()
    
    try:
        fetcher = HTMLFetcher()
        html = fetcher.fetch(url)
        soup = HTMLParser().parse(html)
        metadata = MetadataExtractor().extract(soup, url)
        
        # KEYWORD FIX: Extracting snippets if keyword is provided
        if target_keyword:
            text = soup.get_text()
            # Find snippets of 50 characters around the keyword
            matches = re.findall(rf'(.{{0,50}}{re.escape(target_keyword)}.{{0,50}})', text, re.IGNORECASE)
            metadata["keyword"] = {
                "term": target_keyword,
                "count": len(matches),
                "context_descriptions": matches[:3] # Return top 3 snippets
            }
        else:
            metadata["keyword"] = None
            
        return jsonify(metadata)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json() or {}
    query = data.get("keyword") # Matches your HTML form ID
    # Add your Serper API logic here...
    return jsonify({"results": []}) 

@app.route("/api/crawl", methods=["POST"])
def api_crawl():
    data = request.get_json() or {}
    results = crawl_site(data.get("url"), max_pages=int(data.get("max_pages", 1)))
    return jsonify({"success": True, "results": results})

if __name__ == '__main__':
    app.run(debug=True)