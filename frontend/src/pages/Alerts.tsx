import { useEffect, useState } from "react";
import { Card, Spin, Tabs } from "antd";
import { getAllAlerts, getNotifications } from "../api/client";
import type { Alert, Notification } from "../types";
import AlertList from "../components/AlertList";
import NotificationList from "../components/NotificationList";

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [a, n] = await Promise.all([getAllAlerts(), getNotifications()]);
      setAlerts(a);
      setNotifications(n);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) return <Spin size="large" style={{ display: "block", marginTop: 100 }} />;

  return (
    <div>
      <h2>Alerts & Notifications</h2>
      <Tabs
        items={[
          {
            key: "alerts",
            label: `Active Alerts (${alerts.filter((a) => a.is_active).length})`,
            children: (
              <Card>
                <AlertList alerts={alerts} showProduct onUpdate={load} />
              </Card>
            ),
          },
          {
            key: "notifications",
            label: `Notifications (${notifications.length})`,
            children: (
              <Card>
                <NotificationList notifications={notifications} />
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
}
