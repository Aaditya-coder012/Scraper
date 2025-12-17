🚀 Growth Swift | SEO & Contact Intelligence Engine
Growth Swift is a powerful, dual-purpose web intelligence tool designed for SEO professionals and lead generation specialists. It combines deep-site metadata analysis with a sophisticated multi-page contact extractor, wrapped in a modern, minimalist glassmorphism interface.

----------------------------------------------------------------------------------------------------

🌟 Key Features
1. SEO & Metadata Intelligence
Recursive Meta Extraction: Captures Titles, Descriptions, Canonical URLs, and Open Graph (OG) tags.

Semantic Analysis: Extracts H1, H2, and H3 headings to understand page structure.

WHOIS Lookup: Integrated domain ownership and registration data extraction.

Keyword Contextualizer: Scans site content for specific keywords and provides the surrounding text "context" for SEO analysis.

2. Contact & Lead Extractor
Deep Crawling: Multi-page BFS (Breadth-First Search) crawling within the same domain.

Smart Name Parsing: Automatically derives First and Last names from email strings using regex patterns.

Designation Discovery: Uses JSON-LD schema parsing and DOM proximity logic to find job titles (e.g., "Professor", "Director") associated with found emails.

Export Ready: One-click CSV generation for lead lists.

3. Advanced Fetching Logic
Hybrid Engine: Automatically switches between Requests (fast) and Playwright (headless browser) if a site requires JavaScript rendering.

Anti-Detection: Built-in proxy rotation and random User-Agent headers.

----------------------------------------------------------------------------------------------------

🏗️ Project Architecture
The system is built with a modular approach for high maintainability:

Plaintext

growth_swift/
├── scraper/                # Core Logic Modules
│   ├── email_crawler.py    # BFS crawling & contact aggregation
│   ├── fetcher.py          # Hybrid Requests/Playwright engine
│   ├── metadata_extractor.py # SEO & OG tag parsing
│   ├── whois_lookup.py     # Domain registration info
│   ├── proxymanager.py     # Proxy rotation logic
│   ├── parser.py           # BeautifulSoup wrapper
│   └── utils.py            # Regex & URL normalization helpers
├── templates/              # Flask Frontend
│   ├── UI.html             # Master Control Panel
│   ├── metadata.html       # SEO Intelligence Interface
│   └── pagecontent.html    # Contact Extractor Interface
├── app.py                  # Flask Backend API & Routing
└── requirements.txt        # Dependency List

----------------------------------------------------------------------------------------------------

🛠️ Tech Stack & Libraries
Backend
Flask: The core web framework handling API routing.

BeautifulSoup4 & Lxml: Used for high-speed HTML parsing and DOM traversal.

Playwright: Handles heavy JavaScript-rendered websites that standard scrapers miss.

Pandas: Manages data structuring and CSV generation.

Requests: Handles standard HTTP communications.

Python-Whois: Interfaces with WHOIS servers for domain data.

Frontend
Tailwind CSS: For the professional, responsive "Glassmorphism" UI.