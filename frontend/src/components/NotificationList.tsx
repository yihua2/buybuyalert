import { List, Empty, Tag } from "antd";
import { Link } from "react-router-dom";
import dayjs from "dayjs";
import type { Notification } from "../types";

interface Props {
  notifications: Notification[];
}

export default function NotificationList({ notifications }: Props) {
  if (notifications.length === 0)
    return <Empty description="No notifications yet" />;

  return (
    <List
      dataSource={notifications}
      renderItem={(n) => (
        <List.Item>
          <List.Item.Meta
            title={
              <span>
                {n.product ? (
                  <Link to={`/product/${n.product_id}`}>
                    {n.product.title.slice(0, 50)}
                  </Link>
                ) : (
                  `Product #${n.product_id}`
                )}
              </span>
            }
            description={
              <div>
                <div>{n.message}</div>
                <Tag style={{ marginTop: 4 }}>
                  {dayjs(n.sent_at).format("MMM D, YYYY h:mm A")}
                </Tag>
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
}
