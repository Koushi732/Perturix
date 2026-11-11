import React, { useEffect } from 'react';
import { useToast, Toast } from '../../context/ToastContext';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import { cn } from '../../utils/cn';

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: string) => void }) {
  useEffect(() => {
    if (toast.duration !== 0) {
      const timer = setTimeout(() => onRemove(toast.id), toast.duration || 5000);
      return () => clearTimeout(timer);
    }
  }, [toast, onRemove]);

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-500" aria-hidden="true" />,
    error: <AlertCircle className="w-5 h-5 text-rose-500" aria-hidden="true" />,
    warning: <AlertTriangle className="w-5 h-5 text-amber-500" aria-hidden="true" />,
    info: <Info className="w-5 h-5 text-primary-500" aria-hidden="true" />
  };

  const bgColors = {
    success: 'bg-emerald-500/10 border-emerald-500/20',
    error: 'bg-rose-500/10 border-rose-500/20',
    warning: 'bg-amber-500/10 border-amber-500/20',
    info: 'bg-primary-500/10 border-primary-500/20'
  };

  return (
    <div 
      className={cn(
        "flex items-start w-full max-w-sm p-4 mb-4 border rounded-lg shadow-lg pointer-events-auto backdrop-blur-md animate-in slide-in-from-right-full duration-200",
        bgColors[toast.type] || bgColors.info
      )}
      role="alert"
    >
      <div className="shrink-0 mr-3">
        {icons[toast.type]}
      </div>
      <div className="flex-1 text-sm font-medium text-slate-900 dark:text-white pt-0.5">
        {toast.message}
      </div>
      <button 
        onClick={() => onRemove(toast.id)} 
        className="shrink-0 ml-3 text-slate-300 hover:text-slate-900 dark:hover:text-white dark:text-white transition-colors"
        aria-label="Close notification"
      >
        <X className="w-4 h-4" aria-hidden="true" />
      </button>
    </div>
  );
}

export function ToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <div 
      className="fixed bottom-0 right-0 z-50 flex flex-col p-4 w-full max-w-sm pointer-events-none"
      aria-live="polite"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={removeToast} />
      ))}
    </div>
  );
}
