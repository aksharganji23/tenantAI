'use client';

import React, { useState, useEffect } from 'react';
import AppLayout from '@/components/AppLayout';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { PlatformStats, TenantUsageSummary, Tenant } from '@/lib/types';
import {
  Shield,
  Building2,
  Users,
  FileText,
  Activity,
  Plus,
  RefreshCw,
  Cpu,
  ArrowRight,
  CheckCircle2,
  Lock,
  Sparkles,
} from 'lucide-react';

export default function AdminPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [summaries, setSummaries] = useState<TenantUsageSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New tenant form state
  const [newName, setNewName] = useState('');
  const [newSlug, setNewSlug] = useState('');
  const [newDomain, setNewDomain] = useState('');
  const [newPlan, setNewPlan] = useState('enterprise');
  const [newDocQuota, setNewDocQuota] = useState(100);
  const [newQueryQuota, setNewQueryQuota] = useState(10000);
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [platformStats, tenantSummaries] = await Promise.all([
        api.admin.getStats(),
        api.admin.getTenantsSummary(),
      ]);
      setStats(platformStats);
      setSummaries(tenantSummaries);
    } catch (err) {
      console.error('Failed to load admin telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const handleCreateTenant = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateLoading(true);
    setCreateError(null);

    try {
      await api.admin.createTenant({
        name: newName,
        slug: newSlug,
        domain: newDomain || undefined,
        plan: newPlan,
        quota_docs: newDocQuota,
        quota_queries: newQueryQuota,
      });
      setShowCreateModal(false);
      setNewName('');
      setNewSlug('');
      setNewDomain('');
      await loadAdminData();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Tenant creation failed.';
      setCreateError(msg);
    } finally {
      setCreateLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 text-[10px] font-bold uppercase tracking-wider">
                Root Governance
              </span>
              <span className="text-xs text-slate-400">Operator Portal</span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-slate-900">
              Platform Administration Center
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Global tenant provisioning, resource quotas, and cross-organization telemetry.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-sm transition cursor-pointer"
            >
              <Plus className="h-4 w-4" />
              <span>Provision Tenant</span>
            </button>
            <button
              onClick={loadAdminData}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-semibold shadow-2xs transition cursor-pointer"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Global Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
              <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-2">
                <span>Active Tenants</span>
                <Building2 className="h-4 w-4 text-teal-600" />
              </div>
              <div className="text-2xl font-black text-slate-900">{stats.total_tenants}</div>
              <p className="mt-1 text-[11px] text-slate-400">{stats.active_tenants} online</p>
            </div>

            <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
              <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-2">
                <span>Total Users</span>
                <Users className="h-4 w-4 text-blue-600" />
              </div>
              <div className="text-2xl font-black text-slate-900">{stats.total_users}</div>
              <p className="mt-1 text-[11px] text-slate-400">Across all companies</p>
            </div>

            <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
              <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-2">
                <span>Indexed Documents</span>
                <FileText className="h-4 w-4 text-emerald-600" />
              </div>
              <div className="text-2xl font-black text-slate-900">{stats.total_documents}</div>
              <p className="mt-1 text-[11px] text-slate-400">{stats.failed_documents} failed</p>
            </div>

            <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
              <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-2">
                <span>Total Chat Queries</span>
                <Activity className="h-4 w-4 text-purple-600" />
              </div>
              <div className="text-2xl font-black text-slate-900">{stats.total_queries}</div>
              <p className="mt-1 text-[11px] text-slate-400">All workspaces combined</p>
            </div>

            <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
              <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-2">
                <span>Total Tokens</span>
                <Cpu className="h-4 w-4 text-amber-600" />
              </div>
              <div className="text-2xl font-black text-slate-900">{stats.total_tokens}</div>
              <p className="mt-1 text-[11px] text-slate-400">Measured consumption</p>
            </div>
          </div>
        )}

        {/* Per-Tenant Usage Breakdown Table */}
        <div className="rounded-2xl bg-white border border-slate-200/80 shadow-2xs overflow-hidden">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Tenant Workspaces & Usage Breakdown</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Resource utilization and query frequency per registered organization
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 text-slate-500 font-semibold border-b border-slate-100 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-4">Tenant Name</th>
                  <th className="py-3 px-4">Slug Identifier</th>
                  <th className="py-3 px-4">Documents</th>
                  <th className="py-3 px-4">Queries</th>
                  <th className="py-3 px-4">Tokens Used</th>
                  <th className="py-3 px-4">Last Activity</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      Loading tenant statistics...
                    </td>
                  </tr>
                ) : summaries.map((s) => (
                  <tr key={s.tenant_id} className="hover:bg-slate-50/60 transition">
                    <td className="py-3 px-4 font-semibold text-slate-900">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-teal-600 shrink-0" />
                        <span>{s.tenant_name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                      {s.tenant_slug}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-bold text-slate-900">{s.documents_count}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-bold text-slate-900">{s.queries_count}</span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-600">
                      {s.total_tokens.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">
                      {new Date(s.last_active).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        Active
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Provision New Tenant Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
            <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl border border-slate-200">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <Building2 className="h-5 w-5 text-teal-600" />
                  <h3 className="font-bold text-slate-900 text-sm">Provision New Tenant Workspace</h3>
                </div>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer"
                >
                  ✕
                </button>
              </div>

              {createError && (
                <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800">
                  {createError}
                </div>
              )}

              <form onSubmit={handleCreateTenant} className="mt-4 space-y-4 text-xs">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Company Name</label>
                  <input
                    type="text"
                    required
                    value={newName}
                    onChange={(e) => {
                      setNewName(e.target.value);
                      if (!newSlug) {
                        setNewSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]/g, ''));
                      }
                    }}
                    placeholder="e.g. Apex Health Logistics"
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:border-teal-500 outline-none transition"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Slug Identifier</label>
                  <input
                    type="text"
                    required
                    value={newSlug}
                    onChange={(e) => setNewSlug(e.target.value)}
                    placeholder="e.g. apexhealth"
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 font-mono focus:border-teal-500 outline-none transition"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Domain (Optional)</label>
                  <input
                    type="text"
                    value={newDomain}
                    onChange={(e) => setNewDomain(e.target.value)}
                    placeholder="apexhealth.com"
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:border-teal-500 outline-none transition"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Doc Quota</label>
                    <input
                      type="number"
                      value={newDocQuota}
                      onChange={(e) => setNewDocQuota(parseInt(e.target.value))}
                      className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:border-teal-500 outline-none transition"
                    />
                  </div>
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Query Quota</label>
                    <input
                      type="number"
                      value={newQueryQuota}
                      onChange={(e) => setNewQueryQuota(parseInt(e.target.value))}
                      className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:border-teal-500 outline-none transition"
                    />
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 font-semibold cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createLoading}
                    className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold cursor-pointer disabled:opacity-50"
                  >
                    {createLoading ? 'Provisioning...' : 'Create Tenant'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
