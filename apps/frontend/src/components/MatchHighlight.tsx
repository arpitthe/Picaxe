'use client';
import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface MatchHighlightProps {
  children: React.ReactNode;
  isMatched: boolean;
  delay?: number;
  className?: string;
}

export function MatchHighlight({ children, isMatched, delay = 0, className = '' }: MatchHighlightProps) {
  return (
    <motion.div
      className={cn('relative rounded-lg overflow-hidden border transition-shadow duration-300', className,
        isMatched ? 'border-verdigris/40 glow-green z-10' : 'border-surface-border z-0'
      )}
      initial={false}
      animate={{
        scale: isMatched ? 1.025 : 1,
      }}
      transition={{ duration: 0.35, ease: 'easeOut', delay: delay / 1000 }}
      aria-label={isMatched ? 'Your verified match' : undefined}
    >
      <div className="w-full h-full bg-surface">
        {children}
        {isMatched && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: delay / 1000 + 0.2 }}
            className="absolute top-2 right-2 flex items-center gap-1.5 bg-verdigris/10 text-verdigris font-mono text-[9px] uppercase tracking-wider px-2 py-0.5 rounded-sm border border-verdigris/25 backdrop-blur-md"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-verdigris" />
            Matched
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
