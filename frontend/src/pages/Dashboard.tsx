import { useEffect, useState } from "react";
import {
  Row,
  Col,
  Card,
  Statistic,
  Button,
  message,
  Spin,
  Empty,
} from "antd";
import {
  ShoppingOutlined,
  BellOutlined,
  MailOutlined,
  FallOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { getDashboardSummary, getProducts, checkPrices } from "../api/client";
import type { DashboardSummary, Product } from "../types";
import ProductCard from "../components/ProductCard";

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [s, p] = await Promise.all([getDashboardSummary(), getProducts()]);
      setSummary(s);
      setProducts(p);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCheckPrices = async () => {
    setChecking(true);
    try {
      const result = await checkPrices();
      message.success(
        `Checked ${result.checked} products, ${result.alerts_triggered} alerts triggered`
      );
      load();
    } catch {
      message.error("Failed to check prices");
    } finally {
      setChecking(false);
    }
  };

  if (loading) return <Spin size="large" style={{ display: "block", marginTop: 100 }} />;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>Dashboard</h2>
        <Button
          type="primary"
          icon={<ReloadOutlined />}
          loading={checking}
          onClick={handleCheckPrices}
        >
          Check All Prices
        </Button>
      </div>

      {summary && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="Tracked Products"
                value={summary.total_products}
                prefix={<ShoppingOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Active Alerts"
                value={summary.active_alerts}
                prefix={<BellOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Notifications Today"
                value={summary.notifications_today}
                prefix={<MailOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Price Drops (24h)"
                value={summary.price_drops_today}
                prefix={<FallOutlined />}
                valueStyle={{ color: summary.price_drops_today > 0 ? "#52c41a" : undefined }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {products.length === 0 ? (
        <Empty description="No products tracked yet" />
      ) : (
        <Row gutter={[16, 16]}>
          {products.map((p) => (
            <Col key={p.id} xs={24} sm={12} lg={8} xl={6}>
              <ProductCard product={p} onDelete={load} />
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}
