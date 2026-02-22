export interface Product {
  id: number;
  url: string;
  retailer: string;
  title: string;
  image_url: string | null;
  current_price: number | null;
  original_price: number | null;
  last_checked: string | null;
  is_active: boolean;
  created_at: string;
}

export interface PriceHistory {
  id: number;
  product_id: number;
  price: number;
  original_price: number | null;
  checked_at: string;
}

export interface Alert {
  id: number;
  product_id: number;
  alert_type: "price_below" | "discount_pct";
  threshold: number;
  is_active: boolean;
  last_triggered: string | null;
  created_at: string;
  product?: Product;
}

export interface Notification {
  id: number;
  alert_id: number;
  product_id: number;
  message: string;
  sent_at: string;
  product?: Product;
}

export interface DashboardSummary {
  total_products: number;
  active_alerts: number;
  notifications_today: number;
  price_drops_today: number;
}
