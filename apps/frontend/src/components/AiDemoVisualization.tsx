'use client';
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Image as Img, ScanFace, Sparkles, Check } from 'lucide-react';

// ─────────────────────────────────────────────
// The Interactive AI Demo — centrepiece of the landing page
// Simulates: Upload → Detect → Embed → Match → Done
// ─────────────────────────────────────────────

type Stage = 'upload' | 'detect' | 'embed' | 'match' | 'done';

const STAGES: { id: Stage; label: string; duration: number }[] = [
  { id: 'upload', label: 'Uploading photos',          duration: 1800 },
  { id: 'detect', label: 'Detecting faces',           duration: 1600 },
  { id: 'embed',  label: 'Generating embeddings',     duration: 1400 },
  { id: 'match',  label: 'Matching to students',      duration: 1600 },
  { id: 'done',   label: 'Complete',                  duration: 0 },
];

const FILES = ['IMG_4021.jpg', 'IMG_4022.jpg', 'IMG_4023.jpg', 'IMG_4024.jpg', 'IMG_4025.jpg'];

const MATCHES = [
  { name: 'Arpit Singh',   confidence: 98 },
  { name: 'Rahul Mehta',   confidence: 95 },
  { name: 'Priya Sharma',  confidence: 92 },
  { name: 'Daniel Osei',   confidence: 89 },
];

export function AiDemoVisualization() {
  const [stageIdx, setStageIdx] = useState(0);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [revealedMatches, setRevealedMatches] = useState<number[]>([]);
  const [running, setRunning] = useState(false);

  const stage = STAGES[stageIdx];

  const startDemo = () => {
    setStageIdx(0);
    setUploadProgress(0);
    setRevealedMatches([]);
    setRunning(true);
  };

  useEffect(() => {
    if (!running) return;
    if (stageIdx >= STAGES.length - 1) { setRunning(false); return; }

    const cur = STAGES[stageIdx];
    const timer = setTimeout(() => setStageIdx(i => i + 1), cur.duration);
    return () => clearTimeout(timer);
  }, [stageIdx, running]);

  // Simulate upload progress
  useEffect(() => {
    if (!running || stage.id !== 'upload') return;
    let v = 0;
    const iv = setInterval(() => {
      v += Math.random() * 15;
      if (v >= 100) { v = 100; clearInterval(iv); }
      setUploadProgress(Math.min(v, 100));
    }, 200);
    return () => clearInterval(iv);
  }, [stage.id, running]);

  // Reveal matches one by one
  useEffect(() => {
    if (!running || stage.id !== 'match') return;
    let i = 0;
    const iv = setInterval(() => {
      setRevealedMatches(prev => [...prev, i]);
      i++;
      if (i >= MATCHES.length) clearInterval(iv);
    }, 380);
    return () => clearInterval(iv);
  }, [stage.id, running]);

  const stageProgress = stageIdx / (STAGES.length - 1);

  return (
    <div className="w-full bg-surface border border-surface-border rounded-xl overflow-hidden shadow-overlay">
      {/* Terminal-style top bar */}
      <div className="flex items-center gap-2 px-4 py-3 bg-basalt-50 border-b border-surface-border">
        <div className="w-3 h-3 rounded-full bg-danger/50" />
        <div className="w-3 h-3 rounded-full bg-seam-gold/50" />
        <div className="w-3 h-3 rounded-full bg-verdigris/50" />
        <span className="ml-3 font-mono text-xs text-ash">picaxe — ai pipeline</span>
        {!running && (
          <button
            onClick={startDemo}
            className="ml-auto font-mono text-[10px] text-seam-gold hover:text-bone transition-colors uppercase tracking-widest flex items-center gap-1"
          >
            <span>{stageIdx === 0 ? '▶ Run Demo' : '↺ Run Again'}</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 min-h-[380px]">
        {/* Left: pipeline stages */}
        <div className="flex flex-col p-6 gap-3 border-r border-surface-border">
          <p className="font-mono text-[10px] text-ash uppercase tracking-widest mb-2">Pipeline</p>
          {STAGES.filter(s => s.id !== 'done').map((s, i) => {
            const done = stageIdx > i;
            const active = stageIdx === i && running;
            return (
              <div key={s.id} className="flex items-center gap-3">
                <div className={`w-6 h-6 rounded-full border flex items-center justify-center shrink-0 transition-all duration-300
                  ${done ? 'bg-verdigris border-verdigris' : active ? 'border-seam-gold' : 'border-ash/20'}`}>
                  {done
                    ? <Check className="w-3 h-3 text-basalt" />
                    : active
                    ? <span className="w-2 h-2 rounded-full bg-seam-gold animate-pulse" />
                    : <span className="w-2 h-2 rounded-full bg-ash/20" />}
                </div>
                <span className={`font-mono text-xs transition-colors ${done ? 'text-ash' : active ? 'text-bone' : 'text-ash/40'}`}>
                  {s.label}
                </span>
              </div>
            );
          })}

          {/* Overall progress bar */}
          <div className="mt-auto pt-6">
            <div className="flex justify-between mb-2">
              <span className="font-mono text-[10px] text-ash">Overall Progress</span>
              <span className="font-mono text-[10px] text-bone">{Math.round(stageProgress * 100)}%</span>
            </div>
            <div className="h-1 bg-basalt rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-seam-gold rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${stageProgress * 100}%` }}
                transition={{ duration: 0.4 }}
              />
            </div>
          </div>
        </div>

        {/* Right: live output */}
        <div className="flex flex-col p-6 gap-4">
          <AnimatePresence mode="wait">

            {/* Upload Stage */}
            {(stageIdx === 0 && !running) && (
              <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center h-full gap-4">
                <div className="w-16 h-16 rounded-xl bg-basalt border-2 border-dashed border-ash/20 flex items-center justify-center">
                  <Img className="w-7 h-7 text-ash/40" />
                </div>
                <p className="font-mono text-xs text-ash text-center">Click ▶ Run Demo to see the AI pipeline in action</p>
              </motion.div>
            )}

            {stage.id === 'upload' && running && (
              <motion.div key="upload" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
                <p className="font-mono text-[10px] text-ash uppercase tracking-widest mb-3">Uploading Files</p>
                <div className="flex flex-col gap-2">
                  {FILES.map((f, i) => {
                    const loaded = uploadProgress > (i / FILES.length) * 100;
                    return (
                      <div key={f} className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full shrink-0 ${loaded ? 'bg-verdigris' : 'bg-ash/20'}`} />
                        <span className={`font-mono text-xs ${loaded ? 'text-bone' : 'text-ash/40'}`}>{f}</span>
                        {loaded && <span className="font-mono text-[9px] text-verdigris ml-auto">✓</span>}
                      </div>
                    );
                  })}
                </div>
                <div className="mt-4 h-1 bg-basalt rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-seam-gold rounded-full"
                    animate={{ width: `${uploadProgress}%` }}
                    transition={{ duration: 0.2 }}
                  />
                </div>
                <p className="font-mono text-[10px] text-ash mt-2">{Math.round(uploadProgress)}% uploaded</p>
              </motion.div>
            )}

            {stage.id === 'detect' && (
              <motion.div key="detect" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-3">
                <p className="font-mono text-[10px] text-ash uppercase tracking-widest mb-1">Face Detection</p>
                {FILES.map((f, i) => (
                  <motion.div key={f} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.28 }}
                    className="flex items-center justify-between bg-basalt-50 border border-surface-border rounded-md px-3 py-2">
                    <div className="flex items-center gap-2">
                      <ScanFace className="w-4 h-4 text-seam-gold" />
                      <span className="font-mono text-xs text-bone">{f}</span>
                    </div>
                    <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.28 + 0.5 }}
                      className="font-mono text-[10px] text-verdigris">1 face</motion.span>
                  </motion.div>
                ))}
              </motion.div>
            )}

            {stage.id === 'embed' && (
              <motion.div key="embed" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-3">
                <p className="font-mono text-[10px] text-ash uppercase tracking-widest mb-1">Embedding Vectors</p>
                <div className="grid grid-cols-8 gap-1">
                  {Array.from({ length: 64 }).map((_, i) => (
                    <motion.div key={i}
                      initial={{ opacity: 0.1 }}
                      animate={{ opacity: [0.1, 1, 0.1] }}
                      transition={{ duration: 0.6, delay: i * 0.02, repeat: 2 }}
                      className="h-2 bg-seam-gold rounded-sm"
                      style={{ opacity: Math.random() * 0.8 + 0.2 }}
                    />
                  ))}
                </div>
                <p className="font-mono text-[10px] text-ash">512-dimensional ArcFace vectors</p>
              </motion.div>
            )}

            {stage.id === 'match' && (
              <motion.div key="match" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-2">
                <p className="font-mono text-[10px] text-ash uppercase tracking-widest mb-2">Student Matches</p>
                {MATCHES.map((m, i) => (
                  <AnimatePresence key={m.name}>
                    {revealedMatches.includes(i) && (
                      <motion.div
                        initial={{ opacity: 0, x: -12 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center justify-between bg-verdigris-muted border border-verdigris/20 rounded-md px-3 py-2.5"
                      >
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-full bg-verdigris/20 border border-verdigris/30 flex items-center justify-center">
                            <span className="font-sans text-[9px] font-medium text-verdigris">{m.name[0]}</span>
                          </div>
                          <span className="font-sans text-sm text-bone">{m.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] text-verdigris">{m.confidence}%</span>
                          <Check className="w-3.5 h-3.5 text-verdigris" />
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                ))}
              </motion.div>
            )}

            {stage.id === 'done' && (
              <motion.div key="done" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center justify-center h-full gap-4 text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                  className="w-16 h-16 rounded-full bg-verdigris-muted border border-verdigris/30 flex items-center justify-center"
                >
                  <Sparkles className="w-7 h-7 text-verdigris" />
                </motion.div>
                <div>
                  <p className="font-sans font-semibold text-bone text-xl">{MATCHES.length} matches found</p>
                  <p className="font-mono text-xs text-ash mt-1">across {FILES.length} photos in 4.2s</p>
                </div>
                <button onClick={startDemo} className="font-mono text-[10px] text-seam-gold hover:text-bone transition-colors uppercase tracking-widest mt-2">
                  ↺ Run again
                </button>
              </motion.div>
            )}

          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
