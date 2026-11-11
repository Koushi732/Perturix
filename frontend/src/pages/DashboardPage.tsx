import React, { useState, useRef } from 'react';
import { PageContainer } from '../components/common/PageContainer';
import { Shield, UploadCloud, Sliders, Play, Download, RefreshCw, AlertCircle, CheckCircle, Image as ImageIcon, Check } from 'lucide-react';
import { usePipeline } from '../hooks/usePipeline';
import { motion, AnimatePresence } from 'framer-motion';
import { MetricCard } from '../components/common/MetricCard';
import { Button } from '../components/common/Button';
import { cn } from '../utils/cn';

export default function DashboardPage() {
  const { state, progress, error, result, generate, reset } = usePipeline();
  
  // Local state for configuration
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [algorithm, setAlgorithm] = useState<string>('fgsm');
  const [strength, setStrength] = useState<number>(0.03);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
      }
    }
  };

  const handleGenerate = () => {
    if (selectedFile) {
      generate(selectedFile, algorithm, strength);
    }
  };

  const handleRunAgain = () => {
    reset();
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  // Helper to get text for loading state
  const getProgressText = () => {
    switch (state) {
      case 'uploading': return 'Uploading image...';
      case 'protecting': return 'Generating Perturbation...';
      case 'evaluating': return 'Evaluating Metrics...';
      case 'saving': return 'Saving Session...';
      default: return 'Processing...';
    }
  };

  return (
    <PageContainer 
      title="Dashboard" 
      description="Protect Images Against AI Manipulation"
    >
      <AnimatePresence mode="wait">
        {state === 'idle' && (
          <motion.div 
            key="idle"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* Left Col: Upload & Settings */}
            <div className="lg:col-span-2 space-y-6">
              {/* Dropzone */}
              <div 
                className={cn(
                  "border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center min-h-[320px] transition-all",
                  previewUrl ? "border-primary-500/50 bg-primary-500/5" : "border-black/10 hover:border-primary-500/30 hover:bg-black/5 bg-white dark:bg-dark-800/50"
                )}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => !previewUrl && fileInputRef.current?.click()}
              >
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  className="hidden" 
                  accept="image/png, image/jpeg, image/webp" 
                  onChange={handleFileChange} 
                />
                
                {previewUrl ? (
                  <div className="relative w-full h-full flex flex-col items-center">
                    <img src={previewUrl} alt="Preview" className="max-h-[300px] object-contain rounded-lg shadow-lg mb-4" />
                    <div className="flex gap-4">
                      <Button variant="secondary" size="sm" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>
                        Change Image
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center cursor-pointer">
                    <UploadCloud className="w-16 h-16 text-slate-400 dark:text-slate-500 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">Drag Image Here or Browse</h3>
                    <p className="text-sm text-slate-300">Accepts PNG, JPEG, WEBP</p>
                  </div>
                )}
              </div>
            </div>

            {/* Right Col: Settings & CTA */}
            <div className="space-y-6">
              <div className="glass-panel p-6">
                <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-6 flex items-center">
                  <Sliders className="w-5 h-5 text-primary-500 mr-2" />
                  Configuration
                </h3>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Algorithm</label>
                    <select 
                      className="w-full glass-input p-3"
                      value={algorithm}
                      onChange={(e) => setAlgorithm(e.target.value)}
                    >
                      <option value="fgsm">FGSM (Fast Gradient Sign Method)</option>
                    </select>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Attack Strength (ε)</label>
                      <span className="text-sm font-mono text-primary-400">{strength.toFixed(3)}</span>
                    </div>
                    <input 
                      type="range" 
                      min="0.005" 
                      max="0.1" 
                      step="0.005" 
                      value={strength} 
                      onChange={(e) => setStrength(parseFloat(e.target.value))}
                      className="w-full accent-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Output Format</label>
                    <select className="w-full glass-input p-3" disabled>
                      <option value="png">PNG (Lossless)</option>
                    </select>
                  </div>
                </div>
              </div>

              <Button 
                className="w-full h-14 text-lg font-medium shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_30px_rgba(59,130,246,0.5)] transition-shadow"
                disabled={!selectedFile}
                onClick={handleGenerate}
              >
                <Shield className="w-5 h-5 mr-2" />
                Generate Protected Image
              </Button>
            </div>
          </motion.div>
        )}

        {(state === 'uploading' || state === 'protecting' || state === 'evaluating' || state === 'saving') && (
          <motion.div 
            key="processing"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center py-20"
          >
            <div className="w-full max-w-md">
              <div className="flex justify-between text-sm mb-4">
                <span className="text-slate-900 dark:text-white font-medium">{getProgressText()}</span>
                <span className="text-primary-400 font-mono">{progress}%</span>
              </div>
              
              <div className="w-full h-3 bg-white dark:bg-dark-800 rounded-full overflow-hidden shadow-inner border border-black/5">
                <motion.div 
                  className="h-full bg-primary-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ ease: "linear", duration: 0.5 }}
                />
              </div>
              
              <div className="mt-12 space-y-4">
                <StepIndicator current={state} target="uploading" label="Uploading Image" />
                <StepIndicator current={state} target="protecting" label="Generating Perturbation" />
                <StepIndicator current={state} target="evaluating" label="Evaluating Results" />
                <StepIndicator current={state} target="saving" label="Completed" />
              </div>
            </div>
          </motion.div>
        )}

        {state === 'error' && (
          <motion.div 
            key="error"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20 text-center"
          >
            <AlertCircle className="w-16 h-16 text-rose-500 mb-6" />
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Processing Failed</h3>
            <p className="text-slate-300 mb-8 max-w-lg">{error}</p>
            <Button onClick={handleRunAgain} variant="secondary">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </motion.div>
        )}

        {state === 'completed' && result && (
          <motion.div 
            key="completed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-medium text-slate-900 dark:text-white flex items-center">
                <CheckCircle className="w-6 h-6 text-emerald-500 mr-2" />
                Protection Applied Successfully
              </h3>
              <div className="flex gap-3">
                <Button variant="secondary" onClick={handleRunAgain}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Run Again
                </Button>
                <Button onClick={() => {
                  const a = document.createElement('a');
                  a.href = result.protectedImageUrl;
                  a.download = "protected_image.png";
                  a.click();
                }}>
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <ImageCard title="Original" url={result.originalImageUrl} />
              <ImageCard title="Protection Layer" url={result.heatmapUrl} icon={<Shield className="w-4 h-4 text-primary-400" />} />
              <ImageCard title="Difference Map" url={result.differenceUrl} />
              <ImageCard title="Overlay" url={result.overlayUrl} />
            </div>

            {/* Protected Image Focus */}
            <div className="glass-panel p-6 mt-6 flex flex-col lg:flex-row items-center gap-8 ring-1 ring-primary-500/30">
               <div className="flex-1 w-full flex justify-center bg-slate-50 dark:bg-dark-900/50 rounded-lg p-2 min-h-[400px]">
                 <img src={result.protectedImageUrl} alt="Protected" className="max-h-[500px] object-contain rounded" />
               </div>
               
               {/* Verification Stats Gauge/Panel */}
               <div className="w-full lg:w-1/3 space-y-6">
                 <h4 className="text-xl font-medium text-slate-900 dark:text-white mb-4 border-b border-black/10 pb-2 flex items-center">
                   <CheckCircle className="w-5 h-5 text-emerald-500 mr-2" /> 
                   Verification Score
                 </h4>
                 
                 <div className="text-center">
                   <div className="inline-flex items-center justify-center w-32 h-32 rounded-full border-4 border-primary-500 bg-white dark:bg-dark-800 shadow-[0_0_30px_rgba(59,130,246,0.3)]">
                     <span className="text-4xl font-bold text-slate-900 dark:text-white">{Math.round(result.attackData.verification_data?.verification_score || 0)}</span>
                   </div>
                 </div>
                 
                 <div className="space-y-3">
                   <ProgressBar label="Coverage" value={(result.attackData.verification_data?.coverage || 0) * 100} />
                   <ProgressBar label="Strength" value={(result.attackData.verification_data?.strength || 0) * 100} />
                   <ProgressBar label="Entropy" value={(result.attackData.verification_data?.entropy || 0) * 100} />
                   <ProgressBar label="Density" value={(result.attackData.verification_data?.density || 0) * 100} />
                 </div>
               </div>
            </div>

            <h4 className="text-lg font-medium text-slate-900 dark:text-white mt-8 mb-4 border-b border-black/10 pb-2">Evaluation Metrics</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <MetricCard title="PSNR" value={result.evaluationData.psnr?.toFixed(2) || 'N/A'} icon={ImageIcon} />
              <MetricCard title="SSIM" value={result.evaluationData.ssim?.toFixed(4) || 'N/A'} icon={ImageIcon} />
              <MetricCard title="LPIPS" value={result.evaluationData.lpips?.toFixed(4) || 'N/A'} icon={ImageIcon} />
              <MetricCard title="L2 Norm" value={result.evaluationData.l2?.toFixed(2) || 'N/A'} icon={ImageIcon} />
              <MetricCard title="Conf. Drop" value={((result.evaluationData.confidence_drop || 0) * 100).toFixed(1) + '%'} icon={ImageIcon} />
              <MetricCard title="Runtime" value={`${Math.round(result.attackData.execution_time_ms || 0)}ms`} icon={Play} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </PageContainer>
  );
}

// Helper component for the timeline
function StepIndicator({ current, target, label }: { current: string, target: string, label: string }) {
  const stateOrder = ['idle', 'uploading', 'protecting', 'evaluating', 'saving', 'completed'];
  const currentIndex = stateOrder.indexOf(current);
  const targetIndex = stateOrder.indexOf(target);
  
  const isPast = currentIndex > targetIndex || current === 'completed';
  const isActive = current === target;

  return (
    <div className="flex items-center">
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 transition-colors",
        isActive ? "bg-primary-500 border-primary-400 text-slate-900 dark:text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]" : 
        isPast ? "bg-emerald-500 border-emerald-400 text-slate-900 dark:text-white" : "bg-white dark:bg-dark-800 border-black/10 text-slate-400 dark:text-slate-500"
      )}>
        {isPast ? <Check className="w-4 h-4" /> : <div className="w-2 h-2 rounded-full bg-current" />}
      </div>
      <div className={cn(
        "ml-4 text-sm font-medium transition-colors",
        isActive ? "text-slate-900 dark:text-white" : isPast ? "text-slate-700 dark:text-slate-300" : "text-slate-400 dark:text-slate-500"
      )}>
        {label}
      </div>
    </div>
  );
}

function ImageCard({ title, url, icon }: { title: string, url: string, icon?: React.ReactNode }) {
  return (
    <div className="glass-panel p-3 flex flex-col">
      <div className="flex items-center mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">
        {icon && <span className="mr-2">{icon}</span>}
        {title}
      </div>
      <div className="flex-1 bg-slate-50 dark:bg-dark-900/50 rounded border border-black/5 overflow-hidden flex items-center justify-center min-h-[150px] p-1">
        <img src={url} alt={title} className="max-h-[200px] object-contain rounded" onError={(e) => {
           // Fallback if image fails to load
           (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiMzMzMiIC8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZpbGw9IiM2NjYiIGZvbnQtZmFtaWx5PSJzYW5zLXNlcmlmIiBmb250LXNpemU9IjE0cHgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5VbmF2YWlsYWJsZTwvdGV4dD48L3N2Zz4=';
        }} />
      </div>
    </div>
  );
}

function ProgressBar({ label, value }: { label: string, value: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-slate-700 dark:text-slate-300">{label}</span>
        <span className="text-slate-300">{Math.round(value)}%</span>
      </div>
      <div className="w-full h-1.5 bg-white dark:bg-dark-800 rounded-full overflow-hidden">
        <div 
          className="h-full bg-primary-500"
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  );
}
