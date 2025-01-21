export type ProductStatus = 'ACTIVE' | 'INACTIVE';

export interface ProductSettings {
  id: string;
  created_at: string;
  updated_at: string;
  product_id: string;
  credit_type_id: string;
  credit_amount: number;
}

export interface Product {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  description: string;
  status: ProductStatus;
  settings: ProductSettings[];
}

export interface CreditSettingsRequest {
  credit_type_id: string;
  credit_amount: number;
}

export interface CreateProductRequest {
  name: string;
  description: string;
  settings: CreditSettingsRequest[];
}

export interface UpdateProductRequest {
  name?: string;
  description?: string;
}

export interface PaginatedProductResponse {
  data: Product[];
  total: number;
  page: number;
  page_size: number;
}

export type ProductResponse = Product; 