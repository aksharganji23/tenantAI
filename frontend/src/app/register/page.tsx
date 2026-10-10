'use client';

import { FormEvent, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowRight, Building2, ShieldCheck } from 'lucide-react';
import { api } from '@/lib/api';

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ company_name: '', company_slug: '', full_name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.auth.register(form);
      router.push(`/verify-email?email=${encodeURIComponent(form.email)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create the company.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[var(--background)] px-6 py-12 text-[var(--foreground)]">
      <div className="mx-auto max-w-lg">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-500 text-slate-950"><ShieldCheck /></div>
          <h1 className="text-3xl font-black">Create your workspace</h1>
          <p className="mt-2 text-sm text-slate-400">Your administrator email will be verified with a five-minute OTP.</p>
        </div>
        <form onSubmit={submit} className="surface-card space-y-4 p-7">
          {error && <p className="rounded-xl border border-rose-400/30 bg-rose-400/10 p-3 text-sm text-rose-300">{error}</p>}
          {[
            ['company_name', 'Company name', 'Acme Inc.'],
            ['company_slug', 'Company URL slug', 'acme-inc'],
            ['full_name', 'Administrator name', 'Alex Morgan'],
            ['email', 'Administrator email', 'alex@acme.com'],
          ].map(([key, label, placeholder]) => (
            <label key={key} className="block text-sm font-medium text-slate-300">
              {label}
              <input className="field mt-2" required type={key === 'email' ? 'email' : 'text'} placeholder={placeholder}
                value={form[key as keyof typeof form]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
            </label>
          ))}
          <label className="block text-sm font-medium text-slate-300">Password
            <input className="field mt-2" required minLength={8} type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </label>
          <button className="primary-button w-full" disabled={loading}>{loading ? 'Creating…' : 'Create company'} <ArrowRight className="h-4 w-4" /></button>
          <Link href="/login" className="flex items-center justify-center gap-2 text-sm text-slate-400 hover:text-teal-300"><Building2 className="h-4 w-4" /> Back to sign in</Link>
        </form>
      </div>
    </main>
  );
}
