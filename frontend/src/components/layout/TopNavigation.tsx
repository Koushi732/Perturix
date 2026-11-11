import React from 'react';
import { ChevronRight, Bell } from 'lucide-react';
import { cn } from '../../utils/cn';
import { ThemeToggle } from '../common/ThemeToggle';

export const TopNavigation = React.memo(function TopNavigation({ breadcrumbs }: { breadcrumbs: string[] }) {
  return (
    <header className="h-16 flex items-center justify-between px-8 bg-slate-50 dark:bg-dark-900/50 backdrop-blur-md border-b border-black/5 sticky top-0 z-10 shrink-0">
      
      <div className="flex items-center text-sm font-medium text-slate-300">
        <span className="hover:text-slate-900 dark:hover:text-white dark:text-white cursor-pointer transition-colors">Perturix</span>
        {breadcrumbs.map((crumb, idx) => (
          <React.Fragment key={idx}>
            <ChevronRight className="w-4 h-4 mx-2 text-slate-300" />
            <span className={cn(idx === breadcrumbs.length - 1 ? 'text-slate-900 dark:text-white' : 'hover:text-slate-900 dark:hover:text-white dark:text-white transition-colors cursor-pointer')}>
              {crumb}
            </span>
          </React.Fragment>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <ThemeToggle />
        <button aria-label="Notifications" className="text-slate-300 dark:text-slate-700 hover:text-slate-900 dark:hover:text-white transition-colors relative">
          <Bell className="w-5 h-5" aria-hidden="true" />
          <span className="absolute top-0 right-0 w-2 h-2 bg-primary-500 rounded-full" />
        </button>
        <a href="https://github.com/Koushi732/Perturix" target="_blank" rel="noreferrer" aria-label="GitHub Repository" className="text-slate-300 dark:text-slate-700 hover:text-slate-900 dark:hover:text-white transition-colors font-medium text-sm">
          GitHub
        </a>
        <div className="w-8 h-8 rounded-full bg-white dark:bg-dark-800 border border-black/10 flex items-center justify-center">
          <span className="text-xs font-medium text-primary-500">PX</span>
        </div>
      </div>
    </header>
  );
});
