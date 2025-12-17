from bs4 import BeautifulSoup
from collections import deque
import time
import random
import requests
import logging
import json

from .utils import (
    extract_emails,
    normalize_url,
    is_same_domain,
    extract_names_from_email
)

logging.basicConfig(level=logging.INFO)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

CRAWL_DELAY = (0.8, 1.5)
DESIGNATION_KEYS = ["jobTitle", "role", "position", "title", "designation"]


def fetch_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception:
        return None


def extract_emails_from_soup(soup):
    emails = set()
    emails |= extract_emails(soup.get_text())

    for tag in soup.find_all(True):
        for attr in tag.attrs.values():
            emails |= extract_emails(str(attr))

    return emails


def _extract_from_dict(d):
    results = []
    if not isinstance(d, dict):
        return results

    for k, v in d.items():
        if k in DESIGNATION_KEYS and isinstance(v, str):
            results.append(v.strip())
        elif isinstance(v, dict):
            results.extend(_extract_from_dict(v))
        elif isinstance(v, list):
            for item in v:
                results.extend(_extract_from_dict(item))
    return results


def extract_designations_from_jsonld(soup):
    designations = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                data = [data]
            for entry in data:
                designations.extend(_extract_from_dict(entry))
        except Exception:
            pass
    return list(set(designations))


def get_links(soup, base_url):
    links = set()
    for a in soup.find_all("a", href=True):
        link = normalize_url(base_url, a["href"])
        if link and is_same_domain(base_url, link):
            links.add(link.split("#")[0])
    return links


def crawl_site(start_url, max_pages=10):
    visited = set()
    queue = deque([start_url])
    results = []
    pages_scanned = 0

    while queue and pages_scanned < max_pages:
        url = queue.popleft()
        if url in visited:
            continue

        visited.add(url)
        html = fetch_html(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")
        emails = extract_emails_from_soup(soup)
        designations = extract_designations_from_jsonld(soup)

        for email in emails:
            first, last = extract_names_from_email(email)
            results.append({
                "source_page": url,
                "email": email,
                "first_name": first,
                "last_name": last,
                "designations": ", ".join(designations)
            })

        for link in get_links(soup, url):
            if link not in visited:
                queue.append(link)

        pages_scanned += 1
        time.sleep(random.uniform(*CRAWL_DELAY))

    return results
