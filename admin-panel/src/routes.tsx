import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import Wallets from "./pages/wallets/wallets";
import Transactions from "./pages/transactions/transactions";
import WalletDetails from "./pages/wallet-details/wallet-details";
import ProductDetails from "./pages/product-details/product-details";
import Dashboard from "./pages/dashboard";
import Products from "./pages/products/products";
import Playground from "./pages/playground/playground";
import Credits from "./pages/credits/credits";




export function AppRoutes() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/wallets" element={<Wallets />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetails />} />
        <Route path="/wallets/:id" element={<WalletDetails />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/credits" element={<Credits />} />
        <Route path="/playground" element={<Playground />} />
      </Routes>
    </Layout>
  );
} 