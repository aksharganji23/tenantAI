'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import {
  ShieldCheck,
  Building2,
  Lock,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  FileText,
  KeyRound,
} from 'lucide-react';

export default function LoginPage() {
  const { login, demoAccounts, switchDemoAccount } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Invalid credentials. Please verify your email and password.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (accEmail: string, accPass: string) => {
    setError(null);
    setLoading(true);
    try {
      await switchDemoAccount(accEmail, accPass);
      router.push('/dashboard');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Quick login failed.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-slate-100/50 to-white flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Top Hackathon Banner */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center mb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-50 border border-teal-200/80 text-teal-800 text-xs font-semibold mb-4 shadow-2xs">
          <Sparkles className="h-3.5 w-3.5 text-teal-600" />
          <span>TriCity AI Hackathon — SaaSsum AI (IT & AI)</span>
        </div>

        <div className="flex items-center justify-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-600 text-white shadow-lg shadow-teal-600/30">
            <ShieldCheck className="h-7 w-7" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
            Tenant<span className="text-teal-600">AI</span>
          </h1>
        </div>

        <p className="mt-2 text-sm text-slate-600 max-w-sm mx-auto">
          Secure Multi-Tenant AI Chatbot Platform with Isolated Knowledge Retrival & Audit Telemetry
        </p>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-4xl px-4">
        {/* Hackathon Jury 1-Click Fast-Track Persona Selectors */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-3 px-1">
            <div className="flex items-center gap-2">
              <KeyRound className="h-4 w-4 text-teal-600" />
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Hackathon Jury 1-Click Fast-Track Switchers
              </h2>
            </div>
            <span className="text-xs text-slate-500">Click any card for instant authenticated login</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* TechNova Solutions */}
            <div
              onClick={() => handleQuickLogin('admin@technova.com', 'DemoPass123!')}
              className="group relative rounded-2xl bg-white p-5 border-2 border-slate-200 hover:border-teal-500 hover:shadow-lg transition cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                    <Building2 className="h-3 w-3" /> Company A
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">Tenant ID: 1</span>
                </div>
                <h3 className="font-bold text-slate-900 text-base group-hover:text-teal-600 transition">
                  TechNova Solutions
                </h3>
                <p className="text-xs text-slate-500 mt-1">IT & Hardware Corporation</p>

                <div className="mt-3 p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-[11px] text-slate-600 space-y-1">
                  <div className="flex items-center gap-1.5 font-medium text-slate-700">
                    <FileText className="h-3 w-3 text-teal-600 shrink-0" />
                    <span className="truncate">UltraBook Pro Hardware Manual</span>
                  </div>
                  <div className="text-[10px] text-slate-400">
                    User: <code className="text-slate-600">admin@technova.com</code>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-teal-600 group-hover:text-teal-700">
                <span>Enter Workspace</span>
                <ArrowRight className="h-4 w-4 transform group-hover:translate-x-1 transition" />
              </div>
            </div>

            {/* GreenLeaf Retail */}
            <div
              onClick={() => handleQuickLogin('admin@greenleaf.com', 'DemoPass123!')}
              className="group relative rounded-2xl bg-white p-5 border-2 border-slate-200 hover:border-emerald-500 hover:shadow-lg transition cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <Building2 className="h-3 w-3" /> Company B
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">Tenant ID: 2</span>
                </div>
                <h3 className="font-bold text-slate-900 text-base group-hover:text-emerald-600 transition">
                  GreenLeaf Retail
                </h3>
                <p className="text-xs text-slate-500 mt-1">E-Commerce & Retail Network</p>

                <div className="mt-3 p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-[11px] text-slate-600 space-y-1">
                  <div className="flex items-center gap-1.5 font-medium text-slate-700">
                    <FileText className="h-3 w-3 text-emerald-600 shrink-0" />
                    <span className="truncate">Retail 30-Day Refund Policy</span>
                  </div>
                  <div className="text-[10px] text-slate-400">
                    User: <code className="text-slate-600">admin@greenleaf.com</code>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-emerald-600 group-hover:text-emerald-700">
                <span>Enter Workspace</span>
                <ArrowRight className="h-4 w-4 transform group-hover:translate-x-1 transition" />
              </div>
            </div>

            {/* Platform SuperAdmin */}
            <div
              onClick={() => handleQuickLogin('admin@tenantai.com', 'SuperAdmin123!')}
              className="group relative rounded-2xl bg-white p-5 border-2 border-slate-200 hover:border-purple-500 hover:shadow-lg transition cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
                    <ShieldCheck className="h-3 w-3" /> Platform Root
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">SuperAdmin</span>
                </div>
                <h3 className="font-bold text-slate-900 text-base group-hover:text-purple-600 transition">
                  System Administrator
                </h3>
                <p className="text-xs text-slate-500 mt-1">Platform-Wide Governance</p>

                <div className="mt-3 p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-[11px] text-slate-600 space-y-1">
                  <div className="flex items-center gap-1.5 font-medium text-slate-700">
                    <Lock className="h-3 w-3 text-purple-600 shrink-0" />
                    <span className="truncate">Full Telemetry & Quota Control</span>
                  </div>
                  <div className="text-[10px] text-slate-400">
                    User: <code className="text-slate-600">admin@tenantai.com</code>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-purple-600 group-hover:text-purple-700">
                <span>Open Admin Portal</span>
                <ArrowRight className="h-4 w-4 transform group-hover:translate-x-1 transition" />
              </div>
            </div>
          </div>
        </div>

        {/* Standard Manual Login Card */}
        <div className="max-w-md mx-auto bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-900">Custom Credentials Login</h3>
            <p className="text-xs text-slate-500">Sign in with custom tenant credentials</p>
          </div>

          {error && (
            <div className="mb-4 rounded-xl bg-rose-50 p-3 border border-rose-200 flex items-start gap-2.5 text-xs text-rose-700">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Company Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 outline-none transition"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 outline-none transition"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-sm shadow-sm transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign in to Workspace</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
            <span className="flex items-center gap-1">
              <Lock className="h-3 w-3 text-emerald-600" />
              SHA-256 JWT Authorization
            </span>
            <span>Version 1.0.0</span>
          </div>
        </div>
      </div>
    </div>
  );
}
