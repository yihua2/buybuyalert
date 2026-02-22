import logging
from typing import Callable
from urllib.parse import urlparse

from app.scrapers.base import ScrapedProduct, generic_scrape, fetch_page
from app.scrapers.amazon import scrape_amazon

logger = logging.getLogger(__name__)

# Domain → specialized scraper function
SCRAPER_MAP: dict[str, Callable[[str], ScrapedProduct]] = {
    "amazon.com": scrape_amazon,
    "www.amazon.com": scrape_amazon,
}

# Known retailer display names
KNOWN_RETAILERS: dict[str, str] = {
    "amazon.com": "Amazon",
    "www.amazon.com": "Amazon",
    "walmart.com": "Walmart",
    "www.walmart.com": "Walmart",
    "target.com": "Target",
    "www.target.com": "Target",
    "bestbuy.com": "Best Buy",
    "www.bestbuy.com": "Best Buy",
    "costco.com": "Costco",
    "www.costco.com": "Costco",
    "nike.com": "Nike",
    "www.nike.com": "Nike",
    "nordstrom.com": "Nordstrom",
    "www.nordstrom.com": "Nordstrom",
    "madewell.com": "Madewell",
    "www.madewell.com": "Madewell",
}


def get_retailer(url: str) -> str:
    """Get display name for a retailer. Falls back to cleaned domain."""
    domain = urlparse(url).hostname or ""
    if domain in KNOWN_RETAILERS:
        return KNOWN_RETAILERS[domain]
    # Auto-generate a display name from the domain
    name = domain.removeprefix("www.").split(".")[0]
    return name.capitalize()


def scrape_url(url: str) -> ScrapedProduct:
    """Scrape any URL — uses specialized scraper if available, else generic."""
    domain = urlparse(url).hostname or ""

    # Try specialized scraper first
    specialized = SCRAPER_MAP.get(domain)
    if specialized:
        logger.info(f"Using specialized scraper for {domain}")
        return specialized(url)

    # Generic: fetch with Playwright, then extract with JSON-LD/meta/CSS
    logger.info(f"Using generic scraper for {domain}")
    html = fetch_page(url, wait_seconds=3.0)
    return generic_scrape(url, html)
