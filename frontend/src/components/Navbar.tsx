'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import {
  ShieldCheck,
  Building2,
  ChevronDown,
  LogOut,
  Sparkles,
  RefreshCw,
  User,
  ShieldAlert,
  ArrowRightLeft,
  CheckCircle2,
} from 'lucide-react';
import { api } from '@/lib/api';

export default function Navbar() {
  const { user, tenant, logout, demoAccounts, switchDemoAccount } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [demoModalOpen, setDemoModalOpen] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const handleSwitchAccount = async (email: string, pass: string) => {
    await switchDemoAccount(email, pass);
    setDemoModalOpen(false);
    router.refresh();
  };

  const handleResetSeed = async () => {
    setIsResetting(true);
    try {
      await api.demo.resetSeed();
      alert('Demo data successfully reseeded with clean state!');
      window.location.reload();
    } catch (e) {
      alert(`Error reseeding data: ${e}`);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur-md">
        <div className="flex h-16 items-center justify-between px-4 sm:px-6">
          {/* Brand & Workspace Indicator */}
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex items-center gap-2.5 group">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-600 text-white shadow-sm shadow-teal-500/20 group-hover:bg-teal-700 transition">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-slate-900 tracking-tight text-lg leading-none">
                    Tenant<span className="text-teal-600">AI</span>
                  </span>
                  <span className="rounded-full bg-teal-50 px-2 py-0.5 text-[10px] font-semibold text-teal-700 border border-teal-200/60 uppercase tracking-wider">
                    SaaS RAG
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">Secure Multi-Tenant Platform</span>
              </div>
            </Link>

            {/* Current Workspace Pill */}
            {user && (
              <div className="hidden md:flex items-center gap-2 pl-4 border-l border-slate-200">
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 shadow-2xs">
                  <Building2 className="h-3.5 w-3.5 text-teal-600" />
                  <span className="font-medium text-slate-500">Workspace:</span>
                  <span className="font-semibold text-slate-900">
                    {tenant?.name || user.tenant_name || 'Global Admin'}
                  </span>
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                </div>
              </div>
            )}
          </div>

          {/* Center: Live Isolation Status */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200/80 text-emerald-800 text-xs font-medium">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
            <span>Cryptographic Tenant Isolation Active</span>
          </div>

          {/* Right Action Controls */}
          <div className="flex items-center gap-3">
            {/* Quick Demo Switcher Button for Jury */}
            <button
              onClick={() => setDemoModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-50 border border-teal-200 text-teal-700 hover:bg-teal-100 text-xs font-semibold transition shadow-2xs cursor-pointer"
              title="Switch demo workspace for live evaluation"
            >
              <ArrowRightLeft className="h-3.5 w-3.5 text-teal-600" />
              <span>Demo Personas</span>
            </button>

            {/* User Profile Dropdown */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg hover:bg-slate-100 text-left transition border border-transparent hover:border-slate-200 cursor-pointer"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-tr from-teal-600 to-emerald-500 text-white font-semibold text-xs shadow-2xs">
                    {user.full_name?.charAt(0) || 'U'}
                  </div>
                  <div className="hidden sm:flex flex-col text-xs">
                    <span className="font-semibold text-slate-900 line-clamp-1 leading-snug">
                      {user.full_name}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {user.role}
                    </span>
                  </div>
                  <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
                </button>

                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 rounded-xl bg-white p-1.5 shadow-xl border border-slate-200 text-xs z-50">
                    <div className="px-3 py-2 border-b border-slate-100 mb-1">
                      <p className="font-semibold text-slate-900">{user.full_name}</p>
                      <p className="text-slate-500 text-[11px] truncate">{user.email}</p>
                      <div className="mt-1 flex items-center gap-1">
                        <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700">
                          {user.role}
                        </span>
                        <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-teal-50 text-teal-700">
                          {tenant?.slug || 'admin'}
                        </span>
                      </div>
                    </div>

                    <Link
                      href="/settings"
                      onClick={() => setDropdownOpen(false)}
                      className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 transition"
                    >
                      <User className="h-3.5 w-3.5 text-slate-400" />
                      <span>Workspace Settings</span>
                    </Link>

                    <button
                      onClick={handleResetSeed}
                      disabled={isResetting}
                      className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-slate-700 hover:bg-slate-50 transition text-left cursor-pointer"
                    >
                      <RefreshCw className={`h-3.5 w-3.5 text-slate-400 ${isResetting ? 'animate-spin' : ''}`} />
                      <span>{isResetting ? 'Resetting...' : 'Reset Demo Seed'}</span>
                    </button>

                    <div className="border-t border-slate-100 my-1"></div>

                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-rose-600 hover:bg-rose-50 transition font-medium cursor-pointer"
                    >
                      <LogOut className="h-3.5 w-3.5" />
                      <span>Sign out</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                href="/login"
                className="px-4 py-2 rounded-lg bg-teal-600 text-white text-xs font-semibold hover:bg-teal-700 transition shadow-sm"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Demo Personas Modal for Live Jury Switching */}
      {demoModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-teal-600" />
                <h3 className="font-bold text-slate-900 text-base">Jury Demo Workspace Switcher</h3>
              </div>
              <button
                onClick={() => setDemoModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-sm font-semibold p-1"
              >
                ✕
              </button>
            </div>

            <p className="mt-3 text-xs text-slate-500 leading-relaxed">
              Instantly toggle between isolated tenant company workspaces to test strict cross-tenant RAG isolation.
            </p>

            <div className="mt-4 space-y-2.5">
              {demoAccounts.map((acc) => {
                const isCurrent = user?.email === acc.email;
                return (
                  <div
                    key={acc.email}
                    onClick={() => handleSwitchAccount(acc.email, acc.password)}
                    className={`flex items-start justify-between p-3.5 rounded-xl border transition cursor-pointer ${
                      isCurrent
                        ? 'border-teal-500 bg-teal-50/60 ring-2 ring-teal-500/20'
                        : 'border-slate-200 hover:border-teal-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-900 text-sm">{acc.company}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-medium bg-slate-100 text-slate-700">
                          {acc.badge}
                        </span>
                      </div>
                      <span className="text-xs text-slate-500 mt-0.5">{acc.email}</span>
                      <span className="text-[11px] text-teal-700 mt-1 font-medium">
                        Docs: {acc.sample_document}
                      </span>
                    </div>

                    <div className="flex flex-col items-end gap-1">
                      {isCurrent ? (
                        <span className="text-xs font-bold text-teal-600 flex items-center gap-1">
                          <CheckCircle2 className="h-4 w-4" /> Active
                        </span>
                      ) : (
                        <span className="text-xs font-semibold text-slate-600 bg-white border border-slate-200 px-2.5 py-1 rounded-md shadow-2xs hover:bg-teal-600 hover:text-white transition">
                          Switch
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-5 pt-4 border-t border-slate-100 flex justify-between items-center text-xs">
              <span className="text-slate-400">All passwords: DemoPass123!</span>
              <button
                onClick={() => setDemoModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-slate-100 text-slate-700 font-medium hover:bg-slate-200 transition cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
