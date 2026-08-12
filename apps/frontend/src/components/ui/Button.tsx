import React, { ButtonHTMLAttributes } from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = '', variant = 'primary', size = 'md', loading, icon, children, disabled, ...props }, ref) => {
    const base =
      'inline-flex items-center justify-center gap-2 font-medium transition-all duration-150 ' +
      'select-none disabled:opacity-40 disabled:pointer-events-none ' +
      'focus-visible:outline focus-visible:outline-2 focus-visible:outline-seam-gold focus-visible:outline-offset-2';

    const variants: Record<string, string> = {
      primary:
        'bg-seam-gold text-basalt hover:bg-[#f0b04d] active:scale-[0.98] rounded-md shadow-sm glow-gold',
      secondary:
        'bg-transparent border border-ash/25 text-bone hover:bg-surface-50 hover:border-ash/50 active:scale-[0.98] rounded-md',
      ghost:
        'bg-transparent text-ash hover:text-bone hover:bg-surface-50 rounded-md',
      danger:
        'bg-transparent border border-danger/30 text-danger hover:bg-danger-muted rounded-md',
    };

    const sizes: Record<string, string> = {
      sm: 'h-8 px-3 text-xs',
      md: 'h-9 px-4 text-sm',
      lg: 'h-11 px-6 text-sm font-semibold',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        aria-disabled={disabled || loading}
        className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      >
        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : icon}
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';
