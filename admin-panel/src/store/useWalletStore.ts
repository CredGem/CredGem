import { create } from 'zustand';
import { Wallet, CreateWalletPayload, WalletsQueryParams, WalletDetails, TransactionType, WalletDepositRequest, WalletDebitRequest, WalletAdjustRequest } from '../types/wallet';
import { CreditType, CreateCreditTypePayload } from '../types/creditType';
import { walletApi } from '../api/walletApi';
import { creditTypeApi } from '../api/creditTypeApi';
import { toast } from '@/hooks/use-toast';
import { Product, ProductSubscription } from '../types/product';

type SubscriptionType = "ONE_TIME" | "RECURRING";
type SubscriptionMode = "ADD" | "RESET";

interface SubscribeToProductRequest {
  product_id: string;
  mode: SubscriptionMode;
  type: SubscriptionType;
}

interface WalletStore {
  wallets: (Wallet | WalletDetails)[];
  isLoading: boolean;
  error: string | null;
  selectedWallet: WalletDetails | null;
  creditTypes: CreditType[];
  totalWallets: number;
  currentPage: number;
  pageSize: number;
  subscriptions: ProductSubscription[];
  totalCount: number;
  fetchWallets: (params?: WalletsQueryParams) => Promise<void>;
  fetchWallet: (id: string) => Promise<void>;
  fetchCreditTypes: () => Promise<void>;
  fetchSubscriptions: (walletId: string, params: { page: number; page_size: number }) => Promise<void>;
  createWallet: (payload: CreateWalletPayload) => Promise<WalletDetails>;
  updateWallet: (id: string, name: string, context: Record<string, string>) => Promise<void>;
  clearSelectedWallet: () => void;
  getCreditTypeName: (id: string) => string;
  processCredits: (
    type: TransactionType,
    walletId: string, 
    creditTypeId: string, 
    amount: number, 
    description: string,
    issuer: string,
    context?: Record<string, string>,
    resetSpent?: boolean
  ) => Promise<void>;
  createCreditType: (payload: CreateCreditTypePayload) => Promise<CreditType>;
  updateCreditType: (id: string, data: { name: string; description: string }) => Promise<void>;
  deleteCreditType: (id: string) => Promise<void>;
  setPage: (currentPage: number) => void;
  subscribeToProduct: (walletId: string, data: SubscribeToProductRequest) => Promise<void>;
}

export const useWalletStore = create<WalletStore>((set, get) => ({
  wallets: [],
  isLoading: false,
  error: null,
  selectedWallet: null,
  creditTypes: [],
  totalWallets: 0,
  currentPage: 1,
  pageSize: 10,
  subscriptions: [],
  totalCount: 0,
  setPage: (currentPage: number) => set({ currentPage }),

  fetchWallets: async (params?: WalletsQueryParams) => {
    set({ isLoading: true, error: null });
    try {
      const response = await walletApi.getWallets(params);
      set({ 
        wallets: response.data,
        totalWallets: response.total_count,
        currentPage: response.page,
        pageSize: response.page_size,
        isLoading: false 
      });
    } catch (error) {
      set({ error: 'Failed to fetch wallets', isLoading: false });
    }
  },

  fetchWallet: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const wallet = await walletApi.getWallet(id);
      set({ selectedWallet: wallet, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch wallet', isLoading: false });
    }
  },

  fetchCreditTypes: async () => {
    try {
      const creditTypes = await creditTypeApi.getCreditTypes();
      set({ creditTypes });
    } catch (error) {
      set({ error: 'Failed to fetch credit types' });
    }
  },

  fetchSubscriptions: async (walletId: string, params: { page: number; page_size: number }) => {
    try {
      const response = await walletApi.getSubscriptions(walletId, params);
      set({
        subscriptions: response.data,
        totalCount: response.total_count,
        currentPage: params.page,
        pageSize: params.page_size,
        error: null
      });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch subscriptions' });
    }
  },

  createWallet: async (payload: CreateWalletPayload) => {
    set({ isLoading: true, error: null });
    const { name, context = {} } = payload;
    try {
      const newWallet = await walletApi.createWallet(name, context);
      set((state) => ({
        wallets: [newWallet, ...state.wallets],
        totalWallets: state.totalWallets + 1,
        isLoading: false
      }));
      return newWallet;
    } catch (error) {
      set({ error: 'Failed to create wallet', isLoading: false });
      throw error;
    }
  },

  updateWallet: async (id: string, name: string, context: Record<string, string>) => {
    set({ isLoading: true, error: null });
    try {
      const updatedWallet = await walletApi.updateWallet(id, name, context);
      set((state) => ({
        wallets: state.wallets.map((wallet) =>
          wallet.id === id ? updatedWallet : wallet
        ),
        isLoading: false
      }));
    } catch (error) {
      set({ error: 'Failed to update wallet', isLoading: false });
    }
  },

  clearSelectedWallet: () => {
    set({ selectedWallet: null });
  },

  getCreditTypeName: (id: string) => {
    const creditType = get().creditTypes.find(ct => ct.id === id);
    return creditType?.name || id;
  },

  processCredits: async (
    type: TransactionType,
    walletId: string, 
    creditTypeId: string, 
    amount: number, 
    description: string,
    issuer: string,
    context?: Record<string, string>,
    resetSpent?: boolean
  ) => {
    set({ isLoading: true, error: null });
    try {
      switch (type) { 
        case 'deposit':
          const dataWalletDeposit: WalletDepositRequest = {
            credit_type_id: creditTypeId,
            description: description,
            idempotency_key: issuer,
            type: type,
            context: context || {},
            issuer: issuer,
            payload: {
              type: type,
              amount: amount,
            },
          };
          await walletApi.deposit(walletId, dataWalletDeposit);
          break;
        case 'debit':
          const dataWalletDebit: WalletDebitRequest = {
            credit_type_id: creditTypeId,
            description: description,
            idempotency_key: issuer,
            type: type,
            context: context || {},
            issuer: issuer,
            payload: {
              type: type,
              amount: amount,
            },
          };
          await walletApi.debit(walletId, dataWalletDebit);
          break;
        case 'adjust':
          const dataWalletAdjust: WalletAdjustRequest = {
            credit_type_id: creditTypeId,
            description: description,
            idempotency_key: issuer,
            type: type,
            context: context || {},
            issuer: issuer,
            payload: {
              type: type,
              amount: amount,
              reset_spent: resetSpent ? true : false,
            },
          };
          await walletApi.adjust(walletId, dataWalletAdjust);
          break;
      }
      // Refresh wallet details after transaction
      const wallet = await walletApi.getWallet(walletId);
      set({ selectedWallet: wallet, isLoading: false });
    } catch (error) {
      set({ error: `Failed to ${type} credits`, isLoading: false });
    }
  },

  createCreditType: async (payload: CreateCreditTypePayload) => {
    set({ isLoading: true, error: null });
    const { name, description } = payload;
    try {
      const newCreditType = await creditTypeApi.createCreditType(name, description);
      set((state) => ({
        creditTypes: [...state.creditTypes, newCreditType],
        isLoading: false
      }));
      return newCreditType;
    } catch (error) {
      set({ error: 'Failed to create credit type', isLoading: false });
      throw error;
    }
  },

  updateCreditType: async (id: string, data: { name: string; description: string }) => {
    try {
      // Create optimistic update
      const prevCreditTypes = get().creditTypes;
      const updatedCreditTypes = prevCreditTypes.map(type => 
        type.id === id ? { ...type, ...data, updated_at: new Date().toISOString() } : type
      );
      
      // Apply optimistic update
      set({ creditTypes: updatedCreditTypes });

      // Make API call
      const updatedCreditType = await creditTypeApi.updateCreditType(id, data.name, data.description);
      
      // Update with server response (in case server modified something)
      set({
        creditTypes: prevCreditTypes.map(type => 
          type.id === id ? updatedCreditType : type
        )
      });

      toast({
        title: "Credit type updated",
        description: "Successfully updated credit type",
      });
    } catch (error) {
      // Revert to previous state on error
      const prevCreditTypes = get().creditTypes;
      set({ creditTypes: prevCreditTypes });
      
      toast({
        title: "Error updating credit type",
        description: error instanceof Error ? error.message : "Failed to update credit type",
        variant: "destructive",
      });
      throw error;
    }
  },

  deleteCreditType: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await creditTypeApi.deleteCreditType(id);
      set((state) => ({
        creditTypes: state.creditTypes.filter((ct) => ct.id !== id),
        isLoading: false
      }));
    } catch (error) {
      set({ error: 'Failed to delete credit type', isLoading: false });
    }
  },

  subscribeToProduct: async (walletId: string, data: SubscribeToProductRequest) => {
    try {
      await walletApi.subscribeToProduct(walletId, data);
      // Refresh subscriptions
      const response = await walletApi.getSubscriptions(walletId, { page: 1, page_size: 100 });
      set({ subscriptions: response.data });
      toast({
        title: "Subscription added",
        description: "Successfully subscribed to product",
      });
    } catch (error) {
      set({ error: 'Failed to subscribe to product' });
      toast({
        title: "Error adding subscription",
        description: error instanceof Error ? error.message : "Failed to subscribe to product",
        variant: "destructive",
      });
      throw error;
    }
  }
})); 