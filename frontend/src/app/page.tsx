'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import {
  ArrowRight,
  CheckCircle2,
  FileCheck2,
  LockKeyhole,
  Menu,
  MessageSquareText,
  ShieldCheck,
  X,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function Home() {
  const { user, loading } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [cookieVisible, setCookieVisible] = useState(false);

  useEffect(() => {
    setCookieVisible(localStorage.getItem('tenantai_cookie_consent') !== 'accepted');
  }, []);

  function acceptCookies() {
    localStorage.setItem('tenantai_cookie_consent', 'accepted');
    setCookieVisible(false);
  }

  return (
    <main className="min-h-screen overflow-hidden bg-[var(--background)] text-[var(--foreground)]">
      <header className="relative z-20 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8" aria-label="Main navigation">
          <Link href="/" className="flex items-center gap-3" aria-label="tenantAI home">
            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-teal-400 text-slate-950 shadow-lg shadow-teal-400/20">
              <ShieldCheck className="h-6 w-6" aria-hidden="true" />
            </span>
            <span className="text-lg font-black tracking-tight">tenant<span className="text-teal-300">AI</span></span>
          </Link>
          <div className="hidden items-center gap-7 text-sm text-slate-300 md:flex">
            <a href="#features" className="transition-colors hover:text-teal-300">Features</a>
            <a href="#security" className="transition-colors hover:text-teal-300">Security</a>
            <Link href="/privacy" className="transition-colors hover:text-teal-300">Privacy</Link>
            <Link href="/login" className="rounded-lg px-3 py-2 font-semibold hover:text-teal-300">Sign in</Link>
            <Link href="/register" className="primary-button px-4 py-2">Create workspace <ArrowRight className="h-4 w-4" aria-hidden="true" /></Link>
          </div>
          <button
            type="button"
            className="rounded-lg border border-white/10 p-2 text-slate-200 md:hidden"
            aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
          </button>
        </nav>
        {menuOpen && (
          <div className="mx-6 mb-4 grid gap-2 rounded-2xl border border-white/10 bg-slate-900 p-4 md:hidden">
            <a href="#features" onClick={() => setMenuOpen(false)} className="rounded-lg p-3 hover:bg-white/5">Features</a>
            <a href="#security" onClick={() => setMenuOpen(false)} className="rounded-lg p-3 hover:bg-white/5">Security</a>
            <Link href="/privacy" className="rounded-lg p-3 hover:bg-white/5">Privacy policy</Link>
            <Link href="/login" className="rounded-lg p-3 hover:bg-white/5">Sign in</Link>
            <Link href="/register" className="primary-button">Create workspace <ArrowRight className="h-4 w-4" aria-hidden="true" /></Link>
          </div>
        )}
      </header>

      <section className="relative isolate">
        <div className="hero-grid pointer-events-none absolute inset-0 -z-10 opacity-60" aria-hidden="true" />
        <div className="mx-auto grid max-w-7xl gap-14 px-6 pb-24 pt-20 lg:grid-cols-[1.05fr_.95fr] lg:items-center lg:px-8 lg:pb-32 lg:pt-28">
          <div className="animate-fade-up">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-teal-300/20 bg-teal-300/10 px-4 py-2 text-xs font-bold uppercase tracking-[.18em] text-teal-200">
              <span className="h-2 w-2 rounded-full bg-emerald-400 security-pulse" aria-hidden="true" /> Secure AI for every workspace
            </div>
            <h1 className="max-w-3xl text-5xl font-black leading-[1.02] tracking-tight text-white sm:text-6xl lg:text-7xl">
              Answers your teams can <span className="text-teal-300">trust.</span>
            </h1>
            <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-300">
              tenantAI gives every company a private, document-grounded chatbot with citations,
              audit-ready telemetry, and isolation built into every query.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link href={user && !loading ? '/dashboard' : '/register'} className="primary-button px-6 py-3.5">
                {user && !loading ? 'Open workspace' : 'Start free workspace'} <ArrowRight className="h-5 w-5" aria-hidden="true" />
              </Link>
              <Link href="/login" className="secondary-button px-6 py-3.5">Sign in to your workspace</Link>
            </div>
            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-slate-400">
              <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-teal-300" aria-hidden="true" /> Tenant-isolated by design</span>
              <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-teal-300" aria-hidden="true" /> Grounded citations</span>
            </div>
          </div>
          <div className="animate-fade-up-delay surface-card relative overflow-hidden p-5 sm:p-7" aria-label="Product preview">
            <div className="mb-6 flex items-center justify-between border-b border-white/10 pb-4">
              <div><p className="text-sm font-bold text-white">Workspace intelligence</p><p className="text-xs text-slate-400">Acme Operations · Protected</p></div>
              <LockKeyhole className="h-5 w-5 text-teal-300" aria-hidden="true" />
            </div>
            <div className="space-y-4">
              <div className="rounded-2xl bg-white/5 p-4"><p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Question</p><p className="mt-2 text-sm text-white">What is our customer refund window?</p></div>
              <div className="rounded-2xl border border-teal-300/20 bg-teal-300/10 p-4"><p className="text-xs font-semibold uppercase tracking-wider text-teal-200">Grounded answer</p><p className="mt-2 text-sm leading-6 text-slate-100">Eligible purchases can be returned within 30 days with a valid receipt.</p><p className="mt-3 text-xs text-teal-200">Source · Customer Refund Policy · Page 1</p></div>
              <div className="grid grid-cols-3 gap-3 text-center text-xs"><div className="rounded-xl bg-white/5 p-3"><p className="text-lg font-black text-white">24</p><p className="text-slate-400">Documents</p></div><div className="rounded-xl bg-white/5 p-3"><p className="text-lg font-black text-white">99.9%</p><p className="text-slate-400">Isolated</p></div><div className="rounded-xl bg-white/5 p-3"><p className="text-lg font-black text-white">Live</p><p className="text-slate-400">Audit trail</p></div></div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl scroll-mt-20 px-6 py-20 lg:px-8">
        <div className="max-w-2xl"><p className="text-sm font-bold uppercase tracking-[.18em] text-teal-300">One secure workspace</p><h2 className="mt-3 text-3xl font-black tracking-tight text-white sm:text-4xl">Move from scattered files to confident answers.</h2></div>
        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {[
            [FileCheck2, 'Document-grounded chat', 'Upload company knowledge and get concise answers with source citations.'],
            [ShieldCheck, 'Tenant isolation', 'Every document, conversation, and retrieval query stays inside its company workspace.'],
            [MessageSquareText, 'Audit-ready telemetry', 'See activity, usage, and security events in one transparent operational trail.'],
          ].map(([Icon, title, description]) => (
            <article key={title as string} className="surface-card transition-transform duration-300 hover:-translate-y-1">
              <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-teal-300/10 text-teal-300"><Icon className="h-5 w-5" aria-hidden="true" /></div>
              <h3 className="text-lg font-bold text-white">{title as string}</h3><p className="mt-3 text-sm leading-6 text-slate-400">{description as string}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="security" className="border-y border-white/10 bg-slate-950/40 px-6 py-20 text-center">
        <div className="mx-auto max-w-3xl"><LockKeyhole className="mx-auto h-9 w-9 text-teal-300" aria-hidden="true" /><h2 className="mt-5 text-3xl font-black text-white">Private by default. Clear by design.</h2><p className="mt-4 leading-7 text-slate-400">Verified access, scoped retrieval, citations, and an audit trail give your team the confidence to use AI with sensitive company knowledge.</p><Link href="/register" className="primary-button mt-8 px-6 py-3.5">Create your workspace <ArrowRight className="h-5 w-5" aria-hidden="true" /></Link></div>
      </section>

      <footer className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">
        <p>© 2026 tenantAI. Secure company intelligence.</p>
        <div className="flex gap-5"><Link href="/privacy" className="hover:text-teal-300">Privacy policy</Link><Link href="/terms" className="hover:text-teal-300">Terms &amp; conditions</Link></div>
      </footer>

      {cookieVisible && (
        <aside className="fixed inset-x-4 bottom-4 z-50 mx-auto max-w-3xl rounded-2xl border border-white/15 bg-slate-900/95 p-5 shadow-2xl backdrop-blur-xl" aria-label="Cookie consent">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div><h2 className="font-bold text-white">Your privacy matters</h2><p className="mt-1 text-sm leading-6 text-slate-300">We use essential local storage for sign-in, theme preferences, and this consent choice. Read our <Link href="/privacy" className="text-teal-300 underline">privacy policy</Link>.</p></div><button type="button" onClick={acceptCookies} className="primary-button shrink-0 px-5 py-2.5">Accept essential cookies</button></div>
        </aside>
      )}
    </main>
  );
}
