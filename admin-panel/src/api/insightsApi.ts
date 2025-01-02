import { axiosInstance } from "./axiosInstance";

export interface TimeSeriesPoint {
  timestamp: string;
  credit_type_id: string;
  credit_type_name: string;
  transaction_count: number;
  debits_amount: number;
}

export interface CreditUsageResponse {
  credit_type_id: string;
  credit_type_name: string;
  transaction_count: number;
  debits_amount: number;
}

export interface CreditUsageTimeSeriesResponse {
  start_date: string;
  end_date: string;
  granularity: "day" | "week" | "month";
  points: TimeSeriesPoint[];
}

export interface WalletActivityPoint {
  timestamp: string;
  wallet_id: string;
  wallet_name: string;
  total_transactions: number;
  total_deposits: number;
  total_debits: number;
  total_holds: number;
  total_releases: number;
  total_adjustments: number;
}

export interface WalletActivityResponse {
  start_date: string;
  end_date: string;
  granularity: "day" | "week" | "month";
  points: WalletActivityPoint[];
}

export interface TrendingWallet {
  wallet_id: string;
  transaction_count: number;
  wallet_name: string;
}

export const insightsApi = {
  getCreditUsage: async (startDate: string, endDate: string) => {
    const response = await axiosInstance.get<CreditUsageResponse[]>("/insights/credits/usage-summary", {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    });
    return response.data;
  },

  getCreditUsageTimeSeries: async (startDate: string, endDate: string, granularity: "day" | "week" | "month" = "day") => {
    const response = await axiosInstance.get<CreditUsageTimeSeriesResponse>("/insights/credits/usage-timeseries", {
      params: {
        start_date: startDate,
        end_date: endDate,
        granularity,
      },
    });
    return response.data;
  },

  getWalletActivity: async (startDate: string, endDate: string, granularity: "day" | "week" | "month" = "day", context?: Record<string, string>) => {
    const response = await axiosInstance.get<WalletActivityResponse>("/insights/wallets/activity", {
      params: {
        start_date: startDate,
        end_date: endDate,
        granularity,
        context: context ? Object.entries(context).map(([key, value]) => `${key}=${value}`).join(",") : undefined,
      },
    });
    return response.data;
  },

  getTrendingWallets: async (startDate: string, endDate: string, limit: number = 5) => {
    const response = await axiosInstance.get<TrendingWallet[]>("/insights/wallets/trending", {
      params: {
        start_date: startDate,
        end_date: endDate,
        limit,
      },
    });
    return response.data;
  },
}; 