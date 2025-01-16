import { BrowserRouter } from "react-router-dom";
import { AppRoutes } from "./routes";
import { ToastProvider } from "./components/ToastProvider";
import SidebarSc from "./components/sidebar";
import { ThemeProvider } from "./components/theme-provider";

export default function App() {
  return (
    <BrowserRouter>
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <ToastProvider />
        <SidebarSc>
          <AppRoutes />
        </SidebarSc>
      </ThemeProvider>
    </BrowserRouter>
  );
} 