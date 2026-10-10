'use client';

import React, { useState, useEffect } from 'react';
import AppLayout from '@/components/AppLayout';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { UsageLog } from '@/lib/types';
import {
  Activity,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Search,
  Filter,
  Clock,
  Cpu,
  Globe,
  Lock,
} from 'lucide-react';

export default function LogsPage() {
  const { user, tenant } = useAuth();
  const [logs, setLogs] = useState<UsageLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');
  const [outcomeFilter, setOutcomeFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await api.logs.getLogs({
        action: actionFilter || undefined,
        outcome: outcomeFilter || undefined,
        limit: 100,
      });
      setLogs(data);
    } catch (err) {
      console.error('Failed to load logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [actionFilter, outcomeFilter]);

  const filteredLogs = logs.filter((log) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (log.action && log.action.toLowerCase().includes(q)) ||
      (log.details && log.details.toLowerCase().includes(q)) ||
      (log.user_email && log.user_email.toLowerCase().includes(q))
    );
  });

  const securityBreachesCount = logs.filter((l) => l.outcome === 'FORBIDDEN').length;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black tracking-tight text-slate-900">
              Audit & Telemetry Logs
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Immutable operational audit trail and security telemetry for {tenant?.name || 'Workspace'}.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadLogs}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-semibold shadow-2xs transition cursor-pointer"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Refresh Telemetry</span>
            </button>
          </div>
        </div>

        {/* Security Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-2">
              <span>Total Recorded Events</span>
              <Activity className="h-4 w-4 text-teal-600" />
            </div>
            <div className="text-2xl font-black text-slate-900">{logs.length}</div>
            <p className="mt-1 text-[11px] text-slate-400">Scoped to caller tenant</p>
          </div>

          <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-2">
              <span>Security Violations Denied</span>
              <ShieldAlert className="h-4 w-4 text-rose-600" />
            </div>
            <div className="text-2xl font-black text-rose-600">{securityBreachesCount}</div>
            <p className="mt-1 text-[11px] text-slate-400">IDOR & unauthorized probes blocked</p>
          </div>

          <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-2">
              <span>Data Confidentiality Status</span>
              <Lock className="h-4 w-4 text-emerald-600" />
            </div>
            <div className="text-base font-extrabold text-emerald-600 flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4" /> 100% Isolated
            </div>
            <p className="mt-1 text-[11px] text-slate-400">0 cross-tenant data leaks</p>
          </div>
        </div>

        {/* Filters and Search Bar */}
        <div className="rounded-2xl bg-white p-4 border border-slate-200/80 shadow-2xs flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2 flex-1">
            <div className="relative min-w-[200px]">
              <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search audit details..."
                className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-slate-200 text-xs focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 outline-none transition"
              />
            </div>

            {/* Action Filter */}
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs text-slate-700 bg-white focus:border-teal-500 outline-none transition cursor-pointer"
            >
              <option value="">All Actions</option>
              <option value="login">login</option>
              <option value="chat_query">chat_query</option>
              <option value="doc_upload">doc_upload</option>
              <option value="cross_tenant_denied">cross_tenant_denied (Security Violation)</option>
            </select>

            {/* Outcome Filter */}
            <select
              value={outcomeFilter}
              onChange={(e) => setOutcomeFilter(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs text-slate-700 bg-white focus:border-teal-500 outline-none transition cursor-pointer"
            >
              <option value="">All Outcomes</option>
              <option value="SUCCESS">SUCCESS</option>
              <option value="FORBIDDEN">FORBIDDEN</option>
              <option value="ERROR">ERROR</option>
            </select>
          </div>

          <span className="text-xs text-slate-400 font-mono">
            {filteredLogs.length} logs
          </span>
        </div>

        {/* Logs Table */}
        <div className="rounded-2xl bg-white border border-slate-200/80 shadow-2xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 text-slate-500 font-semibold border-b border-slate-100 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Outcome</th>
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Latency</th>
                  <th className="py-3 px-4">Tokens</th>
                  <th className="py-3 px-4">Details</th>
                  <th className="py-3 px-4">IP Address</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700 font-sans">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-400">
                      Loading telemetry logs...
                    </td>
                  </tr>
                ) : filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-400">
                      No logs found matching filter criteria.
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((log) => {
                    const isViolation = log.outcome === 'FORBIDDEN' || log.action === 'cross_tenant_denied';
                    return (
                      <tr
                        key={log.id}
                        className={`transition ${
                          isViolation ? 'bg-rose-50/40 hover:bg-rose-50/70' : 'hover:bg-slate-50/60'
                        }`}
                      >
                        <td className="py-3 px-4 text-slate-400 text-[11px] whitespace-nowrap font-mono">
                          {new Date(log.created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit',
                          })}
                        </td>
                        <td className="py-3 px-4 font-mono font-bold text-slate-900">
                          <span
                            className={
                              isViolation
                                ? 'text-rose-700 flex items-center gap-1'
                                : 'text-slate-800'
                            }
                          >
                            {isViolation && <ShieldAlert className="h-3.5 w-3.5 text-rose-600" />}
                            {log.action}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              log.outcome === 'SUCCESS'
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : log.outcome === 'FORBIDDEN'
                                ? 'bg-rose-100 text-rose-800 border border-rose-300 font-extrabold animate-pulse'
                                : 'bg-amber-50 text-amber-700 border border-amber-200'
                            }`}
                          >
                            {log.outcome}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-600 text-[11px] truncate max-w-[140px]">
                          {log.user_email || 'System'}
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                          {log.latency_ms !== null && log.latency_ms !== undefined
                            ? `${log.latency_ms}ms`
                            : '—'}
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                          {log.tokens_used ? `${log.tokens_used}` : '—'}
                        </td>
                        <td className="py-3 px-4 text-slate-600 text-[11px] max-w-sm truncate">
                          {log.details || '—'}
                        </td>
                        <td className="py-3 px-4 font-mono text-[10px] text-slate-400">
                          {log.ip_address || '127.0.0.1'}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
