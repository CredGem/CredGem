export type WalletStatus = "active" | "inactive";
export type TransactionType = "deposit" | "debit" | "adjust";

export interface WalletContextPair {
  key: string;
  value: string;
}

export interface WalletBalance {
  credit_type_id: string;
  credit_type_name: string;
  total_credits: number;
  spent_credits: number;
  available_credits: number;
}

export interface WalletDetails {
  id: string;
  updated_at: string;
  created_at: string;
  name: string;
  context: Record<string, string>;
  balances: WalletBalance[];
}

export interface Wallet {
  id: string;
  name: string;
  status: WalletStatus;
  lastActivity: string;
  context?: Record<string, string>;
}

export interface CreateWalletPayload {
  name: string;
  context?: Record<string, string>;
}

export interface PaginatedResponse<T> {
  data: T[];
  total_count: number;
  page: number;
  page_size: number;
}

export interface WalletsQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
}

export interface TransactionPayload {
  type: TransactionType;
  amount: number;
  reset_spent?: boolean;
}

export interface TransactionRequest {
  type: TransactionType;
  credit_type_id: string;
  description: string;
  idempotency_key: string;
  payload: TransactionPayload;
  issuer: string;
  context: Record<string, string>;
}

export interface AdjustRequest {
  type: "adjust";
  credit_type_id: string;
  description: string;
  idempotency_key: string;
  payload: {
    type: "adjust";
    amount: number;
    reset_spent: boolean;
  };
  issuer: string;
  context: Record<string, string>;
}

export interface Transaction {
  id: string;
  updated_at: string;
  created_at: string;
  type: "deposit" | "debit" | "adjust";
  credit_type_id: string;
  description: string;
  context: Record<string, string>;
  idempotency_key: string;
  payload: {
    type: "deposit" | "debit" | "adjust";
    amount: number;
    reset_spent?: boolean;
  };
}

export interface TransactionsQueryParams {
  credit_type_id?: string;
  wallet_id?: string;
  context?: string;
  page?: string;
  page_size?: string;
  start_date?: string;
  end_date?: string;
  search?: string;
}

export interface BaseTransactionRequest {
  type: "deposit" | "debit" | "adjust";
  credit_type_id: string;
  description: string;
  idempotency_key: string;
  issuer: string;
  context: Record<string, string>;
}

export interface WalletDepositRequest extends BaseTransactionRequest {
  type: "deposit";
  payload: {
    type: "deposit";
    amount: number;
  };
}

export interface WalletDebitRequest extends BaseTransactionRequest {
  type: "debit";
  payload: {
    type: "debit";
    amount: number;
  };
}

export interface WalletAdjustRequest extends BaseTransactionRequest {
  type: "adjust";
  payload: {
    type: "adjust";
    amount: number;
    reset_spent: boolean;
  };
} 