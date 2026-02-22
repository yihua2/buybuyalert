import json
import logging
import random
import re
import time
from dataclasses import dataclass

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
]


@dataclass
class ScrapedProduct:
    title: str
    current_price: float | None
    original_price: float | None
    image_url: str | None


STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
window.chrome = {runtime: {}};
"""


def fetch_page(url: str, wait_seconds: float = 3.0) -> str:
    """Fetch a page using Chromium via Playwright with stealth anti-detection.

    Uses headless=False with --headless=new flag to bypass bot detection on
    sites like Nordstrom, Amazon, etc. that fingerprint the old headless mode.
    """
    time.sleep(random.uniform(1, 3))
    ua = random.choice(USER_AGENTS)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--headless=new",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            user_agent=ua,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            java_script_enabled=True,
        )
        context.add_init_script(STEALTH_JS)

        page = context.new_page()

        # Block heavy media for speed (but keep CSS/JS)
        page.route(
            "**/*.{png,jpg,jpeg,gif,webp,svg,mp4,webm,woff,woff2}",
            lambda route: route.abort(),
        )

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(int(wait_seconds * 1000))
            html = page.content()
        finally:
            browser.close()

    return html


def parse_price(text: str) -> float | None:
    """Extract a numeric price from text like '$49.99' or '49.99'."""
    if not text:
        return None
    cleaned = text.replace(",", "").replace("\xa0", "")
    match = re.search(r"\d+\.?\d*", cleaned)
    if match:
        val = float(match.group())
        if val > 0:
            return val
    return None


def extract_jsonld_product(soup: BeautifulSoup) -> dict | None:
    """Extract Product JSON-LD data from the page.

    Handles Product, ProductGroup (returns first variant or the group itself),
    and @graph arrays.
    """
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            item_type = item.get("@type", "")

            # Direct Product
            if item_type == "Product":
                return item

            # ProductGroup — use first variant if it has offers, else the group
            if item_type == "ProductGroup":
                variants = item.get("hasVariant", [])
                if isinstance(variants, list) and variants:
                    first = variants[0]
                    if isinstance(first, dict) and first.get("offers"):
                        # Merge group-level name/image into variant
                        merged = {**item, **first}
                        merged.pop("hasVariant", None)
                        return merged
                return item

            # Nested in @graph
            for graph_item in item.get("@graph", []):
                if isinstance(graph_item, dict) and graph_item.get("@type") == "Product":
                    return graph_item
    return None


def price_from_jsonld(data: dict) -> tuple[float | None, float | None]:
    """Extract (current_price, original_price) from JSON-LD Product data."""
    offers = data.get("offers", {})
    if isinstance(offers, list):
        offers = offers[0] if offers else {}

    current = parse_price(str(offers.get("price", "")))
    if current is None:
        current = parse_price(str(offers.get("lowPrice", "")))

    # Some sites put original price in offers
    original = current
    high = parse_price(str(offers.get("highPrice", "")))
    if high and current and high > current:
        original = high

    return current, original


def extract_og_meta(soup: BeautifulSoup) -> dict:
    """Extract Open Graph and product meta tags."""
    meta = {}
    for tag in soup.find_all("meta"):
        prop = tag.get("property", "") or tag.get("name", "")
        content = tag.get("content", "")
        if prop and content:
            meta[prop] = content
    return meta


def generic_scrape(url: str, html: str | None = None) -> ScrapedProduct:
    """
    Generic scraper that works on any site by trying:
    1. JSON-LD structured data
    2. Open Graph / meta tags
    3. Common price CSS selectors
    """
    if html is None:
        html = fetch_page(url)

    soup = BeautifulSoup(html, "lxml")

    title = ""
    current_price = None
    original_price = None
    image_url = None

    # 1. Try JSON-LD
    jsonld = extract_jsonld_product(soup)
    if jsonld:
        title = jsonld.get("name", "")
        current_price, original_price = price_from_jsonld(jsonld)
        img = jsonld.get("image")
        if isinstance(img, list):
            image_url = img[0] if img else None
        elif isinstance(img, str):
            image_url = img

    # 2. Try meta tags
    meta = extract_og_meta(soup)
    if not title:
        title = meta.get("og:title", "") or meta.get("twitter:title", "")
    if current_price is None:
        current_price = parse_price(
            meta.get("product:price:amount", "")
            or meta.get("og:price:amount", "")
        )
    if not image_url:
        image_url = meta.get("og:image", "") or meta.get("twitter:image", "")

    # 3. Try <title> tag
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

    # 4. Try common price selectors if still no price
    if current_price is None:
        price_selectors = [
            "[data-test='product-price']",
            "[data-testid='product-price']",
            "[itemprop='price']",
            ".product-price",
            ".price-sales",
            ".price--current",
            ".current-price",
            ".sale-price",
            ".pdp-price",
            ".price__current",
            ".priceView-customer-price span",
        ]
        for sel in price_selectors:
            el = soup.select_one(sel)
            if el:
                p = parse_price(el.get_text())
                if p:
                    current_price = p
                    break

    # 4b. Broad scan: any element whose class contains 'price'
    if current_price is None:
        for el in soup.find_all(attrs={"class": re.compile(r"\bprice\b", re.I)}):
            text = el.get_text(strip=True)
            if "$" in text:
                p = parse_price(text)
                if p:
                    current_price = p
                    break

    # 5. Try to find original/compare-at price
    if current_price is not None and original_price is None:
        orig_selectors = [
            ".price--original",
            ".price-standard",
            ".was-price",
            ".compare-at-price",
            ".original-price",
            ".price__was",
            "s",  # strikethrough text often wraps original price
        ]
        for sel in orig_selectors:
            el = soup.select_one(sel)
            if el:
                p = parse_price(el.get_text())
                if p and p > current_price:
                    original_price = p
                    break

    if original_price is None:
        original_price = current_price

    return ScrapedProduct(
        title=title or "Unknown Product",
        current_price=current_price,
        original_price=original_price,
        image_url=image_url or None,
    )
