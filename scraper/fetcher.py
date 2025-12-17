import cloudscraper
import logging
from fake_useragent import UserAgent

class HTMLFetcher:
    def __init__(self, use_proxy=False):
        # cloudscraper bypasses Cloudflare/bot-protections automatically
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

    def fetch(self, url):
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        headers = {"User-Agent": user_agent}

        try:
            logging.info(f"Fetching: {url}")
            response = self.scraper.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                return response.text
            else:
                logging.warning(f"Status {response.status_code} for {url}")
                return None
        except Exception as e:
            logging.error(f"Scraper error: {e}")
            return None