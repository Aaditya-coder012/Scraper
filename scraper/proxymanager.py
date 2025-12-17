# scraper/proxymanager.py
import random

class ProxyManager:
    def __init__(self):
        # Add at least one working proxy if needed
        self.proxies = [
            # Example: "http://username:password@ip:port" or "http://ip:port"
            # "http://123.123.123.123:8080",
        ]

    def get_proxy(self):
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {"http": proxy, "https": proxy}
