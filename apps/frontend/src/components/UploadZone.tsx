'use client';
import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, Check, ScanFace, Sparkles, X } from 'lucide-react';
import { cn } from '@/lib/utils';

type PipelineStage = 'idle' | 'uploading' | 'detecting' | 'embedding' | 'matching' | 'done';

const PIPELINE: { id: PipelineStage; label: string; sub: string; duration: number }[] = [
  { id: 'uploading',  label: 'Uploading',          sub: 'Transferring files to secure storage',  duration: 1800 },
  { id: 'detecting',  label: 'Detecting Faces',     sub: 'RetinaFace scanning each photo',        duration: 1600 },
  { id: 'embedding',  label: 'Generating Embeddings', sub: 'ArcFace 512-dim vectors per face',    duration: 1400 },
  { id: 'matching',   label: 'Matching Students',   sub: 'ANN search across vector database',     duration: 1600 },
  { id: 'done',       label: 'Complete',            sub: '',                                       duration: 0 },
];

interface UploadZoneProps {
  className?: string;
  onComplete?: (matchCount: number) => void;
}

export function UploadZone({ className, onComplete }: UploadZoneProps) {
  const [stage, setStage] = useState<PipelineStage>('idle');
  const [progress, setProgress] = useState(0);
  const [fileCount, setFileCount] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const MATCH_COUNT = 18;

  const startPipeline = (files: number) => {
    setFileCount(files);
    setStage('uploading');
    setProgress(0);

    let pipelineIdx = 0;

    const advance = () => {
      pipelineIdx++;
      if (pipelineIdx >= PIPELINE.length) return;
      const next = PIPELINE[pipelineIdx];
      setStage(next.id);
      setProgress(0);
      if (next.duration > 0) {
        // Animate progress
        let p = 0;
        const iv = setInterval(() => {
          p += Math.random() * 18 + 5;
          if (p >= 100) { p = 100; clearInterval(iv); setTimeout(advance, 200); }
          setProgress(Math.min(p, 100));
        }, next.duration / 20);
      } else {
        onComplete?.(MATCH_COUNT);
      }
    };

    // First stage progress
    let p = 0;
    const iv = setInterval(() => {
      p += Math.random() * 18 + 5;
      if (p >= 100) { p = 100; clearInterval(iv); setTimeout(advance, 200); }
      setProgress(Math.min(p, 100));
    }, PIPELINE[0].duration / 20);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length) startPipeline(files.length);
  };

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) startPipeline(e.target.files.length);
  };

  const reset = () => { setStage('idle'); setProgress(0); setFileCount(0); };

  const currentPipeline = PIPELINE.find(p => p.id === stage);
  const stageIdx = PIPELINE.findIndex(p => p.id === stage);

  return (
    <div className={cn('w-full', className)}>
      {stage === 'idle' ? (
        <motion.div
          onDragOver={e => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
          animate={{ borderColor: isDragging ? 'rgba(227,165,66,0.5)' : 'rgba(148,140,122,0.2)' }}
          className="w-full border-2 border-dashed rounded-xl p-16 flex flex-col items-center justify-center text-center cursor-pointer transition-colors hover:bg-surface-50 hover:border-ash/40"
          role="button"
          tabIndex={0}
          aria-label="Upload event media"
          onKeyDown={e => e.key === 'Enter' && fileRef.current?.click()}
        >
          <div className={cn('w-14 h-14 rounded-xl flex items-center justify-center mb-4 transition-colors', isDragging ? 'bg-seam-gold-muted border border-seam-gold/30' : 'bg-surface border border-surface-border')}>
            <UploadCloud className={cn('w-7 h-7 transition-colors', isDragging ? 'text-seam-gold' : 'text-ash')} />
          </div>
          <p className="font-sans font-medium text-bone mb-1">{isDragging ? 'Drop to upload' : 'Upload Event Media'}</p>
          <p className="font-sans text-sm text-ash">Drag & drop photos or certificates, or click to browse</p>
          <p className="font-mono text-[10px] text-ash/60 mt-3">JPG, PNG, PDF up to 50MB each</p>
          <input ref={fileRef} type="file" multiple accept="image/*,.pdf" className="hidden" onChange={handleInput} />
        </motion.div>
      ) : (
        <div className="w-full border border-surface-border rounded-xl overflow-hidden bg-surface">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 bg-basalt-50 border-b border-surface-border">
            <div>
              <p className="font-sans font-medium text-bone text-sm">
                {stage === 'done' ? 'Processing Complete' : 'AI Processing...'}
              </p>
              <p className="font-mono text-[10px] text-ash mt-0.5">
                {stage === 'done' ? `${MATCH_COUNT} matches found across ${fileCount} files` : `${fileCount} file${fileCount > 1 ? 's' : ''} · ${currentPipeline?.sub}`}
              </p>
            </div>
            {stage === 'done' && <button onClick={reset} className="text-ash hover:text-bone transition-colors"><X className="w-4 h-4" /></button>}
          </div>

          {/* Pipeline Steps */}
          <div className="px-6 py-5 flex flex-col gap-4">
            {PIPELINE.filter(p => p.id !== 'done').map((p, i) => {
              const done = stageIdx > i;
              const active = stageIdx === i && stage !== 'done';
              const icon = done ? <Check className="w-3.5 h-3.5 text-basalt" /> : active ? <span className="w-2 h-2 rounded-full bg-seam-gold animate-pulse" /> : <span className="w-2 h-2 rounded-full bg-ash/20" />;
              return (
                <div key={p.id} className="flex items-center gap-4">
                  <div className={cn('w-7 h-7 rounded-full border flex items-center justify-center shrink-0 transition-all', done ? 'bg-verdigris border-verdigris' : active ? 'border-seam-gold' : 'border-ash/20')}>
                    {icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className={cn('font-sans text-sm transition-colors', done ? 'text-ash' : active ? 'text-bone font-medium' : 'text-ash/40')}>{p.label}</span>
                      {done && <span className="font-mono text-[10px] text-verdigris">✓</span>}
                    </div>
                    {active && (
                      <div className="h-0.5 bg-basalt rounded-full overflow-hidden">
                        <motion.div className="h-full bg-seam-gold rounded-full" animate={{ width: `${progress}%` }} transition={{ duration: 0.2 }} />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {stage === 'done' && (
              <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="mt-2 p-4 bg-verdigris-muted border border-verdigris/20 rounded-lg flex items-center gap-3">
                <Sparkles className="w-5 h-5 text-verdigris shrink-0" />
                <div>
                  <p className="font-sans font-medium text-bone text-sm">{MATCH_COUNT} students automatically matched</p>
                  <p className="font-mono text-[10px] text-verdigris mt-0.5">Notifications sent · Review queue updated</p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
