from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Alert, Product
from app.schemas import AlertCreate, AlertOut, AlertUpdate

router = APIRouter(tags=["alerts"])


@router.post("/api/products/{product_id}/alerts", response_model=AlertOut)
def create_alert(
    product_id: int, data: AlertCreate, db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if data.alert_type not in ("price_below", "discount_pct"):
        raise HTTPException(status_code=400, detail="Invalid alert type")

    alert = Alert(
        product_id=product_id,
        alert_type=data.alert_type,
        threshold=data.threshold,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/api/products/{product_id}/alerts", response_model=list[AlertOut])
def list_product_alerts(product_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Alert)
        .filter(Alert.product_id == product_id)
        .order_by(Alert.created_at.desc())
        .all()
    )


@router.get("/api/alerts", response_model=list[AlertOut])
def list_all_alerts(db: Session = Depends(get_db)):
    return (
        db.query(Alert)
        .options(joinedload(Alert.product))
        .order_by(Alert.created_at.desc())
        .all()
    )


@router.put("/api/alerts/{alert_id}", response_model=AlertOut)
def update_alert(alert_id: int, data: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if data.alert_type is not None:
        if data.alert_type not in ("price_below", "discount_pct"):
            raise HTTPException(status_code=400, detail="Invalid alert type")
        alert.alert_type = data.alert_type
    if data.threshold is not None:
        alert.threshold = data.threshold
    if data.is_active is not None:
        alert.is_active = data.is_active

    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/api/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"ok": True}
