import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <div className="fixed top-0 right-0 left-0 z-40">
        <Header />
      </div>
      <div className="fixed left-0 top-0 h-screen z-50">
        <Sidebar />
      </div>
      <main className="ml-64 pt-16">
        {children}
      </main>
    </div>
  );
} 