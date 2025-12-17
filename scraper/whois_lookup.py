import whois
from urllib.parse import urlparse
from datetime import datetime

class WhoisLookup:
    def lookup(self, url):
        # Ensure url has a scheme for urlparse to work
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        domain = urlparse(url).netloc.replace("www.", "")
        try:
            w = whois.whois(domain)
            
            def fmt_date(d):
                if isinstance(d, list) and d: d = d[0]
                return d.strftime("%Y-%m-%d") if isinstance(d, datetime) else str(d)

            return {
                "domain": domain,
                "registrar": getattr(w, 'registrar', ""),
                "creation_date": fmt_date(getattr(w, 'creation_date', "")),
                "expiration_date": fmt_date(getattr(w, 'expiration_date', "")),
                "country": getattr(w, 'country', ""),
            }
        except Exception as e:
            return {"domain": domain, "error": str(e)}