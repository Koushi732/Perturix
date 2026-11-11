import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

interface PageContainerProps {
  children: ReactNode;
  className?: string;
  title: string;
  description?: string;
}

export const PageContainer = React.memo(function PageContainer({ children, className, title, description }: PageContainerProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn("flex flex-col space-y-6 w-full", className)}
    >
      <div className="flex flex-col">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">{title}</h1>
        {description && <p className="text-slate-300 mt-1 text-sm">{description}</p>}
      </div>
      <div className="w-full">
        {children}
      </div>
    </motion.div>
  );
});
