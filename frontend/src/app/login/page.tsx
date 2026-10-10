'use client';

import { FormEvent, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowRight, LockKeyhole, ShieldCheck, Sparkles } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[var(--background)] px-6 py-12 text-[var(--foreground)]">
      <div className="mx-auto flex min-h-[80vh] max-w-md flex-col justify-center">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-500 text-slate-950 shadow-lg shadow-teal-500/20">
            <ShieldCheck className="h-7 w-7" />
          </div>
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-teal-400/20 bg-teal-400/10 px-3 py-1 text-xs font-semibold text-teal-300">
            <Sparkles className="h-3.5 w-3.5" /> SaaSsum AI
          </div>
          <h1 className="text-3xl font-black tracking-tight">Welcome back</h1>
          <p className="mt-2 text-sm text-slate-400">Sign in to your verified company workspace.</p>
        </div>

        <form onSubmit={handleSubmit} className="surface-card space-y-5 p-7">
          {error && <p className="rounded-xl border border-rose-400/30 bg-rose-400/10 p-3 text-sm text-rose-300">{error}</p>}
          <label className="block text-sm font-medium text-slate-300">
            Work email
            <input className="field mt-2" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label className="block text-sm font-medium text-slate-300">
            Password
            <input className="field mt-2" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          <button className="primary-button w-full" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'} <ArrowRight className="h-4 w-4" />
          </button>
          <div className="flex items-center justify-between border-t border-white/10 pt-4 text-xs text-slate-500">
            <span className="flex items-center gap-1.5"><LockKeyhole className="h-3.5 w-3.5 text-teal-400" /> Tenant-scoped access</span>
            <Link className="font-semibold text-teal-300 hover:text-teal-200" href="/register">Create company</Link>
          </div>
        </form>
      </div>
    </main>
  );
}
