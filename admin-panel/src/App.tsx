import { BrowserRouter } from "react-router-dom";
import { AppRoutes } from "./routes";
import { ToastProvider } from "./components/ToastProvider";

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider />
      <AppRoutes />
    </BrowserRouter>
  );
} 