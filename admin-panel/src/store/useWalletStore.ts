import { create } from 'zustand';
import { Wallet, CreateWalletPayload, WalletsQueryParams, WalletDetails, TransactionType, WalletDepositRequest, WalletDebitRequest, WalletAdjustRequest } from '../types/wallet';
import { CreditType, CreateCreditTypePayload, UpdateCreditTypePayload } from '../types/creditType';
import { walletApi } from '../api/walletApi';
import { creditTypeApi } from '../api/creditTypeApi';

interface WalletStore {
  wallets: Wallet[];
  isLoading: boolean;
  error: string | null;
  selectedWallet: WalletDetails | null;
  creditTypes: CreditType[];
  totalWallets: number;
  currentPage: number;
  pageSize: number;
  fetchWallets: (params?: WalletsQueryParams) => Promise<void>;
  fetchWallet: (id: string) => Promise<void>;
  fetchCreditTypes: () => Promise<void>;
  createWallet: (payload: CreateWalletPayload) => Promise<WalletDetails>;
  updateWalletStatus: (id: string, status: Wallet['status']) => Promise<void>;
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
  updateCreditType: (id: string, payload: UpdateCreditTypePayload) => Promise<void>;
  deleteCreditType: (id: string) => Promise<void>;
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

  createWallet: async (payload: CreateWalletPayload) => {
    set({ isLoading: true, error: null });
    const { name, context } = payload;
    try {
      const newWallet = await walletApi.createWallet(name, context);
      set((state) => ({
        wallets: [...state.wallets, newWallet],
        totalWallets: state.totalWallets + 1,
        isLoading: false
      }));
      return newWallet;
    } catch (error) {
      set({ error: 'Failed to create wallet', isLoading: false });
    }
  },

  updateWalletStatus: async (id: string, status: Wallet['status']) => {
    set({ isLoading: true, error: null });
    try {
      const updatedWallet = await walletApi.updateWalletStatus(id, status);
      set((state) => ({
        wallets: state.wallets.map((wallet) =>
          wallet.id === id ? updatedWallet : wallet
        ),
        isLoading: false
      }));
    } catch (error) {
      set({ error: 'Failed to update wallet status', isLoading: false });
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
    }
  },

  updateCreditType: async (id: string, payload: UpdateCreditTypePayload) => {
    set({ isLoading: true, error: null });
    const { name, description } = payload;
    try {
      const updatedCreditType = await creditTypeApi.updateCreditType(id, name, description);
      set((state) => ({
        creditTypes: state.creditTypes.map((ct) =>
          ct.id === id ? updatedCreditType : ct
        ),
        isLoading: false
      }));
    } catch (error) {
      set({ error: 'Failed to update credit type', isLoading: false });
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
})); 