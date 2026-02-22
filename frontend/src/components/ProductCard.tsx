import { useNavigate } from "react-router-dom";
import { Card, Tag, Popconfirm, message } from "antd";
import { DeleteOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import type { Product } from "../types";
import { deleteProduct } from "../api/client";

interface Props {
  product: Product;
  onDelete: () => void;
}

export default function ProductCard({ product, onDelete }: Props) {
  const navigate = useNavigate();

  const discount =
    product.original_price &&
    product.current_price &&
    product.original_price > product.current_price
      ? ((product.original_price - product.current_price) /
          product.original_price) *
        100
      : null;

  const handleDelete = async (e?: React.MouseEvent) => {
    e?.stopPropagation();
    await deleteProduct(product.id);
    message.success("Product deleted");
    onDelete();
  };

  return (
    <Card
      hoverable
      onClick={() => navigate(`/product/${product.id}`)}
      cover={
        product.image_url ? (
          <img
            alt={product.title}
            src={product.image_url}
            style={{ height: 180, objectFit: "contain", padding: 8 }}
          />
        ) : (
          <div
            style={{
              height: 180,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "#f5f5f5",
              color: "#999",
            }}
          >
            No Image
          </div>
        )
      }
      actions={[
        <Popconfirm
          key="delete"
          title="Delete this product?"
          onConfirm={(e) => handleDelete(e as any)}
          onCancel={(e) => e?.stopPropagation()}
        >
          <DeleteOutlined
            onClick={(e) => e.stopPropagation()}
            style={{ color: "#ff4d4f" }}
          />
        </Popconfirm>,
      ]}
    >
      <Card.Meta
        title={
          <span style={{ fontSize: 13 }}>
            {product.title.length > 60
              ? product.title.slice(0, 60) + "..."
              : product.title}
          </span>
        }
        description={
          <div>
            <Tag color="blue" style={{ marginBottom: 4 }}>
              {product.retailer}
            </Tag>
            <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
              <span
                style={{ fontSize: 18, fontWeight: "bold", color: "#52c41a" }}
              >
                {product.current_price != null
                  ? `$${product.current_price.toFixed(2)}`
                  : "N/A"}
              </span>
              {discount != null && (
                <Tag color="red">{discount.toFixed(0)}% off</Tag>
              )}
            </div>
            {product.last_checked && (
              <div style={{ fontSize: 11, color: "#999", marginTop: 4 }}>
                Updated {dayjs(product.last_checked).fromNow()}
              </div>
            )}
          </div>
        }
      />
    </Card>
  );
}
