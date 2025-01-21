import { axiosInstance } from "./axiosInstance";
import { CreateProductRequest, UpdateProductRequest, ProductResponse, PaginatedProductResponse } from "../types/product";

export const productApi = {
  getProducts: async (params?: { page?: number; page_size?: number }) => {
    const response = await axiosInstance.get<PaginatedProductResponse>("/products", {
      params,
    });
    return response.data;
  },

  getProduct: async (id: string) => {
    const response = await axiosInstance.get<ProductResponse>(`/products/${id}`);
    return response.data;
  },

  createProduct: async (data: CreateProductRequest) => {
    const response = await axiosInstance.post<ProductResponse>("/products", data);
    return response.data;
  },

  updateProduct: async (id: string, data: UpdateProductRequest) => {
    const response = await axiosInstance.put<ProductResponse>(`/products/${id}`, data);
    return response.data;
  }
}; 