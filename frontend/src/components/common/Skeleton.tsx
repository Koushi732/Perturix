import React from 'react';
import { cn } from '../../utils/cn';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export const Skeleton = React.memo(function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-slate-100 dark:bg-dark-700/50",
        className
      )}
      {...props}
    />
  );
});

export const CardSkeleton = React.memo(function CardSkeleton({ className }: SkeletonProps) {
  return (
    <div className={cn("glass-card p-5 flex flex-col space-y-4", className)}>
      <div className="flex justify-between items-start">
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-2 w-2 rounded-full" />
      </div>
      <div className="flex items-baseline gap-2 mt-auto">
        <Skeleton className="h-8 w-1/2" />
      </div>
      <Skeleton className="h-3 w-2/3 mt-2" />
    </div>
  );
});

export const TableRowSkeleton = React.memo(function TableRowSkeleton() {
  return (
    <div className="flex items-center space-x-4 py-3 border-b border-black/5">
      <Skeleton className="h-4 w-8" />
      <Skeleton className="h-4 w-1/4" />
      <Skeleton className="h-4 w-1/5" />
      <Skeleton className="h-4 w-1/6" />
      <Skeleton className="h-4 w-12 ml-auto" />
    </div>
  );
});

export const ImagePreviewSkeleton = React.memo(function ImagePreviewSkeleton({ className }: SkeletonProps) {
  return (
    <div className={cn("w-full h-48 rounded-lg overflow-hidden relative", className)}>
      <Skeleton className="absolute inset-0 h-full w-full rounded-none" />
    </div>
  );
});
