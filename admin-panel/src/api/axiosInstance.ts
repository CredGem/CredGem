import axios from "axios";
import { toast } from "sonner";

export const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Network error or server not available
    if (!error.response) {
      toast.error("Unable to connect to server. Please check your connection and try again.");
      return Promise.reject(error);
    }

    // Server errors (500, etc)
    if (error.response.status >= 500) {
      toast.error("An unexpected error occurred. Please try again later.");
      return Promise.reject(error);
    }

    // Client errors (400, etc)
    if (error.response.status >= 400 && error.response.status < 500) {
      const errorMessage = error.response.data?.detail || "Bad request";
      toast.error(errorMessage);
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
); 