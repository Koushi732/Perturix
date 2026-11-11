import { apiClient } from './apiClient';

export interface HistoryListResponse {
  success: boolean;
  data: {
    items: any[];
    total: number;
    skip: number;
    limit: number;
  }
}

export const historyService = {
  getHistory: async (): Promise<HistoryListResponse> => {
    return apiClient.request<HistoryListResponse>('/history/');
  },
  getSession: async (id: string): Promise<any> => {
    return apiClient.request<any>(`/history/${id}`);
  },
  deleteSession: async (id: string): Promise<any> => {
    return apiClient.request<any>(`/history/${id}`, { method: 'DELETE' });
  }
};
