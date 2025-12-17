import requests
from fake_useragent import UserAgent
from .proxymanager import ProxyManager
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class HTMLFetcher:
    def __init__(self, use_proxy=False):
        self.proxy_manager = ProxyManager() if use_proxy else None
        try:
            self.ua = UserAgent()
        except:
            self.ua = None

    def fetch(self, url):
        headers = {"User-Agent": self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        proxies = self.proxy_manager.get_proxy() if self.proxy_manager else None

        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            response.raise_for_status()
            html = response.text
            if html.strip():
                return html
        except Exception as e:
            print(f"[INFO] Requests failed, trying Playwright: {e}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_user_agent(headers["User-Agent"])
                page.goto(url, timeout=30000)
                html = page.content()
                browser.close()
                return html
        except PlaywrightTimeoutError:
            print(f"[ERROR] Playwright timed out for {url}")
        except Exception as e:
            print(f"[ERROR] Playwright fetch failed: {e}")

        return None

# --- Standalone Test Block ---
if __name__ == '__main__':
    print("--- Testing HTMLFetcher ---")
    
    # NOTE: You MUST have your ProxyManager class defined in scraper/proxymanager.py 
    #       for use_proxy=True to work. Set to False for simpler testing.
    fetcher = HTMLFetcher(use_proxy=False) 
    
    test_url = "https://www.google.com" # Use a site without heavy JS for a quick requests test
    print(f"1. Attempting fetch for: {test_url}")
    
    html_result = fetcher.fetch(test_url)
    
    if html_result:
        print("Fetch successful! HTML content length:", len(html_result))
        # Optional: Print the title using BeautifulSoup if it's imported in fetcher.py
        # If BeautifulSoup is not in fetcher.py, comment out the following lines
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_result, 'html.parser')
            print("Page Title:", soup.title.text if soup.title else "Title not found")
        except ImportError:
            print("Note: BeautifulSoup not available in this test block.")
    else:
        print("Fetch failed.")