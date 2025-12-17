# scraper/metadata_extractor.py
from bs4 import BeautifulSoup

class MetadataExtractor:
    def extract(self, soup, url):
        data = {}

        # --- Title ---
        try:
            data["title"] = soup.title.string.strip() if soup.title and soup.title.string else None
        except Exception:
            data["title"] = None

        # --- Meta Description ---
        try:
            desc = soup.find("meta", attrs={"name": "description"})
            data["description"] = desc["content"].strip() if desc and desc.get("content") else None
        except Exception:
            data["description"] = None

        # --- Canonical URL ---
        try:
            canonical = soup.find("link", rel="canonical")
            data["canonical"] = canonical["href"].strip() if canonical and canonical.get("href") else None
        except Exception:
            data["canonical"] = None

        # --- OG Tags ---
        og = {}
        try:
            for tag in soup.find_all("meta"):
                prop = tag.get("property", "")
                if prop.startswith("og:") and tag.get("content"):
                    og[prop] = tag.get("content").strip()
        except Exception:
            pass
        data["og_tags"] = og

        # --- Headings ---
        headings = {"h1": [], "h2": [], "h3": []}
        try:
            for h_tag in headings.keys():
                headings[h_tag] = [h.get_text(strip=True) for h in soup.find_all(h_tag)]
        except Exception:
            pass
        data["headings"] = headings

        # --- Images ---
        images = []
        try:
            for img in soup.find_all("img"):
                src = img.get("src")
                if src:
                    images.append(src.strip())
        except Exception:
            pass
        data["images"] = images

        # --- Source URL ---
        data["source_url"] = url

        return data
