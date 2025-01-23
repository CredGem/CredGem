import { create } from 'zustand';
import { Transaction, TransactionsQueryParams } from '../types/wallet';
import { transactionApi } from '../api/transactionApi';

interface TransactionStore {
  transactions: Transaction[];
  isLoading: boolean;
  error: string | null;
  totalTransactions: number;
  currentPage: number;
  pageSize: number;
  fetchTransactions: (params?: TransactionsQueryParams) => Promise<void>;
  setPage: (pageSize: number) => void;
}

export const useTransactionStore = create<TransactionStore>((set) => ({
  transactions: [],
  isLoading: false,
  error: null,
  totalTransactions: 0,
  currentPage: 1,
  pageSize: 10,
  setPage: (currentPage: number) => set({ currentPage }),

  fetchTransactions: async (params?: TransactionsQueryParams) => {
    set({ isLoading: true, error: null });
    try {
      const response = await transactionApi.getTransactions(params);
      set({ 
        transactions: response.data,
        totalTransactions: response.total_count,
        currentPage: response.page,
        pageSize: response.page_size,
        isLoading: false 
      });
    } catch (error) {
      set({ error: 'Failed to fetch transactions', isLoading: false });
    }
  },
})); 