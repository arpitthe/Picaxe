'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { PhotoGrid, MediaItem } from '@/components/PhotoGrid';
import { EmptyState, PhotoGridSkeleton } from '@/components/ui/Loading';
import { useToast } from '@/components/ui/Toast';
import { Download, FileText, CheckCircle2, ChevronLeft, Search, Image as ImgIcon, SlidersHorizontal } from 'lucide-react';

const eventPhotos: MediaItem[] = Array.from({ length: 42 }).map((_, i) => ({
  id: `photo-${i}`,
  url: '',
  isMatch: [3, 9, 14, 27].includes(i),
  type: 'photo'
}));

const eventCerts: MediaItem[] = [
  { id: 'cert-1', url: '', isMatch: true, type: 'certificate' },
  { id: 'cert-2', url: '', isMatch: false, type: 'certificate' }
];

export default function StudentEventView({ params }: { params: { id: string } }) {
  const [viewMode, setViewMode] = useState<'matches' | 'all'>('matches');
  const { toast } = useToast();

  const photos = viewMode === 'matches' ? eventPhotos.filter(p => p.isMatch) : eventPhotos;
  const certs  = viewMode === 'matches' ? eventCerts.filter(c => c.isMatch) : eventCerts;
  const matchedCount = eventPhotos.filter(p => p.isMatch).length + eventCerts.filter(c => c.isMatch).length;

  const handleDownloadAll = () => {
    toast({ type: 'success', title: 'Download started', description: `${matchedCount} matched files preparing...` });
  };

  return (
    <div className="min-h-dvh flex flex-col bg-basalt">
      <Navbar context="student" />

      <main className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-8 py-8 md:py-12">

        {/* Back + search row */}
        <div className="flex items-center justify-between mb-8 gap-4">
          <Link href="/student" className="flex items-center gap-1.5 text-ash hover:text-bone transition-colors font-sans text-sm">
            <ChevronLeft className="w-4 h-4" /> Dashboard
          </Link>
          <div className="flex items-center gap-2 bg-surface-50 border border-surface-border rounded-md px-3 py-2 w-48 md:w-72 focus-within:border-seam-gold/50 transition-colors">
            <Search className="w-3.5 h-3.5 text-ash shrink-0" />
            <input type="text" placeholder="Search media..." className="bg-transparent text-sm text-bone font-sans outline-none w-full placeholder-ash/40" aria-label="Search event media" />
          </div>
        </div>

        {/* Event Header */}
        <div className="mb-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <h1 className="font-sans font-semibold text-4xl md:text-5xl text-bone tracking-tight mb-3">
                Annual Tech Fest — 2026
              </h1>
              <div className="flex flex-wrap items-center gap-3">
                <span className="font-mono text-xs text-ash">Mar 14, 2026</span>
                <span className="text-ash/30">·</span>
                <span className="font-mono text-xs text-ash">142 photos</span>
                <span className="text-ash/30">·</span>
                <span className="font-mono text-xs text-ash">38 certificates</span>
                {matchedCount > 0 && (
                  <>
                    <span className="text-ash/30">·</span>
                    <Badge variant="success" dot pulse={false}>{matchedCount} AI Matched</Badge>
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              {matchedCount > 0 && (
                <Button variant="secondary" size="sm" icon={<Download className="w-4 h-4" />} onClick={handleDownloadAll}>
                  Download Matches
                </Button>
              )}
              {/* Toggle */}
              <div className="flex items-center bg-surface border border-surface-border p-1 rounded-md">
                <button
                  className={`px-3 py-1.5 text-sm font-sans rounded-sm transition-all ${viewMode === 'matches' ? 'bg-basalt text-bone shadow-sm border border-surface-border' : 'text-ash hover:text-bone'}`}
                  onClick={() => setViewMode('matches')}
                  aria-pressed={viewMode === 'matches'}
                >
                  Your Matches ({matchedCount})
                </button>
                <button
                  className={`px-3 py-1.5 text-sm font-sans rounded-sm transition-all ${viewMode === 'all' ? 'bg-basalt text-bone shadow-sm border border-surface-border' : 'text-ash hover:text-bone'}`}
                  onClick={() => setViewMode('all')}
                  aria-pressed={viewMode === 'all'}
                >
                  All Media (180)
                </button>
              </div>
            </div>
          </div>

          {/* AI confidence summary banner */}
          {viewMode === 'matches' && matchedCount > 0 && (
            <motion.div initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} className="mt-6 p-4 bg-verdigris-muted border border-verdigris/20 rounded-lg flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-verdigris shrink-0" />
              <p className="font-sans text-sm text-bone">
                AI matched you to <strong>{matchedCount} items</strong> with an average confidence of <strong>94%</strong>.
              </p>
            </motion.div>
          )}
        </div>

        {/* Certificates */}
        <section className="mb-16" aria-label="Certificates">
          <SectionHeader title="Certificates" matched={viewMode === 'matches'} count={certs.length} />
          {certs.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {certs.map(cert => (
                <CertCard key={cert.id} cert={cert} />
              ))}
            </div>
          ) : (
            <EmptyState
              icon={<FileText className="w-6 h-6" />}
              title="No certificates yet"
              description="We'll notify you once AI finishes processing certificates for this event."
            />
          )}
        </section>

        {/* Photos */}
        <section aria-label="Event photos">
          <SectionHeader title="Photos" matched={viewMode === 'matches'} count={photos.length} />
          {photos.length > 0 ? (
            <PhotoGrid items={photos} />
          ) : (
            <EmptyState
              icon={<ImgIcon className="w-6 h-6" />}
              title="No matched photos yet"
              description="We couldn't find you in these photos yet. Try switching to All Media to browse manually."
              action={<Button variant="secondary" size="sm" onClick={() => setViewMode('all')}>Browse All Media</Button>}
            />
          )}
        </section>
      </main>
    </div>
  );
}

function SectionHeader({ title, matched, count }: { title: string, matched: boolean, count: number }) {
  return (
    <div className="flex items-center gap-3 mb-6">
      <h2 className="font-sans font-semibold text-xl text-bone">{title}</h2>
      {matched && count > 0 && <Badge variant="success" dot>Verified</Badge>}
      <span className="font-mono text-xs text-ash ml-auto">{count} item{count !== 1 ? 's' : ''}</span>
    </div>
  );
}

function CertCard({ cert }: { cert: MediaItem }) {
  const { toast } = useToast();
  return (
    <div className={`card p-5 flex items-center justify-between gap-4 hover:border-ash/25 transition-colors ${cert.isMatch ? 'border-verdigris/25' : ''}`}>
      <div className="flex items-center gap-4">
        <div className="w-11 h-14 bg-basalt border border-surface-border rounded-md flex items-center justify-center text-ash/30 shrink-0">
          <FileText className="w-5 h-5" />
        </div>
        <div>
          <p className="font-sans font-medium text-bone text-sm">TechFest_Participation_{cert.id}.pdf</p>
          {cert.isMatch
            ? <p className="font-mono text-[10px] text-verdigris mt-1">AI Match · 96% confidence</p>
            : <p className="font-mono text-[10px] text-ash mt-1">Not matched to you</p>}
        </div>
      </div>
      {cert.isMatch && (
        <Button
          variant="ghost"
          size="sm"
          icon={<Download className="w-4 h-4" />}
          aria-label={`Download certificate ${cert.id}`}
          onClick={() => toast({ type: 'success', title: 'Download started', description: `TechFest_Participation_${cert.id}.pdf` })}
        />
      )}
    </div>
  );
}
