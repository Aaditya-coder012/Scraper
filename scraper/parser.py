from bs4 import BeautifulSoup

class HTMLParser:
    def parse(self, html):
        # Using built-in parser for better compatibility
        return BeautifulSoup(html, "html.parser")