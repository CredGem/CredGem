import { axiosInstance } from "./axiosInstance";
import { WalletDetails, WalletDepositRequest, WalletDebitRequest, WalletAdjustRequest, WalletsQueryParams, PaginatedResponse, Wallet } from "../types/wallet";
import { API_URL } from "@/lib/constants";
import { Product } from "../types/product";
import axios from "axios";
import { ProductSubscription } from "@/types/product";

type SubscriptionType = "ONE_TIME" | "RECURRING";
type SubscriptionMode = "ADD" | "RESET";

interface SubscribeToProductRequest {
  product_id: string;
  mode: SubscriptionMode;
  type: SubscriptionType;
}

export const walletApi = {
  getWallets: async (params?: WalletsQueryParams) => {
    const response = await axiosInstance.get<PaginatedResponse<Wallet>>("/wallets", {
      params,
    });
    return response.data;
  },

  getWallet: async (id: string) => {
    const response = await axiosInstance.get<WalletDetails>(`/wallets/${id}`);
    return response.data;
  },

  createWallet: async (name: string, context: Record<string, string>) => {
    const response = await axiosInstance.post<WalletDetails>("/wallets", {
      name,
      context,
    });
    return response.data;
  },

  updateWallet: async (id: string, name: string, context: Record<string, string>) => {
    const response = await axiosInstance.put<WalletDetails>(`/wallets/${id}`, {
      name,
      context,
    });
    return response.data;
  },
  
  deleteWallet: async (id: string) => {
    await axiosInstance.delete(`/wallets/${id}`);
  },

  deposit: async (walletId: string, data: WalletDepositRequest) => {
    const response = await axiosInstance.post<WalletDetails>(
      `/wallets/${walletId}/deposit`,
      data
    );
    return response.data;
  },

  debit: async (walletId: string, data: WalletDebitRequest) => {
    const response = await axiosInstance.post<WalletDetails>(
      `/wallets/${walletId}/debit`,
      data
    );
    return response.data;
  },

  adjust: async (walletId: string, data: WalletAdjustRequest) => {
    const response = await axiosInstance.post<WalletDetails>(
      `/wallets/${walletId}/adjust`,
      data
    );
    return response.data;
  },

  getSubscriptions: async (walletId: string, params: { page: number; page_size: number }) => {
    const response = await axios.get<PaginatedResponse<ProductSubscription>>(
      `${API_URL}/wallets/${walletId}/subscriptions`,
      { params }
    );
    return response.data;
  },

  getProducts: async () => {
    const response = await axiosInstance.get<Product[]>("/products");
    return response.data;
  },

  subscribeToProduct: async (walletId: string, data: SubscribeToProductRequest) => {
    const response = await axiosInstance.post<void>(`/wallets/${walletId}/subscriptions`, data);
    return response.data;
  },
}; 