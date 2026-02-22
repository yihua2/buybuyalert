import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Card,
  Button,
  Descriptions,
  Spin,
  message,
  Popconfirm,
  Tag,
  Space,
  Row,
  Col,
} from "antd";
import {
  ReloadOutlined,
  DeleteOutlined,
  LinkOutlined,
} from "@ant-design/icons";
import dayjs from "dayjs";
import {
  getProduct,
  refreshProduct,
  deleteProduct,
  getPriceHistory,
  getProductAlerts,
} from "../api/client";
import type { Product, PriceHistory, Alert } from "../types";
import PriceHistoryChart from "../components/PriceHistoryChart";
import AlertForm from "../components/AlertForm";
import AlertList from "../components/AlertList";

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [history, setHistory] = useState<PriceHistory[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const productId = Number(id);

  const load = async () => {
    setLoading(true);
    try {
      const [p, h, a] = await Promise.all([
        getProduct(productId),
        getPriceHistory(productId),
        getProductAlerts(productId),
      ]);
      setProduct(p);
      setHistory(h);
      setAlerts(a);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [productId]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const p = await refreshProduct(productId);
      setProduct(p);
      const h = await getPriceHistory(productId);
      setHistory(h);
      message.success("Price refreshed");
    } catch {
      message.error("Failed to refresh");
    } finally {
      setRefreshing(false);
    }
  };

  const handleDelete = async () => {
    await deleteProduct(productId);
    message.success("Product deleted");
    navigate("/");
  };

  if (loading || !product) {
    return <Spin size="large" style={{ display: "block", marginTop: 100 }} />;
  }

  const discount =
    product.original_price && product.current_price && product.original_price > product.current_price
      ? ((product.original_price - product.current_price) / product.original_price) * 100
      : null;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>{product.title}</h2>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            loading={refreshing}
            onClick={handleRefresh}
          >
            Refresh Price
          </Button>
          <Popconfirm title="Delete this product?" onConfirm={handleDelete}>
            <Button danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      </div>

      <Row gutter={24}>
        <Col xs={24} lg={16}>
          <Card title="Price Details" style={{ marginBottom: 16 }}>
            <Descriptions column={2}>
              <Descriptions.Item label="Retailer">
                <Tag color="blue">{product.retailer}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Current Price">
                <span style={{ fontSize: 20, fontWeight: "bold", color: "#52c41a" }}>
                  {product.current_price != null ? `$${product.current_price.toFixed(2)}` : "N/A"}
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="Original Price">
                {product.original_price != null ? (
                  <span style={{ textDecoration: discount ? "line-through" : undefined }}>
                    ${product.original_price.toFixed(2)}
                  </span>
                ) : (
                  "N/A"
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Discount">
                {discount ? (
                  <Tag color="red">{discount.toFixed(1)}% off</Tag>
                ) : (
                  "None"
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Last Checked">
                {product.last_checked
                  ? dayjs(product.last_checked).format("MMM D, YYYY h:mm A")
                  : "Never"}
              </Descriptions.Item>
              <Descriptions.Item label="Link">
                <a href={product.url} target="_blank" rel="noopener noreferrer">
                  <LinkOutlined /> View on {product.retailer}
                </a>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          <Card title="Price History" style={{ marginBottom: 16 }}>
            {history.length > 0 ? (
              <PriceHistoryChart data={history} />
            ) : (
              <p>No price history yet.</p>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="Create Alert" style={{ marginBottom: 16 }}>
            <AlertForm productId={productId} onCreated={load} />
          </Card>

          <Card title="Alerts">
            <AlertList alerts={alerts} onUpdate={load} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
