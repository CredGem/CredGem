import { axiosInstance } from "./axiosInstance";
import { WalletDetails, WalletBalance, WalletDepositRequest, WalletDebitRequest, WalletAdjustRequest } from "../types/wallet";

export const walletApi = {
  getWallets: async () => {
    const response = await axiosInstance.get<WalletDetails[]>("/wallets");
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
}; 