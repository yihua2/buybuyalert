import axios from "axios";
import type {
  Product,
  PriceHistory,
  Alert,
  Notification,
  DashboardSummary,
} from "../types";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

// Products
export const getProducts = () =>
  api.get<Product[]>("/products").then((r) => r.data);

export const getProduct = (id: number) =>
  api.get<Product>(`/products/${id}`).then((r) => r.data);

export const addProduct = (url: string) =>
  api.post<Product>("/products", { url }).then((r) => r.data);

export const deleteProduct = (id: number) =>
  api.delete(`/products/${id}`);

export const refreshProduct = (id: number) =>
  api.post<Product>(`/products/${id}/refresh`).then((r) => r.data);

export const getPriceHistory = (id: number) =>
  api.get<PriceHistory[]>(`/products/${id}/price-history`).then((r) => r.data);

// Alerts
export const getProductAlerts = (productId: number) =>
  api.get<Alert[]>(`/products/${productId}/alerts`).then((r) => r.data);

export const createAlert = (
  productId: number,
  data: { alert_type: string; threshold: number }
) =>
  api.post<Alert>(`/products/${productId}/alerts`, data).then((r) => r.data);

export const getAllAlerts = () =>
  api.get<Alert[]>("/alerts").then((r) => r.data);

export const updateAlert = (
  id: number,
  data: { alert_type?: string; threshold?: number; is_active?: boolean }
) => api.put<Alert>(`/alerts/${id}`, data).then((r) => r.data);

export const deleteAlert = (id: number) =>
  api.delete(`/alerts/${id}`);

// Notifications
export const getNotifications = (limit = 50) =>
  api.get<Notification[]>("/notifications", { params: { limit } }).then((r) => r.data);

// Dashboard
export const getDashboardSummary = () =>
  api.get<DashboardSummary>("/dashboard/summary").then((r) => r.data);

// Manual check
export const checkPrices = () =>
  api.post("/check-prices").then((r) => r.data);
