import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Input, Button, message, Typography, Alert } from "antd";
import { LinkOutlined } from "@ant-design/icons";
import { addProduct } from "../api/client";

const { Paragraph } = Typography;

export default function AddProduct() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!url.trim()) {
      message.warning("Please enter a product URL");
      return;
    }

    setLoading(true);
    try {
      const product = await addProduct(url.trim());
      message.success(`Added: ${product.title}`);
      navigate(`/product/${product.id}`);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      message.error(detail || "Failed to add product");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600 }}>
      <h2>Add Product</h2>

      <Card>
        <Paragraph>Paste any product URL to start tracking its price. Works with Amazon, Walmart, Target, Best Buy, Costco, Nike, Nordstrom, Madewell, and most other retailers.</Paragraph>

        <Input
          size="large"
          prefix={<LinkOutlined />}
          placeholder="https://www.nike.com/t/air-max-..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onPressEnter={handleSubmit}
          style={{ marginBottom: 16 }}
        />

        <Button
          type="primary"
          size="large"
          block
          loading={loading}
          onClick={handleSubmit}
        >
          {loading ? "Scraping product..." : "Add & Track Product"}
        </Button>
      </Card>

      <Alert
        style={{ marginTop: 16 }}
        type="info"
        showIcon
        message="Works with any retailer"
        description="Paste a direct product page URL from any online store. The scraper uses a headless browser to extract title, price, and image from the page."
      />
    </div>
  );
}
