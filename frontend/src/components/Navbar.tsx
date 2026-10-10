'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { LogOut, Moon, ShieldCheck, Sun } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function Navbar() {
  const { user, tenant, logout } = useAuth();
  const router = useRouter();
  const [dark, setDark] = useState(true);

  useEffect(() => setDark(document.documentElement.classList.contains('dark')), []);

  function toggleTheme() {
    const next = !dark;
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('tenantai_theme', next ? 'dark' : 'light');
    setDark(next);
  }

  async function handleLogout() {
    await logout();
    router.push('/login');
  }

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur-md dark:border-white/10 dark:bg-slate-950/90">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        <Link href="/dashboard" className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-500 text-slate-950"><ShieldCheck className="h-5 w-5" /></div>
          <div>
            <div className="font-bold tracking-tight text-slate-900 dark:text-white">SaaSsum<span className="text-teal-500"> AI</span></div>
            <div className="text-[11px] text-slate-400">{tenant?.name || user?.tenant_name || 'Secure company workspace'}</div>
          </div>
        </Link>
        <div className="flex items-center gap-2">
          <button onClick={toggleTheme} className="rounded-lg border border-slate-200 p-2 text-slate-500 hover:text-teal-500 dark:border-white/10 dark:text-slate-300" aria-label="Toggle theme">
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          {user && <span className="hidden text-xs text-slate-500 sm:inline dark:text-slate-400">{user.email}</span>}
          <button onClick={handleLogout} className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:text-rose-500 dark:border-white/10 dark:text-slate-300">
            <LogOut className="h-3.5 w-3.5" /> Sign out
          </button>
        </div>
      </div>
    </header>
  );
}
