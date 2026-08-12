import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  dot?: boolean;
  pulse?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function Badge({ variant = 'default', dot, pulse, children, className }: BadgeProps) {
  const variants = {
    default: 'bg-surface-border text-bone border border-ash/20',
    success: 'bg-verdigris-muted text-verdigris border border-verdigris/25',
    warning: 'bg-seam-gold-muted text-seam-gold border border-seam-gold/25',
    danger:  'bg-danger-muted text-danger border border-danger/25',
    info:    'bg-basalt-50 text-ash border border-ash/20',
  };
  const dotColor = {
    default: 'bg-ash', success: 'bg-verdigris', warning: 'bg-seam-gold', danger: 'bg-danger', info: 'bg-ash',
  };

  return (
    <span className={cn('inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-sm', variants[variant], className)}>
      {dot && (
        <span className="relative flex h-1.5 w-1.5">
          {pulse && <span className={cn('animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', dotColor[variant])} />}
          <span className={cn('relative inline-flex rounded-full h-1.5 w-1.5', dotColor[variant])} />
        </span>
      )}
      {children}
    </span>
  );
}
