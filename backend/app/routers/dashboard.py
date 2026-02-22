from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, Notification, PriceHistory, Product
from app.schemas import DashboardSummary
from app.services.scraper_service import check_all_prices

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    total_products = db.query(Product).count()
    active_alerts = db.query(Alert).filter(Alert.is_active == True).count()

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    notifications_today = (
        db.query(Notification)
        .filter(Notification.sent_at >= today_start)
        .count()
    )

    # Count products where price dropped in last 24h
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent_history = (
        db.query(PriceHistory)
        .filter(PriceHistory.checked_at >= yesterday)
        .all()
    )
    product_prices: dict[int, list[float]] = {}
    for h in recent_history:
        product_prices.setdefault(h.product_id, []).append(h.price)

    price_drops = sum(
        1 for prices in product_prices.values() if len(prices) >= 2 and prices[-1] < prices[0]
    )

    return DashboardSummary(
        total_products=total_products,
        active_alerts=active_alerts,
        notifications_today=notifications_today,
        price_drops_today=price_drops,
    )


@router.post("/check-prices")
def manual_check(db: Session = Depends(get_db)):
    results = check_all_prices(db)
    return results
