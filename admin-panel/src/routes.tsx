import { Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { Wallets } from "./pages/Wallets";
import { WalletDetails } from "./pages/WalletDetails";
import { Transactions } from "./pages/Transactions";
import { CreditSettings } from "./pages/CreditSettings";

export function AppRoutes() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/wallets" element={<Wallets />} />
        <Route path="/wallets/:id" element={<WalletDetails />} />
        <Route path="/transactions" element={<Transactions />} />
        <Route path="/credit-settings" element={<CreditSettings />} />
      </Routes>
    </Layout>
  );
} 