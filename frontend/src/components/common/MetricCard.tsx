import React from 'react';
import { cn } from '../../utils/cn';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon?: React.ElementType;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  statusIndicator?: 'completed' | 'in-progress' | 'pending';
  className?: string;
}

export const MetricCard = React.memo(function MetricCard({ title, value, icon: Icon, description, trend, trendValue, statusIndicator, className }: MetricCardProps) {
  return (
    <div className={cn("glass-card p-5 flex flex-col", className)}>
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-slate-300 text-sm font-medium flex items-center gap-2">
          {Icon && <Icon className="w-4 h-4 text-primary-400" />}
          {title}
        </h3>
        {statusIndicator && (
          <div className={cn(
            "w-2 h-2 rounded-full shadow-[0_0_8px_currentColor]",
            statusIndicator === 'completed' ? "bg-emerald-500 text-emerald-500" :
            statusIndicator === 'in-progress' ? "bg-primary-500 text-primary-500 animate-pulse" :
            "bg-slate-500 text-slate-400 dark:text-slate-500"
          )} title={statusIndicator} />
        )}
      </div>
      
      <div className="flex items-baseline gap-2 mt-auto">
        <span className="text-3xl font-mono font-semibold text-slate-900 dark:text-white tracking-tight">{value}</span>
        {trendValue && (
          <span className={cn(
            "text-xs font-medium px-2 py-0.5 rounded-full border",
            trend === 'up' ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
            trend === 'down' ? "bg-rose-500/10 text-rose-400 border-rose-500/20" :
            "bg-slate-500/10 text-slate-300 border-slate-500/20"
          )}>
            {trendValue}
          </span>
        )}
      </div>
      {description && <p className="text-xs text-slate-400 dark:text-slate-500 mt-2">{description}</p>}
    </div>
  );
});
