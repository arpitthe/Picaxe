'use client';
import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, AlertCircle, X, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

type ToastType = 'success' | 'error' | 'info';
interface Toast {
  id: string;
  type: ToastType;
  title: string;
  description?: string;
}
interface ToastContextValue {
  toast: (t: Omit<Toast, 'id'>) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((t: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).slice(2);
    setToasts(prev => [...prev, { ...t, id }]);
    setTimeout(() => setToasts(prev => prev.filter(x => x.id !== id)), 4000);
  }, []);

  const remove = (id: string) => setToasts(prev => prev.filter(x => x.id !== id));

  const icons = { success: CheckCircle2, error: AlertCircle, info: Info };
  const colors = {
    success: 'text-verdigris border-verdigris/20',
    error:   'text-danger border-danger/20',
    info:    'text-ash border-ash/20',
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none">
        <AnimatePresence>
          {toasts.map(t => {
            const Icon = icons[t.type];
            return (
              <motion.div
                key={t.id}
                initial={{ opacity: 0, x: 60, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 60, scale: 0.95 }}
                transition={{ duration: 0.2, ease: 'easeOut' }}
                className={cn(
                  'pointer-events-auto w-80 bg-surface border rounded-lg p-4 shadow-overlay',
                  'flex items-start gap-3',
                  colors[t.type]
                )}
              >
                <Icon className="w-4 h-4 mt-0.5 shrink-0" />
                <div className="flex-1">
                  <p className="text-bone font-sans font-medium text-sm">{t.title}</p>
                  {t.description && <p className="text-ash text-xs mt-0.5">{t.description}</p>}
                </div>
                <button onClick={() => remove(t.id)} className="text-ash hover:text-bone transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be inside ToastProvider');
  return ctx;
}
