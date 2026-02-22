import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import { ConfigProvider, Layout, Menu, Typography } from "antd";
import {
  DashboardOutlined,
  PlusCircleOutlined,
  BellOutlined,
} from "@ant-design/icons";
import Dashboard from "./pages/Dashboard";
import AddProduct from "./pages/AddProduct";
import ProductDetail from "./pages/ProductDetail";
import Alerts from "./pages/Alerts";

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

function AppLayout() {
  const location = useLocation();

  const menuItems = [
    {
      key: "/",
      icon: <DashboardOutlined />,
      label: <Link to="/">Dashboard</Link>,
    },
    {
      key: "/add",
      icon: <PlusCircleOutlined />,
      label: <Link to="/add">Add Product</Link>,
    },
    {
      key: "/alerts",
      icon: <BellOutlined />,
      label: <Link to="/alerts">Alerts</Link>,
    },
  ];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider breakpoint="lg" collapsedWidth={0}>
        <div
          style={{
            padding: "16px",
            textAlign: "center",
          }}
        >
          <Title
            level={4}
            style={{ color: "#fff", margin: 0, cursor: "pointer" }}
            onClick={() => (window.location.href = "/")}
          >
            BuyBuyAlert
          </Title>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            borderBottom: "1px solid #f0f0f0",
          }}
        >
          <Title level={4} style={{ margin: "16px 0" }}>
            Price Tracking & Alerts
          </Title>
        </Header>
        <Content style={{ margin: "24px", maxWidth: 1200 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/add" element={<AddProduct />} />
            <Route path="/product/:id" element={<ProductDetail />} />
            <Route path="/alerts" element={<Alerts />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

function App() {
  return (
    <ConfigProvider
      theme={{
        token: { colorPrimary: "#1677ff" },
      }}
    >
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
