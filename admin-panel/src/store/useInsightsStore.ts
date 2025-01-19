import { create } from "zustand";
import { insightsApi, CreditUsageResponse, CreditUsageTimeSeriesResponse, WalletActivityResponse, TrendingWallet } from "../api/insightsApi";

interface InsightsState {
  creditUsage: CreditUsageResponse[] | null;
  creditUsageTimeSeries: CreditUsageTimeSeriesResponse | null;
  walletActivity: WalletActivityResponse | null;
  trendingWallets: TrendingWallet[] | null;
  isLoading: boolean;
  isLoadingFetchCreditUsage: boolean;
  isLoadingFetchCreditUsageTimeSeries: boolean;
  isLoadingFetchWalletActivity: boolean;
  isLoadingFetchTrendingWallets: boolean;
  error: string | null;

  // Actions
  fetchCreditUsage: (startDate: string, endDate: string) => Promise<void>;
  fetchCreditUsageTimeSeries: (startDate: string, endDate: string, granularity?: "day" | "week" | "month") => Promise<void>;
  fetchWalletActivity: (startDate: string, endDate: string, granularity?: "day" | "week" | "month", context?: Record<string, string>) => Promise<void>;
  fetchTrendingWallets: (startDate: string, endDate: string, limit?: number) => Promise<void>;
}

export const useInsightsStore = create<InsightsState>((set) => ({
  creditUsage: null,
  creditUsageTimeSeries: null,
  walletActivity: null,
  trendingWallets: null,
  isLoading: false,
  isLoadingFetchCreditUsage: false,
  isLoadingFetchCreditUsageTimeSeries: false,
  isLoadingFetchWalletActivity: false,
  isLoadingFetchTrendingWallets: false,
  error: null,

  fetchCreditUsage: async (startDate: string, endDate: string) => {
    try {
      set({ isLoading: true, error: null });
      const data = await insightsApi.getCreditUsage(startDate, endDate);
      set({ creditUsage: data, isLoading: false });
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
    }
  },

  fetchCreditUsageTimeSeries: async (startDate: string, endDate: string, granularity = "day") => {
    try {
      set({ isLoading: true, error: null });
      const data = await insightsApi.getCreditUsageTimeSeries(startDate, endDate, granularity);
      set({ creditUsageTimeSeries: data, isLoading: false });
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
    }
  },

  fetchWalletActivity: async (startDate: string, endDate: string, granularity = "day", context?) => {
    try {
      set({ isLoading: true, error: null });
      const data = await insightsApi.getWalletActivity(startDate, endDate, granularity, context);
      set({ walletActivity: data, isLoading: false });
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
    }
  },

  fetchTrendingWallets: async (startDate: string, endDate: string, limit = 5) => {
    try {
      set({ isLoading: true, error: null });
      const data = await insightsApi.getTrendingWallets(startDate, endDate, limit);
      set({ trendingWallets: data, isLoading: false });
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
    }
  },
})); 