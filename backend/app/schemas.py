from datetime import datetime

from pydantic import BaseModel, HttpUrl


# Products
class ProductCreate(BaseModel):
    url: str


class ProductOut(BaseModel):
    id: int
    url: str
    retailer: str
    title: str
    image_url: str | None
    current_price: float | None
    original_price: float | None
    last_checked: datetime | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PriceHistoryOut(BaseModel):
    id: int
    product_id: int
    price: float
    original_price: float | None
    checked_at: datetime

    model_config = {"from_attributes": True}


# Alerts
class AlertCreate(BaseModel):
    alert_type: str  # price_below | discount_pct
    threshold: float


class AlertUpdate(BaseModel):
    alert_type: str | None = None
    threshold: float | None = None
    is_active: bool | None = None


class AlertOut(BaseModel):
    id: int
    product_id: int
    alert_type: str
    threshold: float
    is_active: bool
    last_triggered: datetime | None
    created_at: datetime
    product: ProductOut | None = None

    model_config = {"from_attributes": True}


# Notifications
class NotificationOut(BaseModel):
    id: int
    alert_id: int
    product_id: int
    message: str
    sent_at: datetime
    product: ProductOut | None = None

    model_config = {"from_attributes": True}


# Dashboard
class DashboardSummary(BaseModel):
    total_products: int
    active_alerts: int
    notifications_today: int
    price_drops_today: int
