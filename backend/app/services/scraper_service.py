import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Product
from app.services.alert_service import evaluate_alerts
from app.services.product_service import refresh_product

logger = logging.getLogger(__name__)


def check_all_prices(db: Session | None = None) -> dict:
    own_session = db is None
    if own_session:
        db = SessionLocal()

    try:
        products = db.query(Product).filter(Product.is_active == True).all()
        results = {"checked": 0, "updated": 0, "alerts_triggered": 0, "errors": 0}

        for product in products:
            try:
                old_price = product.current_price
                refresh_product(db, product)
                results["checked"] += 1

                if product.current_price != old_price:
                    results["updated"] += 1

                notifications = evaluate_alerts(db, product)
                results["alerts_triggered"] += len(notifications)
            except Exception as e:
                logger.error(f"Error checking product {product.id}: {e}")
                results["errors"] += 1

        return results
    finally:
        if own_session:
            db.close()
