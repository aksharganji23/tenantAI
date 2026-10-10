'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  Activity,
  Settings,
  Shield,
  Sparkles,
  Database,
  Lock,
} from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();
  const { user, tenant } = useAuth();

  const navItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      badge: null,
    },
    {
      name: 'AI Chatbot',
      href: '/chat',
      icon: MessageSquare,
      badge: 'RAG',
    },
    {
      name: 'Knowledge Docs',
      href: '/documents',
      icon: FileText,
      badge: tenant?.document_count !== undefined ? `${tenant.document_count}` : null,
    },
    {
      name: 'Audit & Telemetry',
      href: '/logs',
      icon: Activity,
      badge: null,
      adminOnly: true,
    },
    {
      name: 'Workspace Settings',
      href: '/settings',
      icon: Settings,
      badge: null,
    },
    {
      name: 'Platform Admin',
      href: '/admin',
      icon: Shield,
      badge: user?.role === 'superadmin' ? 'Root' : 'Admin',
      superOnly: true,
    },
    {
      name: 'Jury Demo Suite',
      href: '/demo',
      icon: Sparkles,
      badge: 'Live',
      highlight: true,
    },
  ].filter((item) =>
    (!item.adminOnly || user?.role === 'tenant_admin' || user?.role === 'superadmin') &&
    (!item.superOnly || user?.role === 'superadmin')
  );

  return (
    <aside className="w-64 border-r border-slate-200 bg-white flex flex-col shrink-0 min-h-[calc(100vh-4rem)]">
      {/* Workspace Identity Mini-Card */}
      <div className="p-4 border-b border-slate-100">
        <div className="rounded-xl bg-slate-50 p-3 border border-slate-200/80">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700 bg-teal-100/70 px-2 py-0.5 rounded">
              {tenant?.plan || 'Enterprise'} Plan
            </span>
            <span className="flex items-center gap-1 text-[10px] text-emerald-600 font-semibold">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              Isolated
            </span>
          </div>
          <h4 className="mt-2 text-sm font-bold text-slate-900 truncate">
            {tenant?.name || user?.tenant_name || 'System Workspace'}
          </h4>
          <p className="text-[11px] text-slate-500 truncate">
            {tenant?.domain || `${tenant?.slug || 'tenant'}.tenantai.io`}
          </p>

          <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-slate-600">
            <span>Doc Quota</span>
            <span className="font-semibold text-slate-800">
              {tenant?.document_count || 0} / {tenant?.quota_docs || 100}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition group ${
                isActive
                  ? 'bg-teal-600 text-white shadow-sm shadow-teal-600/20'
                  : item.highlight
                  ? 'text-teal-900 bg-teal-50/70 border border-teal-200/70 hover:bg-teal-100/70'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`h-4 w-4 transition ${
                    isActive
                      ? 'text-white'
                      : item.highlight
                      ? 'text-teal-600'
                      : 'text-slate-400 group-hover:text-slate-600'
                  }`}
                />
                <span>{item.name}</span>
              </div>

              {item.badge && (
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-semibold tracking-wide uppercase ${
                    isActive
                      ? 'bg-white/20 text-white'
                      : item.highlight
                      ? 'bg-teal-200 text-teal-800'
                      : 'bg-slate-200/70 text-slate-700'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Security Guarantee Footer Badge */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-start gap-2.5 text-[11px] text-slate-500">
          <Lock className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
          <div className="leading-tight">
            <span className="font-semibold text-slate-800 block">Row-Level Isolation</span>
            <span>Zero cross-tenant data bleed guaranteed by backend SQL scoping.</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
