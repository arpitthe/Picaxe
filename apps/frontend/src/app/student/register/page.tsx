'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/Button';
import { MatchHighlight } from '@/components/MatchHighlight';
import { useToast } from '@/components/ui/Toast';
import { UploadCloud, ScanFace, ArrowRight } from 'lucide-react';

export default function StudentRegister() {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success'>('idle');
  const [feedbackLine, setFeedbackLine] = useState('Waiting for photo upload...');
  const { toast } = useToast();

  const handleUpload = () => {
    setStatus('uploading');
    setFeedbackLine('Processing biometric face data...');
    setTimeout(() => {
      setStatus('success');
      setFeedbackLine('Face detected · Lighting: Optimal · Single face confirmed');
      toast({ type: 'success', title: 'Identity registered', description: 'You will now receive automatic photo matches.' });
    }, 2200);
  };

  return (
    <div className="min-h-dvh flex flex-col bg-basalt">
      <Navbar context="public" />

      <main className="flex-1 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="card w-full max-w-[440px] p-8"
        >
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-sans font-semibold text-2xl text-bone mb-2">Register Identity</h1>
            <p className="font-sans text-sm text-ash leading-relaxed">
              Upload a clear, front-facing photo. You only do this once — every future event match is automatic.
            </p>
          </div>

          {/* Upload area */}
          <div className="w-full aspect-square mb-5 relative">
            <AnimatePresence mode="wait">
              {status === 'success' ? (
                <motion.div key="success" initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} className="w-full h-full">
                  <MatchHighlight isMatched={true} delay={100} className="w-full h-full">
                    <div className="w-full h-full bg-basalt flex flex-col items-center justify-center gap-3">
                      <ScanFace className="w-14 h-14 text-verdigris opacity-70" />
                      <span className="font-sans font-medium text-bone text-sm">Identity Embedded</span>
                    </div>
                  </MatchHighlight>
                </motion.div>
              ) : (
                <motion.div
                  key="upload"
                  exit={{ opacity: 0 }}
                  onClick={status === 'idle' ? handleUpload : undefined}
                  className={`w-full h-full border-2 border-dashed rounded-xl flex flex-col items-center justify-center gap-4 transition-colors
                    ${status === 'uploading' ? 'border-seam-gold/40 bg-seam-gold-muted' : 'border-surface-border hover:border-ash/40 cursor-pointer'}`}
                  role="button"
                  tabIndex={0}
                  aria-label="Click to upload photo"
                  onKeyDown={e => { if (e.key === 'Enter' && status === 'idle') handleUpload(); }}
                >
                  {status === 'uploading' ? (
                    <>
                      <div className="w-8 h-8 rounded-full border-2 border-seam-gold border-t-transparent animate-spin" />
                      <span className="font-mono text-xs text-seam-gold">Extracting vector...</span>
                    </>
                  ) : (
                    <>
                      <UploadCloud className="w-10 h-10 text-ash/50" />
                      <div className="text-center">
                        <p className="font-sans text-sm font-medium text-bone">Click or drag photo here</p>
                        <p className="font-mono text-[10px] text-ash mt-1">JPG, PNG · Max 20MB</p>
                      </div>
                    </>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Status line */}
          <div className="mb-6 px-3 py-2.5 bg-basalt rounded-md border border-surface-border flex items-center gap-2">
            <div className={`w-1.5 h-1.5 rounded-full shrink-0 transition-colors ${status === 'success' ? 'bg-verdigris' : status === 'uploading' ? 'bg-seam-gold animate-pulse' : 'bg-ash/30'}`} />
            <p className="font-mono text-[11px] text-ash/80 truncate">{feedbackLine}</p>
          </div>

          {/* Consent */}
          <p className="font-sans text-[11px] text-ash/60 leading-relaxed mb-5">
            By submitting, you consent to Picaxe converting your photo into an encrypted mathematical vector for AI matching. The raw image is immediately discarded. <Link href="#" className="underline hover:text-bone transition-colors">Manage permissions.</Link>
          </p>

          {/* CTA */}
          {status === 'success' ? (
            <Link href="/student" className="block">
              <Button variant="primary" className="w-full justify-center gap-2">
                Continue to Dashboard <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          ) : (
            <Button
              variant="primary"
              className="w-full justify-center"
              onClick={handleUpload}
              loading={status === 'uploading'}
              disabled={status === 'uploading'}
            >
              Upload & Confirm
            </Button>
          )}
        </motion.div>
      </main>
    </div>
  );
}
