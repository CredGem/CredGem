export interface CreditType {
  id: string;
  updated_at: string;
  created_at: string;
  name: string;
  description: string;
}

export interface CreateCreditTypePayload {
  name: string;
  description: string;
}

export interface UpdateCreditTypePayload {
  name?: string;
  description?: string;
} 