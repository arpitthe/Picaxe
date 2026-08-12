'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useToast } from '@/components/ui/Toast';
import {
  Shield, Activity, Users, Database, Search, LayoutGrid,
  Filter, TrendingUp, CheckCircle2, AlertCircle, Settings, X
} from 'lucide-react';

// ─── Types & Data ─────────────────────────────────────────────────────────────

type AdminSection = 'overview' | 'events' | 'organizations' | 'queues' | 'audit';

const METRICS = [
  { label: 'Global Match Rate', value: '84.2%', trend: '+2.1%', positive: true },
  { label: 'Media Processed (30d)', value: '1.24M', trend: undefined, positive: true },
  { label: 'Manual Corrections', value: '1.4%', trend: '-0.3%', positive: true },
  { label: 'Active GPU Workers', value: '12', trend: undefined, positive: true },
];

const LOGS = [
  { time: '10:42:01', actor: 'admin_77', type: 'admin', action: 'OVERRIDE_MATCH', target: 'photo_823', reason: 'False positive on obscured face' },
  { time: '10:15:33', actor: 'org_nyu', type: 'org', action: 'EVENT_CREATED', target: 'event_402', reason: '—' },
  { time: '09:55:12', actor: 'admin_77', type: 'admin', action: 'DELETE_PROFILE', target: 'student_901', reason: 'Data privacy request (GDPR)' },
  { time: '09:12:00', actor: 'system', type: 'system', action: 'BATCH_COMPLETE', target: 'batch_77', reason: 'Processed 4,200 items in 12s' },
  { time: '09:10:11', actor: 'org_stanford', type: 'org', action: 'BATCH_UPLOAD', target: 'batch_77', reason: '—' },
  { time: '08:44:22', actor: 'system', type: 'system', action: 'WORKER_SCALE', target: 'gpu_pool', reason: 'Scale down to 4 nodes (idle window)' },
];

const EVENTS_DATA = [
  { id: 'e1', title: 'Engineering Hackathon', org: 'org_nyu', date: 'Aug 8, 2026', media: 1450, matches: 890, status: 'done' },
  { id: 'e2', title: 'Alumni Dinner 2026', org: 'org_stanford', date: 'Aug 5, 2026', media: 320, matches: 210, status: 'review' },
  { id: 'e3', title: 'Convocation 2026', org: 'org_nyu', date: 'Processing...', media: 4200, matches: 0, status: 'processing' },
  { id: 'e4', title: 'Freshman Orientation', org: 'org_mit', date: 'Jul 28, 2026', media: 890, matches: 670, status: 'done' },
];

const ORGS_DATA = [
  { id: 'o1', name: 'NYU', handle: 'org_nyu', events: 12, students: 3200, plan: 'Enterprise', status: 'active' },
  { id: 'o2', name: 'Stanford University', handle: 'org_stanford', events: 8, students: 2100, plan: 'Pro', status: 'active' },
  { id: 'o3', name: 'MIT', handle: 'org_mit', events: 5, students: 1450, plan: 'Enterprise', status: 'active' },
  { id: 'o4', name: 'Columbia University', handle: 'org_columbia', events: 3, students: 890, plan: 'Starter', status: 'pending' },
];

const QUEUES_DATA = [
  { id: 'q1', name: 'batch_77 — Convocation 2026', org: 'org_nyu', items: 4200, processed: 3100, status: 'running', workers: 4 },
  { id: 'q2', name: 'batch_78 — Alumni Dinner', org: 'org_stanford', items: 320, processed: 320, status: 'complete', workers: 0 },
  { id: 'q3', name: 'batch_79 — Orientation', org: 'org_mit', items: 890, processed: 890, status: 'complete', workers: 0 },
];

// ─── Section Components ───────────────────────────────────────────────────────

function OverviewSection() {
  const [filter, setFilter] = useState('');
  const filtered = LOGS.filter(l =>
    !filter ||
    l.action.includes(filter.toUpperCase()) ||
    l.actor.includes(filter)
  );

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="font-sans font-semibold text-xl text-bone">Overview</h1>
        <Badge variant="success" dot pulse>System Healthy</Badge>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {METRICS.map(m => (
          <div key={m.label} className="card p-5">
            <p className="font-mono text-[10px] text-ash uppercase tracking-wide mb-3">{m.label}</p>
            <div className="flex items-end justify-between">
              <p className="font-sans font-semibold text-2xl text-bone">{m.value}</p>
              {m.trend && (
                <span className={`font-mono text-xs flex items-center gap-0.5 ${m.positive ? 'text-verdigris' : 'text-danger'}`}>
                  <TrendingUp className="w-3 h-3" /> {m.trend}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Audit Logs */}
      <section className="card flex flex-col overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-surface-border shrink-0">
          <h2 className="font-sans font-medium text-bone">Audit Logs</h2>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-basalt border border-surface-border rounded-md px-2.5 py-1.5 focus-within:border-seam-gold/50 transition-colors">
              <Filter className="w-3.5 h-3.5 text-ash" />
              <input
                type="text"
                placeholder="Filter..."
                value={filter}
                onChange={e => setFilter(e.target.value)}
                className="bg-transparent text-xs font-mono text-bone outline-none w-32 placeholder-ash/40"
                aria-label="Filter audit logs"
              />
            </div>
            <Button variant="ghost" size="sm" className="font-mono text-xs text-ash">Export CSV</Button>
          </div>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-left font-mono text-[11px]" role="table" aria-label="System audit logs">
            <thead className="sticky top-0 bg-basalt border-b border-surface-border z-10">
              <tr>
                {['Timestamp', 'Actor', 'Action', 'Target', 'Reason'].map(h => (
                  <th key={h} className="px-4 py-2.5 font-medium text-ash uppercase tracking-wider text-[10px]" scope="col">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border">
              {filtered.map((log, i) => (
                <tr key={i} className="hover:bg-surface-50 transition-colors">
                  <td className="px-4 py-3 text-ash whitespace-nowrap">2026-03-14 {log.time}</td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span className={`flex items-center gap-1.5 ${log.type === 'admin' ? 'text-seam-gold' : log.type === 'system' ? 'text-ash' : 'text-bone'}`}>
                      {log.type === 'admin' ? <Shield className="w-3 h-3" /> : log.type === 'system' ? <Database className="w-3 h-3" /> : <Users className="w-3 h-3" />}
                      {log.actor}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 bg-basalt-50 border border-surface-border rounded-sm text-bone">{log.action}</span>
                  </td>
                  <td className="px-4 py-3 text-ash">{log.target}</td>
                  <td className="px-4 py-3 text-ash/70 max-w-[220px] truncate">{log.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function EventsSection() {
  const [search, setSearch] = useState('');
  const filtered = EVENTS_DATA.filter(e =>
    e.title.toLowerCase().includes(search.toLowerCase()) ||
    e.org.includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="font-sans font-semibold text-xl text-bone">Events</h1>
        <span className="font-mono text-xs text-ash">{EVENTS_DATA.length} total</span>
      </div>

      <div className="flex items-center gap-2 bg-surface border border-surface-border rounded-md px-3 py-2 max-w-sm focus-within:border-seam-gold/50 transition-colors">
        <Search className="w-3.5 h-3.5 text-ash shrink-0" />
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search events or organizations..."
          className="bg-transparent text-sm text-bone font-sans outline-none w-full placeholder-ash/40"
        />
      </div>

      <div className="flex flex-col gap-3">
        {filtered.map(ev => (
          <div key={ev.id} className="card p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-sans font-medium text-bone">{ev.title}</h3>
                <Badge variant={ev.status === 'done' ? 'success' : ev.status === 'review' ? 'warning' : 'info'} dot>
                  {ev.status === 'done' ? 'Processed' : ev.status === 'review' ? 'Review' : 'Processing'}
                </Badge>
              </div>
              <p className="font-mono text-[10px] text-ash">{ev.org} · {ev.date} · {ev.media.toLocaleString()} files · {ev.matches.toLocaleString()} matches</p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button variant="ghost" size="sm">View Details</Button>
              <Button variant="danger" size="sm">Delete</Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function OrganizationsSection() {
  const { toast } = useToast();
  const [search, setSearch] = useState('');
  const filtered = ORGS_DATA.filter(o =>
    o.name.toLowerCase().includes(search.toLowerCase()) ||
    o.handle.includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="font-sans font-semibold text-xl text-bone">Organizations</h1>
        <span className="font-mono text-xs text-ash">{ORGS_DATA.length} registered</span>
      </div>

      <div className="flex items-center gap-2 bg-surface border border-surface-border rounded-md px-3 py-2 max-w-sm focus-within:border-seam-gold/50 transition-colors">
        <Search className="w-3.5 h-3.5 text-ash shrink-0" />
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search organizations..."
          className="bg-transparent text-sm text-bone font-sans outline-none w-full placeholder-ash/40"
        />
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left" role="table">
          <thead className="bg-basalt border-b border-surface-border">
            <tr>
              {['Organization', 'Handle', 'Events', 'Students', 'Plan', 'Status', ''].map(h => (
                <th key={h} className="px-4 py-3 font-mono text-[10px] text-ash uppercase tracking-wider" scope="col">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border">
            {filtered.map(org => (
              <tr key={org.id} className="hover:bg-surface-50 transition-colors">
                <td className="px-4 py-3 font-sans text-sm text-bone font-medium">{org.name}</td>
                <td className="px-4 py-3 font-mono text-xs text-ash">{org.handle}</td>
                <td className="px-4 py-3 font-mono text-xs text-bone">{org.events}</td>
                <td className="px-4 py-3 font-mono text-xs text-bone">{org.students.toLocaleString()}</td>
                <td className="px-4 py-3">
                  <span className="font-mono text-[10px] px-2 py-0.5 bg-basalt border border-surface-border rounded-sm text-ash">{org.plan}</span>
                </td>
                <td className="px-4 py-3">
                  <Badge variant={org.status === 'active' ? 'success' : 'warning'} dot>
                    {org.status === 'active' ? 'Active' : 'Pending'}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={<Settings className="w-3.5 h-3.5" />}
                    onClick={() => toast({ type: 'info', title: `Managing ${org.name}`, description: 'Opening organization settings.' })}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function QueuesSection() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="font-sans font-semibold text-xl text-bone">Processing Queues</h1>
        <Badge variant="info" dot pulse>1 Running</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-2">
        {[
          { label: 'Active Workers', value: '4' },
          { label: 'Jobs Today', value: '3' },
          { label: 'Avg Time/Batch', value: '12s' },
        ].map(m => (
          <div key={m.label} className="card p-5">
            <p className="font-mono text-[10px] text-ash uppercase tracking-wide mb-2">{m.label}</p>
            <p className="font-sans font-semibold text-2xl text-bone">{m.value}</p>
          </div>
        ))}
      </div>

      <div className="flex flex-col gap-3">
        {QUEUES_DATA.map(q => {
          const pct = Math.round((q.processed / q.items) * 100);
          return (
            <div key={q.id} className="card p-5">
              <div className="flex items-start justify-between mb-3 gap-4">
                <div>
                  <p className="font-sans font-medium text-bone text-sm">{q.name}</p>
                  <p className="font-mono text-[10px] text-ash mt-0.5">{q.org} · {q.workers} workers active</p>
                </div>
                <Badge
                  variant={q.status === 'running' ? 'info' : 'success'}
                  dot
                  pulse={q.status === 'running'}
                >
                  {q.status === 'running' ? 'Running' : 'Complete'}
                </Badge>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-1.5 bg-basalt rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${q.status === 'complete' ? 'bg-verdigris' : 'bg-seam-gold'}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="font-mono text-[10px] text-ash shrink-0">
                  {q.processed.toLocaleString()} / {q.items.toLocaleString()} ({pct}%)
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function AuditSection() {
  const [filter, setFilter] = useState('');
  const filtered = LOGS.filter(l =>
    !filter ||
    l.action.includes(filter.toUpperCase()) ||
    l.actor.includes(filter) ||
    l.reason.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="font-sans font-semibold text-xl text-bone">Audit Logs</h1>
        <Button variant="ghost" size="sm" className="font-mono text-xs text-ash">Export CSV</Button>
      </div>

      <div className="flex items-center gap-2 bg-surface border border-surface-border rounded-md px-3 py-2 max-w-sm focus-within:border-seam-gold/50 transition-colors">
        <Search className="w-3.5 h-3.5 text-ash shrink-0" />
        <input
          type="text"
          value={filter}
          onChange={e => setFilter(e.target.value)}
          placeholder="Search logs..."
          className="bg-transparent text-sm text-bone font-sans outline-none w-full placeholder-ash/40"
        />
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left font-mono text-[11px]" role="table" aria-label="Full audit logs">
          <thead className="bg-basalt border-b border-surface-border">
            <tr>
              {['Timestamp', 'Actor', 'Action', 'Target', 'Reason'].map(h => (
                <th key={h} className="px-4 py-2.5 font-medium text-ash uppercase tracking-wider text-[10px]" scope="col">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border">
            {filtered.map((log, i) => (
              <tr key={i} className="hover:bg-surface-50 transition-colors">
                <td className="px-4 py-3 text-ash whitespace-nowrap">2026-03-14 {log.time}</td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`flex items-center gap-1.5 ${log.type === 'admin' ? 'text-seam-gold' : log.type === 'system' ? 'text-ash' : 'text-bone'}`}>
                    {log.type === 'admin' ? <Shield className="w-3 h-3" /> : log.type === 'system' ? <Database className="w-3 h-3" /> : <Users className="w-3 h-3" />}
                    {log.actor}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 bg-basalt-50 border border-surface-border rounded-sm text-bone">{log.action}</span>
                </td>
                <td className="px-4 py-3 text-ash">{log.target}</td>
                <td className="px-4 py-3 text-ash/70 max-w-[220px] truncate">{log.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── Nav config ───────────────────────────────────────────────────────────────

const NAV: { id: AdminSection; icon: React.ElementType; label: string; count?: number }[] = [
  { id: 'overview',      icon: Activity,    label: 'Overview' },
  { id: 'events',        icon: LayoutGrid,  label: 'Events',        count: EVENTS_DATA.length },
  { id: 'organizations', icon: Users,       label: 'Organizations', count: ORGS_DATA.length },
  { id: 'queues',        icon: Database,    label: 'Processing Queues' },
  { id: 'audit',         icon: Search,      label: 'Audit Logs' },
];

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function AdminDashboard() {
  const [activeSection, setActiveSection] = useState<AdminSection>('overview');

  const sectionContent: Record<AdminSection, React.ReactNode> = {
    overview:      <OverviewSection />,
    events:        <EventsSection />,
    organizations: <OrganizationsSection />,
    queues:        <QueuesSection />,
    audit:         <AuditSection />,
  };

  return (
    <div className="min-h-dvh flex flex-col bg-basalt">
      <Navbar context="admin" />

      <div className="flex-1 flex flex-col md:flex-row">
        {/* Sidebar */}
        <aside className="hidden md:flex w-60 border-r border-surface-border flex-col p-3 gap-1 bg-basalt shrink-0">
          {NAV.map(item => {
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-md font-sans text-sm transition-all ${
                  isActive
                    ? 'bg-surface text-bone border border-surface-border'
                    : 'text-ash hover:bg-surface-50 hover:text-bone border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <item.icon className="w-4 h-4 shrink-0" />
                  {item.label}
                </div>
                {item.count != null && (
                  <span className="font-mono text-[9px] bg-basalt px-1.5 py-0.5 rounded-full border border-surface-border">{item.count}</span>
                )}
              </button>
            );
          })}

          <div className="mt-auto pt-4 border-t border-surface-border">
            <Link href="/" className="flex items-center gap-3 px-3 py-2 rounded-md text-ash hover:text-bone hover:bg-surface-50 transition-all font-sans text-sm">
              ← Back to Home
            </Link>
          </div>
        </aside>

        {/* Mobile nav */}
        <div className="flex md:hidden overflow-x-auto gap-1 p-2 border-b border-surface-border bg-basalt shrink-0">
          {NAV.map(item => {
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-sans text-xs whitespace-nowrap transition-all ${
                  isActive ? 'bg-surface text-bone border border-surface-border' : 'text-ash hover:bg-surface-50'
                }`}
              >
                <item.icon className="w-3.5 h-3.5 shrink-0" />
                {item.label}
              </button>
            );
          })}
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 md:p-8 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeSection}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.2 }}
            >
              {sectionContent[activeSection]}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}


