# utils.py
import re
from bs4 import BeautifulSoup

# ---------- Email extraction ----------
def extract_emails(text):
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return set(re.findall(email_regex, text))

# ---------- Name extraction ----------
def extract_names_from_email(email):
    try:
        local_part = email.split("@")[0]
        parts = re.split(r'[._-]', local_part)
        first = parts[0].capitalize() if len(parts) > 0 else ""
        last = parts[1].capitalize() if len(parts) > 1 else ""
        return first, last
    except:
        return "", ""

# ---------- URL helpers ----------
from urllib.parse import urljoin, urlparse

def normalize_url(base, link):
    if not link:
        return None
    return urljoin(base, link)

def is_same_domain(base, link):
    return urlparse(base).netloc == urlparse(link).netloc

# ---------- Smart designation extraction ----------
COMMON_DESIGNATIONS = [
    "Professor", "Assistant Professor", "Associate Professor",
    "Lecturer", "Graduate Student", "Researcher",
    "Director", "Coordinator", "Instructor", "Manager",
    "Postdoc", "Staff", "Fellow", "Teaching Assistant"
]

def extract_designation_near_email(soup, email_tag):
    """
    Looks for designation near an email tag in DOM.
    """
    if not email_tag:
        return ""
    
    # Check parent element
    parent_text = email_tag.parent.get_text(separator=" ", strip=True)
    for d in COMMON_DESIGNATIONS:
        if d.lower() in parent_text.lower():
            return d

    # Check siblings (next 2 elements)
    sibling_texts = []
    for sib in list(email_tag.parent.next_siblings)[:2]:
        if hasattr(sib, "get_text"):
            sibling_texts.append(sib.get_text(separator=" ", strip=True))
        elif isinstance(sib, str):
            sibling_texts.append(sib.strip())
    
    combined_text = " ".join(sibling_texts)
    for d in COMMON_DESIGNATIONS:
        if d.lower() in combined_text.lower():
            return d

    # Fallback: check previous sibling
    prev_texts = []
    for sib in list(email_tag.parent.previous_siblings)[-2:]:
        if hasattr(sib, "get_text"):
            prev_texts.append(sib.get_text(separator=" ", strip=True))
        elif isinstance(sib, str):
            prev_texts.append(sib.strip())
    combined_prev = " ".join(prev_texts)
    for d in COMMON_DESIGNATIONS:
        if d.lower() in combined_prev.lower():
            return d

    return ""
