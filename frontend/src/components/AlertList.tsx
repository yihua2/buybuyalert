import { List, Switch, Tag, Popconfirm, Button, Empty } from "antd";
import { DeleteOutlined } from "@ant-design/icons";
import { Link } from "react-router-dom";
import { updateAlert, deleteAlert } from "../api/client";
import type { Alert } from "../types";

interface Props {
  alerts: Alert[];
  showProduct?: boolean;
  onUpdate: () => void;
}

export default function AlertList({ alerts, showProduct, onUpdate }: Props) {
  if (alerts.length === 0) return <Empty description="No alerts" />;

  const handleToggle = async (alert: Alert) => {
    await updateAlert(alert.id, { is_active: !alert.is_active });
    onUpdate();
  };

  const handleDelete = async (id: number) => {
    await deleteAlert(id);
    onUpdate();
  };

  return (
    <List
      dataSource={alerts}
      renderItem={(alert) => (
        <List.Item
          actions={[
            <Switch
              key="toggle"
              checked={alert.is_active}
              onChange={() => handleToggle(alert)}
              size="small"
            />,
            <Popconfirm
              key="delete"
              title="Delete this alert?"
              onConfirm={() => handleDelete(alert.id)}
            >
              <Button
                type="text"
                danger
                size="small"
                icon={<DeleteOutlined />}
              />
            </Popconfirm>,
          ]}
        >
          <List.Item.Meta
            title={
              <span>
                <Tag color={alert.alert_type === "price_below" ? "green" : "orange"}>
                  {alert.alert_type === "price_below"
                    ? `Below $${alert.threshold.toFixed(2)}`
                    : `${alert.threshold}% off`}
                </Tag>
                {!alert.is_active && <Tag>Paused</Tag>}
              </span>
            }
            description={
              showProduct && alert.product ? (
                <Link to={`/product/${alert.product_id}`}>
                  {alert.product.title.slice(0, 50)}
                </Link>
              ) : null
            }
          />
        </List.Item>
      )}
    />
  );
}
