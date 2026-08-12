import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Home, LogOut } from 'lucide-react';

// Shared nav for all portal headers
interface NavbarProps {
  context?: 'student' | 'organization' | 'admin' | 'public';
  className?: string;
}

export function Navbar({ context = 'public', className }: NavbarProps) {
  const labels = { student: 'Student', organization: 'Organization', admin: 'Admin Console', public: '' };
  const contextLabel = labels[context];

  return (
    <header className={cn(
      'w-full h-14 flex items-center justify-between px-6 border-b border-surface-border sticky top-0 z-50 backdrop-blur-md',
      context === 'admin' ? 'bg-surface/95' : 'bg-basalt/90',
      className
    )}>
      <Link href="/" className="flex items-center gap-2.5 font-sans font-semibold text-bone hover:opacity-80 transition-opacity" aria-label="Picaxe home">
        {/* The brand mark: 2x2 grid of dots */}
        <PicaxeMark />
        <span className="tracking-tight">Picaxe</span>
        {contextLabel && (
          <span className="font-mono text-[10px] text-ash uppercase tracking-widest pl-2 border-l border-ash/20 ml-1">
            {contextLabel}
          </span>
        )}
      </Link>

      {context === 'public' && (
        <nav className="hidden md:flex items-center gap-6 font-sans text-sm text-ash">
          <Link href="/student" className="hover:text-bone transition-colors">Students</Link>
          <Link href="/organization" className="hover:text-bone transition-colors">Organizations</Link>
          <Link href="/admin" className="hover:text-bone transition-colors">Enterprise</Link>
        </nav>
      )}

      {context === 'student' && (
        <nav className="flex items-center gap-4 font-sans text-sm text-ash">
          <Link href="/student" className="hover:text-bone transition-colors hidden sm:block">Dashboard</Link>
          <Link href="/" className="flex items-center gap-1.5 hover:text-bone transition-colors text-xs">
            <Home className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Home</span>
          </Link>
        </nav>
      )}

      {context === 'organization' && (
        <nav className="flex items-center gap-4 font-sans text-sm text-ash">
          <Link href="/organization" className="hover:text-bone transition-colors hidden sm:block">Dashboard</Link>
          <Link href="/" className="flex items-center gap-1.5 hover:text-bone transition-colors text-xs">
            <Home className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Home</span>
          </Link>
        </nav>
      )}

      {context === 'admin' && (
        <nav className="flex items-center gap-4 font-sans text-sm text-ash">
          <Link href="/" className="flex items-center gap-1.5 hover:text-bone transition-colors text-xs">
            <Home className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Home</span>
          </Link>
        </nav>
      )}
    </header>
  );
}

// The Picaxe brand mark — a 2×2 grid of dots that suggests a coordinate / face recognition grid
export function PicaxeMark({ size = 16, className }: { size?: number; className?: string }) {
  return (
    <svg
      width={size} height={size} viewBox="0 0 16 16"
      fill="none" aria-hidden="true"
      className={className}
    >
      {/* 2×2 dot grid */}
      <rect x="0" y="0" width="6" height="6" rx="1.5" fill="currentColor" className="text-seam-gold" />
      <rect x="10" y="0" width="6" height="6" rx="1.5" fill="currentColor" className="text-seam-gold opacity-60" />
      <rect x="0" y="10" width="6" height="6" rx="1.5" fill="currentColor" className="text-seam-gold opacity-60" />
      <rect x="10" y="10" width="6" height="6" rx="1.5" fill="currentColor" className="text-verdigris" />
    </svg>
  );
}
