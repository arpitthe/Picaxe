'use client';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Navbar, PicaxeMark } from '@/components/Navbar';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { AiDemoVisualization } from '@/components/AiDemoVisualization';
import { type Variants } from 'framer-motion';
import { ArrowRight, UserCheck, Building2, ShieldCheck, Image as ImgIcon, Clock, Zap } from 'lucide-react';

const fadeUp: Variants = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { duration: 0.5 } } };
const stagger: Variants = { show: { transition: { staggerChildren: 0.1 } } };

export default function Home() {
  return (
    <div className="min-h-dvh flex flex-col bg-basalt">
      <Navbar context="public" />

      <main className="flex-1 flex flex-col">

        {/* ── Hero ── */}
        <section className="relative flex flex-col items-center text-center pt-24 pb-20 px-6 overflow-hidden">
          {/* Brand grid background */}
          <div className="absolute inset-0 picaxe-grid-bg picaxe-grid-mask pointer-events-none" />

          {/* Subtle radial glow behind hero */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-seam-gold/5 rounded-full blur-3xl pointer-events-none" />

          <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10 flex flex-col items-center max-w-4xl">
            <motion.div variants={fadeUp}>
              <Badge variant="success" dot pulse className="mb-8">AI Face Recognition · Live</Badge>
            </motion.div>

            <motion.h1 variants={fadeUp} className="font-sans font-semibold text-5xl md:text-7xl text-bone leading-[1.05] tracking-tight mb-6">
              Every event.<br />
              <span className="text-seam-gold">Every photo.</span><br />
              Instantly yours.
            </motion.h1>

            <motion.p variants={fadeUp} className="font-sans text-lg md:text-xl text-ash max-w-2xl leading-relaxed mb-10">
              Picaxe uses AI face recognition to automatically find and deliver your event photos and certificates — no searching, no shared drives, no manual tagging.
            </motion.p>

            <motion.div variants={fadeUp} className="flex flex-wrap gap-4 justify-center">
              <Link href="/student/register">
                <Button variant="primary" size="lg" className="rounded-md gap-2">
                  Register Face <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link href="/organization">
                <Button variant="secondary" size="lg" className="rounded-md">
                  Organization Login
                </Button>
              </Link>
            </motion.div>
          </motion.div>
        </section>

        {/* ── Live AI Demo ── */}
        <section className="px-6 pb-24 max-w-5xl mx-auto w-full">
          <div className="text-center mb-10">
            <p className="font-mono text-xs text-ash uppercase tracking-widest mb-3">Interactive Demo</p>
            <h2 className="font-sans font-semibold text-3xl text-bone">See the AI pipeline in action</h2>
          </div>
          <AiDemoVisualization />
        </section>

        {/* ── How it Works ── */}
        <section className="px-6 py-20 max-w-5xl mx-auto w-full border-t border-surface-border">
          <div className="text-center mb-14">
            <p className="font-mono text-xs text-ash uppercase tracking-widest mb-3">How it Works</p>
            <h2 className="font-sans font-semibold text-3xl text-bone">From upload to inbox in seconds</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { icon: <ImgIcon className="w-5 h-5 text-seam-gold" />, step: '01', title: 'Register Once', body: 'Upload a clear photo. We convert it into a secure mathematical embedding — your permanent face key.' },
              { icon: <Zap className="w-5 h-5 text-seam-gold" />, step: '02', title: 'AI Processes Events', body: 'Organizations upload event photos. Our AI scans every face and certificate automatically in the background.' },
              { icon: <UserCheck className="w-5 h-5 text-seam-gold" />, step: '03', title: 'Receive Your Matches', body: 'Log in and instantly see every photo and certificate confirmed to be yours, with AI confidence scores.' },
            ].map(item => (
              <div key={item.step} className="card p-6 flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-basalt border border-surface-border flex items-center justify-center">{item.icon}</div>
                  <span className="font-mono text-xs text-ash/40">{item.step}</span>
                </div>
                <div>
                  <h3 className="font-sans font-semibold text-bone mb-1.5">{item.title}</h3>
                  <p className="font-sans text-sm text-ash leading-relaxed">{item.body}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── Student / Org Role Split ── */}
        <section className="px-6 py-20 max-w-5xl mx-auto w-full border-t border-surface-border">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <RoleCard
              icon={<UserCheck className="w-6 h-6 text-seam-gold" />}
              who="For Students"
              headline="Your photos, found automatically"
              bullets={['Register your face once', 'Matches delivered to your dashboard', 'Download certificates with one click', 'Manual search always available']}
              cta="Get Started"
              href="/student/register"
            />
            <RoleCard
              icon={<Building2 className="w-6 h-6 text-seam-gold" />}
              who="For Organizations"
              headline="Distribute photos at any scale"
              bullets={['Bulk upload thousands of photos', 'Automatic student matching', 'Review queue for uncertain matches', 'Analytics and audit logs']}
              cta="Create Event"
              href="/organization"
            />
          </div>
        </section>

        {/* ── Security ── */}
        <section className="px-6 py-20 border-t border-surface-border">
          <div className="max-w-3xl mx-auto text-center flex flex-col items-center gap-6">
            <div className="w-12 h-12 rounded-xl bg-surface border border-surface-border flex items-center justify-center">
              <ShieldCheck className="w-6 h-6 text-verdigris" />
            </div>
            <h2 className="font-sans font-semibold text-2xl text-bone">Built for biometric privacy</h2>
            <p className="font-sans text-ash leading-relaxed">
              Your face photo is converted to an encrypted mathematical vector and immediately discarded. We never store raw images. You can delete your data at any time. Every action is logged in an immutable audit trail.
            </p>
            <Link href="#" className="font-mono text-xs text-ash underline hover:text-bone transition-colors uppercase tracking-widest">
              Read Privacy Policy
            </Link>
          </div>
        </section>

        {/* ── FAQ ── */}
        <section className="px-6 py-20 max-w-3xl mx-auto w-full border-t border-surface-border">
          <h2 className="font-sans font-semibold text-2xl text-bone mb-10 text-center">Frequently Asked Questions</h2>
          <div className="flex flex-col divide-y divide-surface-border">
            {[
              { q: 'How accurate is the face recognition?', a: 'We use ArcFace embeddings, which are state-of-the-art for face verification. High-confidence matches (≥92%) are auto-delivered. Lower-confidence matches go to a review queue before distribution.' },
              { q: 'Is my face photo stored?', a: 'No. Your photo is immediately converted to a 512-dimensional embedding vector and discarded. The vector itself is encrypted at rest and in transit.' },
              { q: 'What if my photo isn\'t matched?', a: 'You can manually search any event by name or date. You can also "claim" a photo, which gets reviewed by the organization and improves future matching.' },
              { q: 'Which file formats are supported?', a: 'Photos: JPG, PNG, HEIC. Certificates: PDF, JPG, PNG. Bulk uploads of up to 10,000 files per batch are supported.' },
            ].map(item => (
              <div key={item.q} className="py-6">
                <p className="font-sans font-medium text-bone mb-2">{item.q}</p>
                <p className="font-sans text-sm text-ash leading-relaxed">{item.a}</p>
              </div>
            ))}
          </div>
        </section>

      </main>

      <footer className="w-full py-8 px-6 border-t border-surface-border">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 font-sans font-semibold text-bone">
            <PicaxeMark />
            <span>Picaxe</span>
          </div>
          <p className="font-mono text-xs text-ash">© 2026 Picaxe. Built for universities, companies, and events.</p>
          <div className="flex gap-4 font-mono text-xs text-ash">
            <Link href="#" className="hover:text-bone transition-colors">Privacy</Link>
            <Link href="#" className="hover:text-bone transition-colors">Terms</Link>
            <Link href="#" className="hover:text-bone transition-colors">Status</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

function RoleCard({ icon, who, headline, bullets, cta, href }: { icon: React.ReactNode, who: string, headline: string, bullets: string[], cta: string, href: string }) {
  return (
    <div className="card p-8 flex flex-col gap-6 hover:border-ash/25 transition-colors">
      <div className="flex items-center gap-3">
        <div className="w-11 h-11 rounded-lg bg-basalt border border-surface-border flex items-center justify-center">{icon}</div>
        <span className="font-mono text-xs text-ash uppercase tracking-widest">{who}</span>
      </div>
      <h3 className="font-sans font-semibold text-xl text-bone">{headline}</h3>
      <ul className="flex flex-col gap-2.5">
        {bullets.map(b => (
          <li key={b} className="flex items-center gap-2.5 font-sans text-sm text-ash">
            <span className="w-1.5 h-1.5 rounded-full bg-seam-gold/60 shrink-0" />
            {b}
          </li>
        ))}
      </ul>
      <Link href={href} className="mt-auto">
        <Button variant="secondary" size="md" className="w-full justify-center">{cta}</Button>
      </Link>
    </div>
  );
}
