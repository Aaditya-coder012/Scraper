import whois
import logging
from urllib.parse import urlparse

class WhoisLookup:
    def lookup(self, url):
        try:
            # Clean the URL to get just the domain (e.g., example.com)
            domain = urlparse(url).netloc
            if not domain:
                domain = url.split('/')[0]
            
            logging.info(f"Performing WHOIS lookup for: {domain}")
            w = whois.whois(domain)
            
            # Extract dates safely (handling lists or single objects)
            def format_date(d):
                if isinstance(d, list):
                    return str(d[0].date()) if d[0] else "N/A"
                return str(d.date()) if d else "N/A"

            return {
                "registrar": w.registrar if w.registrar else "Private/Unknown",
                "creation_date": format_date(w.creation_date),
                "expiration_date": format_date(w.expiration_date),
                "status": w.status[0] if isinstance(w.status, list) else w.status
            }
        except Exception as e:
            logging.error(f"WHOIS lookup failed for {url}: {e}")
            return "N/A (Lookup Blocked or Private)"