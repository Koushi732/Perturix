import { useState, useCallback } from 'react';
import { imageService } from '../services/imageService';
import { protectionService, AttackResponse } from '../services/protectionService';
import { evaluationService, EvaluationResponse } from '../services/evaluationService';

export type PipelineState = 
  | 'idle' 
  | 'uploading' 
  | 'protecting' 
  | 'evaluating' 
  | 'saving' 
  | 'completed' 
  | 'error';

export interface PipelineResult {
  sessionId: string;
  originalImageUrl: string;
  protectedImageUrl: string;
  attackData: AttackResponse['data'];
  evaluationData: EvaluationResponse['data'];
  heatmapUrl: string;
  differenceUrl: string;
  overlayUrl: string;
}

export function usePipeline() {
  const [state, setState] = useState<PipelineState>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PipelineResult | null>(null);

  const reset = useCallback(() => {
    setState('idle');
    setProgress(0);
    setError(null);
    setResult(null);
  }, []);

  const generate = useCallback(async (
    file: File, 
    algorithm: string, 
    strength: number
  ) => {
    try {
      reset();
      
      // Step 1: Upload
      setState('uploading');
      setProgress(10);
      const uploadRes = await imageService.uploadImage(file);
      const sessionId = uploadRes.data.id;
      const originalImageName = uploadRes.data.original_image_name;
      
      // We assume original_image_name has the extension. In backend we know it's stored as {session_id}{ext}
      // Or we can just fetch it by the exact name backend provides. Wait, imageService.getImageUrl uses {filename}
      const ext = originalImageName.substring(originalImageName.lastIndexOf('.'));
      const originalUrl = imageService.getImageUrl(`${sessionId}${ext}`);
      
      // Step 2: Protection
      setState('protecting');
      setProgress(40);
      const attackParams = { epsilon: strength };
      const attackRes = await protectionService.protect(sessionId, algorithm, attackParams);
      
      const protectedUrl = imageService.getImageUrl(`${sessionId}_adv.png`);
      const heatmapUrl = imageService.getImageUrl(`${sessionId}_heatmap.png`);
      const differenceUrl = imageService.getImageUrl(`${sessionId}_difference.png`);
      const overlayUrl = imageService.getImageUrl(`${sessionId}_overlay.png`);
      
      // Step 3: Evaluation
      setState('evaluating');
      setProgress(75);
      const evalRes = await evaluationService.evaluate(sessionId);
      
      // Step 4: Finalize
      setState('saving');
      setProgress(95);
      
      // History is already saved by backend automatically in these endpoints!
      // evaluate() triggers history_service.save_evaluation internally.
      
      setResult({
        sessionId,
        originalImageUrl: originalUrl,
        protectedImageUrl: protectedUrl,
        attackData: attackRes.data,
        evaluationData: evalRes.data,
        heatmapUrl,
        differenceUrl,
        overlayUrl,
      });
      
      setState('completed');
      setProgress(100);
      
    } catch (err: any) {
      setError(err.message || 'An unknown error occurred during the pipeline execution.');
      setState('error');
    }
  }, [reset]);

  return {
    state,
    progress,
    error,
    result,
    generate,
    reset,
  };
}
