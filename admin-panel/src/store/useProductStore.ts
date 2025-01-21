import { create } from 'zustand';
import { Product, CreateProductRequest, UpdateProductRequest } from '../types/product';
import { productApi } from '../api/productApi';

interface ProductStore {
  products: Product[];
  isLoading: boolean;
  error: string | null;
  selectedProduct: Product | null;
  totalProducts: number;
  currentPage: number;
  pageSize: number;
  fetchProducts: (params?: { page?: number; page_size?: number }) => Promise<void>;
  fetchProduct: (id: string) => Promise<void>;
  createProduct: (payload: CreateProductRequest) => Promise<Product>;
  updateProduct: (id: string, payload: UpdateProductRequest) => Promise<void>;
  clearSelectedProduct: () => void;
}

export const useProductStore = create<ProductStore>((set) => ({
  products: [],
  isLoading: false,
  error: null,
  selectedProduct: null,
  totalProducts: 0,
  currentPage: 1,
  pageSize: 10,

  fetchProducts: async (params?: { page?: number; page_size?: number }) => {
    set({ isLoading: true, error: null });
    try {
      const response = await productApi.getProducts(params);
      set({ 
        products: response.data,
        totalProducts: response.total_count,
        currentPage: response.page,
        pageSize: response.page_size,
        isLoading: false 
      });
    } catch (error) {
      set({ error: 'Failed to fetch products', isLoading: false });
    }
  },

  fetchProduct: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const product = await productApi.getProduct(id);
      set({ selectedProduct: product, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch product', isLoading: false });
    }
  },

  createProduct: async (payload: CreateProductRequest) => {
    set({ isLoading: true, error: null });
    try {
      const newProduct = await productApi.createProduct(payload);
      set((state) => ({
        products: [...state.products, newProduct],
        totalProducts: state.totalProducts + 1,
        isLoading: false
      }));
      return newProduct;
    } catch (error) {
      set({ error: 'Failed to create product', isLoading: false });
      throw error;
    }
  },

  updateProduct: async (id: string, payload: UpdateProductRequest) => {
    set({ isLoading: true, error: null });
    try {
      const updatedProduct = await productApi.updateProduct(id, payload);
      set((state) => ({
        products: state.products.map((product) =>
          product.id === id ? updatedProduct : product
        ),
        isLoading: false
      }));
    } catch (error) {
      set({ error: 'Failed to update product', isLoading: false });
      throw error;
    }
  },

  clearSelectedProduct: () => {
    set({ selectedProduct: null });
  },
})); 