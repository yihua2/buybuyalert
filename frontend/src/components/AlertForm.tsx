import { useState } from "react";
import { Form, Select, InputNumber, Button, message } from "antd";
import { createAlert } from "../api/client";

interface Props {
  productId: number;
  onCreated: () => void;
}

export default function AlertForm({ productId, onCreated }: Props) {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleSubmit = async (values: {
    alert_type: string;
    threshold: number;
  }) => {
    setLoading(true);
    try {
      await createAlert(productId, values);
      message.success("Alert created");
      form.resetFields();
      onCreated();
    } catch {
      message.error("Failed to create alert");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form form={form} layout="vertical" onFinish={handleSubmit}>
      <Form.Item
        name="alert_type"
        label="Alert Type"
        rules={[{ required: true }]}
      >
        <Select
          placeholder="Select type"
          options={[
            { value: "price_below", label: "Price drops below" },
            { value: "discount_pct", label: "Discount percentage reaches" },
          ]}
        />
      </Form.Item>
      <Form.Item
        name="threshold"
        label="Threshold"
        rules={[{ required: true }]}
      >
        <InputNumber
          style={{ width: "100%" }}
          min={0}
          step={1}
          placeholder="e.g. 50.00 or 20"
        />
      </Form.Item>
      <Button type="primary" htmlType="submit" block loading={loading}>
        Create Alert
      </Button>
    </Form>
  );
}
