import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Alert, Notification, Product
from app.services.email_service import send_alert_email

logger = logging.getLogger(__name__)

COOLDOWN_HOURS = 24


def evaluate_alerts(db: Session, product: Product) -> list[Notification]:
    if product.current_price is None:
        return []

    alerts = (
        db.query(Alert)
        .filter(Alert.product_id == product.id, Alert.is_active == True)
        .all()
    )

    notifications = []
    now = datetime.utcnow()

    for alert in alerts:
        # Check cooldown
        if alert.last_triggered and (now - alert.last_triggered) < timedelta(
            hours=COOLDOWN_HOURS
        ):
            continue

        triggered = False
        message = ""

        if alert.alert_type == "price_below":
            if product.current_price <= alert.threshold:
                triggered = True
                message = (
                    f"{product.title} is now ${product.current_price:.2f} "
                    f"(below your threshold of ${alert.threshold:.2f})"
                )

        elif alert.alert_type == "discount_pct":
            if product.original_price and product.original_price > 0:
                discount = (
                    (product.original_price - product.current_price)
                    / product.original_price
                    * 100
                )
                if discount >= alert.threshold:
                    triggered = True
                    message = (
                        f"{product.title} is now {discount:.1f}% off "
                        f"(${product.current_price:.2f} from ${product.original_price:.2f})"
                    )

        if triggered:
            # Send email
            send_alert_email(
                product_title=product.title,
                product_url=product.url,
                current_price=product.current_price,
                original_price=product.original_price,
                alert_type=alert.alert_type,
                threshold=alert.threshold,
            )

            # Record notification
            notification = Notification(
                alert_id=alert.id,
                product_id=product.id,
                message=message,
            )
            db.add(notification)

            alert.last_triggered = now
            notifications.append(notification)

    if notifications:
        db.commit()

    return notifications
