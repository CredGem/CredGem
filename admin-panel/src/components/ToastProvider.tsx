import { Toaster } from "sonner";

export const ToastProvider = () => {
  return (
    <Toaster
      position="top-right"
      theme="dark"
      richColors
      style={{
        background: "#2D3748",
        border: "1px solid #4A5568",
        color: "white",
      }}
      className="toast-dark"
    />
  );
}; 