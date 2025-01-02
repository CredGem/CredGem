import { Link } from "react-router-dom";
import { HomeIcon, WalletIcon, TransactionsIcon, CreditTypeIcon } from "./Icons";
import { ReactNode } from "react";
import { useLocation } from "react-router-dom";

export function Sidebar() {
  const location = useLocation();

  return (
    <div className="w-64 bg-content1 h-screen shadow-lg">
      <div className="p-6">
        <h1 className="text-2xl font-bold">
          <span className="text-primary">CredGem</span>
        </h1>
      </div>
      <nav className="mt-6 flex flex-col gap-1">
        <SidebarItem 
          icon={<HomeIcon />} 
          text="Home" 
          to="/"
          active={location.pathname === '/'} 
        />
        <SidebarItem 
          icon={<WalletIcon />} 
          text="Wallets" 
          to="/wallets"
          active={location.pathname === '/wallets'} 
        />
        <SidebarItem 
          icon={<TransactionsIcon />} 
          text="Transactions" 
          to="/transactions"
          active={location.pathname === '/transactions'} 
        />
        <SidebarItem 
          icon={<CreditTypeIcon />} 
          text="Credit Types" 
          to="/credit-settings"
          active={location.pathname === '/credit-settings'} 
        />
      </nav>
    </div>
  );
}

interface SidebarItemProps {
  icon: ReactNode;
  text: string;
  to: string;
  active?: boolean;
}

function SidebarItem({ icon, text, to, active }: SidebarItemProps) {
  return (
    <Link
      to={to}
      className={`flex items-center px-6 py-3 text-foreground transition-colors relative ${
        active 
          ? "bg-primary/10 text-primary before:absolute before:left-0 before:top-0 before:h-full before:w-1 before:bg-primary"
          : "hover:bg-content2"
      }`}
    >
      <span className={`mr-3 ${active ? "text-primary" : ""}`}>{icon}</span>
      <span className={active ? "font-medium" : ""}>{text}</span>
    </Link>
  );
} 