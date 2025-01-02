import { axiosInstance } from "./axiosInstance";
import { CreditType } from "../types/creditType";

export const creditTypeApi = {
  getCreditTypes: async () => {
    const response = await axiosInstance.get<CreditType[]>("/credit-types");
    return response.data;
  },

  getCreditType: async (id: string) => {
    const response = await axiosInstance.get<CreditType>(`/credit-types/${id}`);
    return response.data;
  },

  createCreditType: async (name: string, description: string) => {
    const response = await axiosInstance.post<CreditType>("/credit-types", {
      name,
      description,
    });
    return response.data;
  },

  updateCreditType: async (id: string, name: string, description: string) => {
    const response = await axiosInstance.put<CreditType>(`/credit-types/${id}`, {
      name,
      description,
    });
    return response.data;
  },

  deleteCreditType: async (id: string) => {
    await axiosInstance.delete(`/credit-types/${id}`);
  },
}; 