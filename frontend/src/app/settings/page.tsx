'use client';

import React, { useState, useEffect } from 'react';
import AppLayout from '@/components/AppLayout';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import {
  Building2,
  Lock,
  Save,
  CheckCircle2,
  Shield,
  HardDrive,
  Users,
  Globe,
  Key,
} from 'lucide-react';

export default function SettingsPage() {
  const { user, tenant, refreshTenant } = useAuth();
  const [name, setName] = useState('');
  const [domain, setDomain] = useState('');
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (tenant) {
      setName(tenant.name || '');
      setDomain(tenant.domain || '');
    }
  }, [tenant]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(null);
    setError(null);

    try {
      await api.tenants.updateCurrent({ name, domain });
      await refreshTenant();
      setSuccess('Workspace settings saved successfully.');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Save failed.';
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  const isTenantAdmin = user?.role === 'tenant_admin' || user?.role === 'superadmin';

  return (
    <AppLayout>
      <div className="space-y-6 max-w-4xl">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-black tracking-tight text-slate-900">
            Workspace Settings
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure tenant parameters, domain bindings, and security boundaries.
          </p>
        </div>

        {/* Workspace Form */}
        <div className="rounded-2xl bg-white p-6 border border-slate-200/80 shadow-2xs">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
            <Building2 className="h-4 w-4 text-teal-600" />
            <h3 className="font-bold text-slate-900 text-sm">Company Workspace Profile</h3>
          </div>

          {success && (
            <div className="mb-4 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
              <span>{success}</span>
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800">
              {error}
            </div>
          )}

          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Tenant Company Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={!isTenantAdmin}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:border-teal-500 outline-none transition disabled:bg-slate-50 disabled:text-slate-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Tenant Unique Slug (Immutable)
                </label>
                <input
                  type="text"
                  disabled
                  value={tenant?.slug || ''}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs bg-slate-50 text-slate-500 font-mono outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Corporate Domain / URL
              </label>
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                disabled={!isTenantAdmin}
                placeholder="e.g. company.com"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:border-teal-500 outline-none transition disabled:bg-slate-50 disabled:text-slate-500"
              />
            </div>

            {isTenantAdmin && (
              <div className="pt-2 flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-sm transition flex items-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <Save className="h-3.5 w-3.5" />
                  <span>{saving ? 'Saving...' : 'Save Workspace Changes'}</span>
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Quotas & Capacity Card */}
        <div className="rounded-2xl bg-white p-6 border border-slate-200/80 shadow-2xs">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
            <HardDrive className="h-4 w-4 text-teal-600" />
            <h3 className="font-bold text-slate-900 text-sm">Contract Quotas & Subscription</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-[11px] font-semibold text-slate-500 block">Subscription Tier</span>
              <span className="text-base font-bold text-slate-900 capitalize mt-1 block">
                {tenant?.plan || 'Enterprise'} Plan
              </span>
              <span className="text-[10px] text-teal-700 mt-1 inline-block">
                Dedicated vector namespace enabled
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-[11px] font-semibold text-slate-500 block">Monthly Query Capacity</span>
              <span className="text-base font-bold text-slate-900 mt-1 block">
                {tenant?.quota_queries?.toLocaleString() || '10,000'} Queries
              </span>
              <span className="text-[10px] text-slate-500 mt-1 inline-block">
                Unlimited semantic embeddings
              </span>
            </div>
          </div>
        </div>

        {/* User Identity Details */}
        <div className="rounded-2xl bg-white p-6 border border-slate-200/80 shadow-2xs">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
            <Users className="h-4 w-4 text-teal-600" />
            <h3 className="font-bold text-slate-900 text-sm">Authenticated User Profile</h3>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Name:</span>
              <span className="font-semibold text-slate-900">{user?.full_name}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Email:</span>
              <span className="font-mono text-slate-900">{user?.email}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Assigned Role:</span>
              <span className="font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded">
                {user?.role}
              </span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Tenant Binding:</span>
              <span className="font-mono text-slate-900">
                Tenant #{tenant?.id || user?.tenant_id} ({tenant?.name})
              </span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
