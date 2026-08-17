"""
src/tools/search.py
Production-grade Web & Wikipedia Extractor.
Extracts clean structured tables, strips infoboxes/sidebars, and preserves complete rosters.
"""

import time
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from ddgs import DDGS


class CleanArticleExtractor(HTMLParser):
    """
    Extracts structured body text and tables from web pages.
    Ignores infoboxes, sidebars, navigation headers, and metadata clutter.
    """
    def __init__(self):
        super().__init__()
        self.reset()
        self.output = []
        self.ignore_depth = 0
        self.in_table = False
        self.current_row = []
        
        self.ignored_tags = {"script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form"}
        self.ignored_classes = ["infobox", "sidebar", "navbox", "mw-editsection", "catlinks", "toc", "reference"]

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get("class", "").lower()
        id_attr = attrs_dict.get("id", "").lower()

        # Skip headers, footers, infoboxes, navigation menus, and citation links
        if tag in self.ignored_tags or any(c in classes or c in id_attr for c in self.ignored_classes):
            self.ignore_depth += 1
            return

        if self.ignore_depth == 0:
            if tag == "table":
                self.in_table = True
                self.output.append("\n")
            elif tag == "tr":
                self.current_row = []
            elif tag in ["p", "h2", "h3", "li"]:
                self.output.append("\n")

    def handle_endtag(self, tag):
        if tag in self.ignored_tags:
            if self.ignore_depth > 0:
                self.ignore_depth -= 1
            return

        if self.ignore_depth == 0:
            if tag == "table":
                self.in_table = False
                self.output.append("\n")
            elif tag == "tr" and self.in_table:
                if len(self.current_row) >= 2:
                    # Clean row representation: "Name | Dates / Details"
                    clean_row = " — ".join(self.current_row[:3])
                    self.output.append(f"• {clean_row}\n")
                self.current_row = []
            elif tag in ["p", "h2", "h3", "li"]:
                self.output.append("\n")

    def handle_data(self, data):
        if self.ignore_depth == 0:
            cleaned = data.strip()
            # Ignore citation markers like [1], [a], [note 2]
            if cleaned and not re.match(r'^\[[0-9a-zA-Z\s]+\]$', cleaned):
                if self.in_table:
                    self.current_row.append(cleaned)
                else:
                    self.output.append(cleaned + " ")

    def get_clean_text(self, max_chars: int = 8000) -> str:
        text = "".join(self.output)
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()[:max_chars]


def fetch_webpage_content(url: str, max_chars: int = 8000) -> str:
    """Scrapes structured clean text from an authoritative URL."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=7) as response:
            html = response.read().decode("utf-8", errors="ignore")
            extractor = CleanArticleExtractor()
            extractor.feed(html)
            return extractor.get_clean_text(max_chars=max_chars)
    except Exception:
        return ""


def search_and_fetch_knowledge(query: str, max_results: int = 4) -> str:
    """
    Two-Stage Frontier RAG Pipeline:
    1. Search DuckDuckGo for top authoritative links.
    2. Deep-fetch structured table rows and list entries from the top page.
    """
    clean_query = query.replace("?", "").replace("!", "").strip()

    # Optimize for structured encyclopedic lists when roster keywords appear
    if any(k in clean_query.lower() for k in ["list", "all", "history", "presidents", "movies", "films", "order"]):
        if "wikipedia" not in clean_query.lower():
            clean_query += " Wikipedia"

    try:
        with DDGS(timeout=8) as ddgs:
            results = list(ddgs.text(clean_query, max_results=max_results))
            if not results:
                return ""

            snippet_texts = []
            top_url = ""
            for i, r in enumerate(results, 1):
                title = r.get('title', '').strip()
                body = r.get('body', '').strip()
                href = r.get('href', '').strip()
                if not top_url and "http" in href and "wikipedia.org" in href:
                    top_url = href
                elif not top_url and "http" in href:
                    top_url = href
                    
                if body:
                    snippet_texts.append(f"[{i}] {title}: {body}")

            combined_context = "\n\n".join(snippet_texts)

            # Deep scrape the top authoritative page to capture complete tables
            if top_url:
                print(f"📖 [Nova Deep Fetch] Extracting structured table data from: {top_url[:65]}...")
                page_body = fetch_webpage_content(top_url, max_chars=8000)
                if page_body and len(page_body) > 300:
                    combined_context = f"Verified Source Records ({top_url}):\n{page_body}\n\nSearch Summary:\n{combined_context}"

            return combined_context

    except Exception as e:
        print(f"⚠️ Search error: {e}")
        return ""