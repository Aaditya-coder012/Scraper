import requests
from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class HTMLFetcher:
    def __init__(self, use_proxy=False):
        try:
            self.ua = UserAgent()
        except:
            self.ua = None

    def fetch(self, url):
        user_agent = self.ua.random if self.ua else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        headers = {"User-Agent": user_agent}

        # Step 1: Fast Request
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200 and len(response.text) > 500:
                return response.text
        except Exception:
            pass

        # Step 2: Playwright Fallback (for JS sites)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
                context = browser.new_context(user_agent=user_agent)
                page = context.new_page()
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            print(f"Fetch failed: {e}")
            return None