import { apiClient } from './apiClient';

export interface EvaluationResponse {
  success: boolean;
  data: {
    id: string;
    session_id: string;
    psnr: number | null;
    ssim: number | null;
    lpips: number | null;
    l0: number | null;
    l2: number | null;
    linf: number | null;
    confidence_before: number | null;
    confidence_after: number | null;
    confidence_drop: number | null;
    attack_success: boolean | null;
    runtime_ms: number | null;
    memory_usage_mb: number | null;
    extra_metrics: Record<string, any> | null;
  }
}

export const evaluationService = {
  evaluate: async (sessionId: string): Promise<EvaluationResponse> => {
    return apiClient.request<EvaluationResponse>('/evaluation/execute', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId })
    });
  }
};
