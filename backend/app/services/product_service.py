import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import PriceHistory, Product
from app.scrapers.registry import get_retailer, scrape_url

logger = logging.getLogger(__name__)


def add_product(db: Session, url: str) -> Product:
    existing = db.query(Product).filter(Product.url == url).first()
    if existing:
        return existing

    retailer = get_retailer(url)

    product = Product(
        url=url,
        retailer=retailer,
        title="Loading...",
        is_active=True,
    )

    try:
        scraped = scrape_url(url)
        product.title = scraped.title or "Unknown Product"
        product.current_price = scraped.current_price
        product.original_price = scraped.original_price
        product.image_url = scraped.image_url
        product.last_checked = datetime.utcnow()
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        product.title = "Failed to scrape - will retry"

    db.add(product)
    db.commit()
    db.refresh(product)

    # Record initial price history
    if product.current_price is not None:
        history = PriceHistory(
            product_id=product.id,
            price=product.current_price,
            original_price=product.original_price,
        )
        db.add(history)
        db.commit()

    return product


def refresh_product(db: Session, product: Product) -> Product:
    try:
        scraped = scrape_url(product.url)
        if scraped.current_price is not None:
            product.current_price = scraped.current_price
            product.original_price = scraped.original_price or product.original_price
            product.last_checked = datetime.utcnow()

            if scraped.title and scraped.title != product.title:
                product.title = scraped.title
            if scraped.image_url:
                product.image_url = scraped.image_url

            history = PriceHistory(
                product_id=product.id,
                price=scraped.current_price,
                original_price=scraped.original_price,
            )
            db.add(history)
            db.commit()
            db.refresh(product)
        else:
            logger.warning(f"No price found for product {product.id} ({product.url})")
    except Exception as e:
        logger.error(f"Failed to refresh product {product.id}: {e}")

    return product
