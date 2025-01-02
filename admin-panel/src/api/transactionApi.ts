import { axiosInstance } from "./axiosInstance";
import { Transaction } from "../types/wallet";

export interface TransactionQueryParams {
  credit_type_id?: string;
  wallet_id?: string;
  context?: string;
}

export const transactionApi = {
  getTransactions: async (params?: TransactionQueryParams) => {
    const response = await axiosInstance.get<Transaction[]>("/transactions", {
      params,
    });
    return response.data;
  },

  getTransaction: async (id: string) => {
    const response = await axiosInstance.get<Transaction>(`/transactions/${id}`);
    return response.data;
  },
}; 