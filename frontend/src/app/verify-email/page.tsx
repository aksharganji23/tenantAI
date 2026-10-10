'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';

export default function VerifyEmailPage() {
  const router = useRouter();
  const [email, setEmail] = useState(() => (
    typeof window === 'undefined' ? '' : new URLSearchParams(window.location.search).get('email') || ''
  ));
  const [otp, setOtp] = useState('');
  const [seconds, setSeconds] = useState(300);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (seconds <= 0) return;
    const timer = window.setInterval(() => setSeconds((value) => value - 1), 1000);
    return () => window.clearInterval(timer);
  }, [seconds]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    try {
      await api.auth.verifyEmail(email, otp);
      router.push('/login?verified=1');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed.');
    }
  }

  async function resend() {
    setError('');
    try {
      await api.auth.resendVerification(email);
      setSeconds(300);
      setMessage('A new code was sent.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to resend the code.');
    }
  }

  return (
    <main className="min-h-screen bg-[var(--background)] px-6 py-12 text-[var(--foreground)]">
      <div className="mx-auto max-w-md">
        <form onSubmit={submit} className="surface-card space-y-5 p-7">
          <div><p className="text-sm font-semibold uppercase tracking-wider text-teal-300">Email verification</p><h1 className="mt-2 text-3xl font-black">Enter your OTP</h1><p className="mt-2 text-sm text-slate-400">The six-digit code expires in five minutes.</p></div>
          {message && <p className="rounded-xl border border-emerald-400/30 bg-emerald-400/10 p-3 text-sm text-emerald-300">{message}</p>}
          {error && <p className="rounded-xl border border-rose-400/30 bg-rose-400/10 p-3 text-sm text-rose-300">{error}</p>}
          <label className="block text-sm text-slate-300">Email<input className="field mt-2" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
          <label className="block text-sm text-slate-300">Verification code<input className="field mt-2 text-center text-2xl tracking-[0.5em]" inputMode="numeric" pattern="\d{6}" maxLength={6} required value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))} /></label>
          <p className="text-center text-sm text-slate-400">{seconds ? `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')} remaining` : 'Code expired'}</p>
          <button className="primary-button w-full" disabled={!seconds}>Verify email</button>
          <button type="button" onClick={resend} className="w-full text-sm font-semibold text-teal-300 hover:text-teal-200">Resend code</button>
          <Link href="/login" className="block text-center text-sm text-slate-500 hover:text-slate-300">Back to sign in</Link>
        </form>
      </div>
    </main>
  );
}
