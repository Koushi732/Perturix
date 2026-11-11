import React from 'react';
import { AlertCircle } from 'lucide-react';
import { cn } from '../../utils/cn';

interface FormErrorProps {
  error: string | string[] | null;
  className?: string;
}

export const FormError = React.memo(function FormError({ error, className }: FormErrorProps) {
  if (!error || (Array.isArray(error) && error.length === 0)) return null;

  const errorList = Array.isArray(error) ? error : [error];

  return (
    <div 
      className={cn("mt-2 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-start text-sm animate-in fade-in duration-200", className)}
      role="alert"
    >
      <AlertCircle className="w-5 h-5 mr-3 shrink-0 mt-0.5" aria-hidden="true" />
      <div className="flex flex-col">
        {errorList.map((err, idx) => (
          <span key={idx}>{err}</span>
        ))}
      </div>
    </div>
  );
});
