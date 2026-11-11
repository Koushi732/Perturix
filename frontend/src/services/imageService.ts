import { apiClient } from './apiClient';

export interface UploadResponse {
  success: boolean;
  message: string;
  data: {
    id: string; // The backend ProcessingSession UUID
    original_image_name: string;
    original_image_hash: string;
    image_width: number;
    image_height: number;
    image_format: string;
    status: string;
  }
}

export const imageService = {
  uploadImage: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('image', file);
    
    return apiClient.request<UploadResponse>('/images/upload', {
      method: 'POST',
      body: formData,
    });
  },
  
  getImageUrl: (filename: string) => `http://localhost:8000/api/v1/images/${filename}`
};
