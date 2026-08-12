import React from 'react';
import { cn } from '@/lib/utils';

// === Skeleton Primitive ===
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('skeleton', className)} aria-hidden="true" />;
}

// === Empty State ===
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}
export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center text-center py-20 px-6', className)}>
      {icon && (
        <div className="w-14 h-14 rounded-xl bg-surface border border-surface-border flex items-center justify-center text-ash mb-5">
          {icon}
        </div>
      )}
      <p className="font-sans font-medium text-bone text-base mb-2">{title}</p>
      {description && <p className="font-sans text-ash text-sm max-w-xs leading-relaxed mb-6">{description}</p>}
      {action}
    </div>
  );
}

// === Photo Skeleton Grid ===
export function PhotoGridSkeleton({ count = 10 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} className="aspect-[4/3] rounded-lg" />
      ))}
    </div>
  );
}

// === Card Skeleton ===
export function CardSkeleton() {
  return (
    <div className="card p-6 flex flex-col gap-3">
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-3 w-1/2" />
      <Skeleton className="h-8 w-full mt-2" />
    </div>
  );
}
