from sqlalchemy.orm import Session, joinedload

from app.models import Notification


def get_recent_notifications(db: Session, limit: int = 50) -> list[Notification]:
    return (
        db.query(Notification)
        .options(joinedload(Notification.product))
        .order_by(Notification.sent_at.desc())
        .limit(limit)
        .all()
    )
