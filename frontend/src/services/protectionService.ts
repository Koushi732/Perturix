import { apiClient } from './apiClient';

export interface AttackResponse {
  success: boolean;
  data: {
    id: string;
    session_id: string;
    attack_name: string;
    attack_version: string;
    epsilon: number | null;
    execution_time_ms: number | null;
    device: string;
    success: boolean;
    parameters: Record<string, any> | null;
    verification_data: Record<string, any> | null;
  }
}

export const protectionService = {
  protect: async (sessionId: string, algorithm: string, parameters: Record<string, any>): Promise<AttackResponse> => {
    return apiClient.request<AttackResponse>('/attacks/execute', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        attack_name: algorithm,
        parameters: {
          ...parameters,
          save_research_artifacts: true
        }
      })
    });
  }
};
