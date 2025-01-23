export interface BaseResponse {
    id: string;
    created_at: string;
    updated_at: string;
}

export interface PaginatedResponse<T> {
    data: T[];
    page: number;
    page_size: number;
    total_count: number;
} 