import logging
import random
import re
import time

import requests
from bs4 import BeautifulSoup

from app.scrapers.base import (
    ScrapedProduct,
    STEALTH_JS,
    USER_AGENTS,
    extract_jsonld_product,
    fetch_page,
    parse_price,
    price_from_jsonld,
)

logger = logging.getLogger(__name__)

# Containers that scope to the main product's price
PRICE_CONTAINERS = [
    "#corePriceDisplay_desktop_feature_div",
    "#corePrice_feature_div",
    "#corePrice_desktop",
    "#apex_offerDisplay_desktop",
    "#price_inside_buybox",
    "#newBuyBoxPrice",
    "#buybox",
    "#desktop_buybox",
]


def _extract_price_from_soup(soup: BeautifulSoup) -> tuple[float | None, float | None]:
    """Try to extract (current_price, original_price) from Amazon HTML."""
    current_price = None
    original_price = None

    # 1. Try scoped to price containers
    for container_sel in PRICE_CONTAINERS:
        container = soup.select_one(container_sel)
        if not container:
            continue
        for price_el in container.select("span.a-offscreen"):
            parent_price = price_el.find_parent("span", class_="a-price")
            if parent_price and parent_price.get("data-a-strike"):
                continue
            p = parse_price(price_el.get_text())
            if p:
                current_price = p
                break
        if current_price is not None:
            for strike_el in container.select(
                "span.a-price[data-a-strike] span.a-offscreen"
            ):
                p = parse_price(strike_el.get_text())
                if p and p > current_price:
                    original_price = p
                    break
            if original_price is None or original_price == current_price:
                basis = container.select_one(".basisPrice span.a-offscreen")
                if basis:
                    p = parse_price(basis.get_text())
                    if p and p > current_price:
                        original_price = p
            break

    # 2. Fallback: look in main product area, avoiding carousels
    if current_price is None:
        main = soup.select_one("#ppd, #dp-container, #centerCol")
        if main:
            for price_el in main.select("span.a-offscreen"):
                parent_price = price_el.find_parent("span", class_="a-price")
                if parent_price and parent_price.get("data-a-strike"):
                    continue
                in_carousel = price_el.find_parent(
                    "div", class_=re.compile(r"carousel|sims-fbt|a-carousel")
                )
                if in_carousel:
                    continue
                p = parse_price(price_el.get_text())
                if p:
                    current_price = p
                    break

    return current_price, original_price


def _requests_fallback(url: str) -> tuple[BeautifulSoup, str]:
    """Fallback using requests with session cookies."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
    })
    # Get cookies from homepage
    session.get("https://www.amazon.com/", timeout=10)
    time.sleep(random.uniform(1, 2))
    resp = session.get(url, timeout=15)
    return BeautifulSoup(resp.text, "lxml"), resp.text


def scrape_amazon(url: str) -> ScrapedProduct:
    title = ""
    current_price = None
    original_price = None
    image_url = None

    # Attempt 1: Playwright (headless browser)
    try:
        html = fetch_page(url, wait_seconds=5.0)
        soup = BeautifulSoup(html, "lxml")

        # JSON-LD
        jsonld = extract_jsonld_product(soup)
        if jsonld:
            title = jsonld.get("name", "")
            current_price, original_price = price_from_jsonld(jsonld)
            img = jsonld.get("image")
            if isinstance(img, list):
                image_url = img[0] if img else None
            elif isinstance(img, str):
                image_url = img

        if not title:
            el = soup.select_one("#productTitle")
            if el:
                title = el.get_text(strip=True)

        if current_price is None:
            current_price, original_price = _extract_price_from_soup(soup)

        if not image_url:
            img_el = soup.select_one("#landingImage, #imgBlkFront, #main-image")
            if img_el:
                image_url = img_el.get("src") or img_el.get("data-old-hires")
    except Exception as e:
        logger.warning(f"Playwright attempt failed for {url}: {e}")

    # Attempt 2: requests fallback if Playwright didn't get price
    if current_price is None:
        try:
            soup2, raw = _requests_fallback(url)

            if not title:
                el = soup2.select_one("#productTitle")
                if el:
                    title = el.get_text(strip=True)

            current_price, original_price = _extract_price_from_soup(soup2)

            if not image_url:
                img_el = soup2.select_one("#landingImage, #imgBlkFront")
                if img_el:
                    image_url = img_el.get("src") or img_el.get("data-old-hires")

            # Last resort: search for priceAmount in embedded JS
            if current_price is None:
                match = re.search(r'"priceAmount"\s*:\s*"?([\d.]+)', raw)
                if match:
                    current_price = float(match.group(1))
        except Exception as e:
            logger.warning(f"Requests fallback failed for {url}: {e}")

    if original_price is None:
        original_price = current_price

    if current_price is None:
        logger.warning(
            f"Amazon: could not extract price from {url}. "
            "Amazon may be blocking automated requests."
        )

    return ScrapedProduct(
        title=title or "Unknown Product",
        current_price=current_price,
        original_price=original_price,
        image_url=image_url,
    )
