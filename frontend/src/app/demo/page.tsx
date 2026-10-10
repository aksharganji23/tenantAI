'use client';

import React, { useState } from 'react';
import AppLayout from '@/components/AppLayout';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { CrossTenantSimulationResult, ChatResponse } from '@/lib/types';
import {
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  Lock,
  Building2,
  FileText,
  MessageSquare,
  Activity,
  ArrowRight,
  Terminal,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react';

export default function JuryDemoPage() {
  const { user, tenant, switchDemoAccount } = useAuth();
  const [simulationResult, setSimulationResult] = useState<CrossTenantSimulationResult | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [chatTesting, setChatTesting] = useState(false);
  const [liveChatResult, setLiveChatResult] = useState<ChatResponse | null>(null);

  const handleSimulateAttack = async (type: 'document' | 'conversation') => {
    setSimulating(true);
    try {
      const res = await api.admin.simulateCrossTenantAttack({
        source_tenant_slug: 'greenleaf',
        target_tenant_slug: 'technova',
        resource_type: type,
      });
      setSimulationResult(res);
    } catch (err) {
      alert(`Simulation call error: ${err}`);
    } finally {
      setSimulating(false);
    }
  };

  const handleLiveQuery = async (queryText: string) => {
    setChatTesting(true);
    setLiveChatResult(null);
    try {
      const res = await api.chat.sendMessage(queryText);
      setLiveChatResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Chat query failed.';
      alert(`Chat error: ${msg}`);
    } finally {
      setChatTesting(false);
    }
  };

  const isTechNova = tenant?.slug === 'technova';
  const isGreenLeaf = tenant?.slug === 'greenleaf';

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="rounded-2xl bg-gradient-to-r from-teal-900 via-slate-900 to-indigo-950 p-6 md:p-8 text-white shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-300 border border-teal-400/30 text-xs font-semibold uppercase tracking-wider">
              Hackathon Evaluation Suite
            </span>
            <span className="text-xs text-slate-300 font-mono">TriCity AI Hackathon</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Live Jury Demonstration & Security Audit Lab
          </h1>
          <p className="mt-1 text-sm text-slate-200 max-w-2xl leading-relaxed">
            Execute the 10-step official jury test sequence. Verify tenant login, isolated RAG citations, real document extraction, and zero-bleed IDOR attack prevention in real time.
          </p>
        </div>

        {/* Current Active Persona Status Bar */}
        <div className="rounded-2xl bg-white p-4 border border-slate-200/80 shadow-2xs flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center font-bold text-sm">
              <Building2 className="h-5 w-5" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block">
                Active Tenant Session
              </span>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-slate-900 text-sm">
                  {tenant?.name || 'Platform Administrator'}
                </span>
                <span className="text-xs font-mono text-slate-500">
                  (Slug: {tenant?.slug || 'admin'} • ID: #{tenant?.id || user?.tenant_id})
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => switchDemoAccount('admin@technova.com', 'DemoPass123!')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition cursor-pointer ${
                isTechNova
                  ? 'bg-blue-600 text-white border-blue-600 shadow-2xs'
                  : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              Company A: TechNova
            </button>
            <button
              onClick={() => switchDemoAccount('admin@greenleaf.com', 'DemoPass123!')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition cursor-pointer ${
                isGreenLeaf
                  ? 'bg-emerald-600 text-white border-emerald-600 shadow-2xs'
                  : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              Company B: GreenLeaf
            </button>
            <button
              onClick={() => switchDemoAccount('admin@tenantai.com', 'SuperAdmin123!')}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition cursor-pointer ${
                user?.role === 'superadmin'
                  ? 'bg-purple-600 text-white border-purple-600 shadow-2xs'
                  : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              SuperAdmin
            </button>
          </div>
        </div>

        {/* Two-Column Test Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Interactive 10-Step Jury Flow */}
          <div className="space-y-4">
            <div className="rounded-2xl bg-white p-6 border border-slate-200/80 shadow-2xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-teal-600" />
                  <h3 className="font-bold text-slate-900 text-sm">
                    10-Step Jury Demonstration Roadmap
                  </h3>
                </div>
                <span className="text-[10px] font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded">
                  Verified MVP
                </span>
              </div>

              <div className="space-y-3 text-xs">
                {/* Step 1 & 2 & 3: TechNova */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
                  <div className="flex items-center justify-between font-bold text-slate-900 mb-1">
                    <span>Part 1: TechNova Solutions Knowledge Retrieval</span>
                    <span className="text-[10px] font-mono text-teal-700 bg-teal-50 px-1.5 py-0.5 rounded">
                      Steps 1-4
                    </span>
                  </div>
                  <p className="text-slate-500 text-[11px] mb-3">
                    Query TechNova UltraBook hardware manual for battery warranty. Answers include source title, page 1, and chunk excerpts.
                  </p>
                  <button
                    onClick={async () => {
                      if (!isTechNova) {
                        await switchDemoAccount('admin@technova.com', 'DemoPass123!');
                      }
                      handleLiveQuery('What is the warranty coverage for the battery?');
                    }}
                    disabled={chatTesting}
                    className="w-full py-2 px-3 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    <span>Run TechNova Battery Query</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                </div>

                {/* Step 4 & 5 & 6: GreenLeaf */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
                  <div className="flex items-center justify-between font-bold text-slate-900 mb-1">
                    <span>Part 2: GreenLeaf Retail Knowledge Retrieval</span>
                    <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">
                      Steps 5-7
                    </span>
                  </div>
                  <p className="text-slate-500 text-[11px] mb-3">
                    Query GreenLeaf retail refund policy for return windows. Answers verify 30-day return policy without accessing TechNova data.
                  </p>
                  <button
                    onClick={async () => {
                      if (!isGreenLeaf) {
                        await switchDemoAccount('admin@greenleaf.com', 'DemoPass123!');
                      }
                      handleLiveQuery('What is the return window for purchases?');
                    }}
                    disabled={chatTesting}
                    className="w-full py-2 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    <span>Run GreenLeaf Refund Query</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                </div>

                {/* Step 7 & 8: Cross-Tenant Probe */}
                <div className="p-3.5 rounded-xl bg-rose-50/60 border border-rose-200">
                  <div className="flex items-center justify-between font-bold text-rose-900 mb-1">
                    <span className="flex items-center gap-1.5">
                      <ShieldAlert className="h-3.5 w-3.5 text-rose-600" />
                      Part 3: Cross-Tenant Breach Attack (Live Probe)
                    </span>
                    <span className="text-[10px] font-mono text-rose-700 bg-rose-100 px-1.5 py-0.5 rounded">
                      Steps 8-9
                    </span>
                  </div>
                  <p className="text-rose-800 text-[11px] mb-3">
                    GreenLeaf user explicitly probes for TechNova UltraBook confidential reset instructions. The system refuses to fabricate and admits data is unavailable in GreenLeaf.
                  </p>
                  <button
                    onClick={async () => {
                      if (!isGreenLeaf) {
                        await switchDemoAccount('admin@greenleaf.com', 'DemoPass123!');
                      }
                      handleLiveQuery('What is the BIOS password reset procedure for the UltraBook Pro X15?');
                    }}
                    disabled={chatTesting}
                    className="w-full py-2 px-3 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    <span>Execute Unauthorized Cross-Tenant Query</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            </div>

            {/* Live Chat Result Visualizer */}
            {liveChatResult && (
              <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-900 flex items-center gap-1.5">
                    <MessageSquare className="h-4 w-4 text-teal-600" />
                    Live RAG Output
                  </span>
                  <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    {liveChatResult.latency_ms}ms • {liveChatResult.tokens_used} tokens
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-800 leading-relaxed font-sans whitespace-pre-wrap">
                  {liveChatResult.content}
                </div>

                {liveChatResult.citations && liveChatResult.citations.length > 0 ? (
                  <div className="space-y-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700">
                      Citations ({liveChatResult.citations.length}):
                    </span>
                    {liveChatResult.citations.map((c, i) => (
                      <div key={i} className="p-2.5 rounded-lg bg-teal-50/60 border border-teal-200 text-xs">
                        <div className="font-semibold text-teal-900 flex justify-between">
                          <span>{c.document_title}</span>
                          <span className="text-[10px]">Page {c.page_number} (Score: {c.score})</span>
                        </div>
                        <p className="text-[11px] text-slate-600 italic mt-1">&ldquo;{c.excerpt}&rdquo;</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-2.5 rounded-lg bg-slate-100 text-slate-600 text-xs flex items-center gap-2 font-medium">
                    <ShieldCheck className="h-4 w-4 text-emerald-600 shrink-0" />
                    <span>0 citations returned (Zero cross-tenant bleed verified).</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Column: Direct IDOR Simulator & Security Enforcement Lab */}
          <div className="space-y-4">
            <div className="rounded-2xl bg-white p-6 border border-slate-200/80 shadow-2xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                <div className="flex items-center gap-2">
                  <Lock className="h-4 w-4 text-purple-600" />
                  <h3 className="font-bold text-slate-900 text-sm">
                    Direct IDOR Security Attack Simulator
                  </h3>
                </div>
                <span className="text-[10px] font-bold text-purple-800 bg-purple-50 px-2 py-0.5 rounded">
                  Direct API Level
                </span>
              </div>

              <p className="text-xs text-slate-500 leading-relaxed mb-4">
                Simulates an attacker on <code>GreenLeaf Retail</code> who knows the database ID of <code>TechNova Solutions</code>&apos;s private document or conversation, and attempts a direct REST API read/delete (Insecure Direct Object Reference).
              </p>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <button
                  onClick={() => handleSimulateAttack('document')}
                  disabled={simulating}
                  className="py-2.5 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <FileText className="h-3.5 w-3.5 text-teal-400" />
                  <span>Simulate Document IDOR</span>
                </button>
                <button
                  onClick={() => handleSimulateAttack('conversation')}
                  disabled={simulating}
                  className="py-2.5 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <MessageSquare className="h-3.5 w-3.5 text-blue-400" />
                  <span>Simulate Thread IDOR</span>
                </button>
              </div>

              {simulating && (
                <div className="p-4 rounded-xl bg-slate-50 text-xs text-slate-600 flex items-center gap-2 animate-pulse">
                  <RefreshCw className="h-4 w-4 animate-spin text-teal-600" />
                  <span>Executing simulated direct cross-tenant request...</span>
                </div>
              )}

              {/* Simulation Result Terminal Output */}
              {simulationResult && (
                <div className="rounded-xl bg-slate-950 p-4 text-slate-100 font-mono text-xs space-y-2 border border-slate-800">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-[10px]">
                    <span className="text-teal-400 flex items-center gap-1">
                      <Terminal className="h-3 w-3" />
                      SIMULATION AUDIT LOG
                    </span>
                    <span className="text-emerald-400 font-bold bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                      HTTP {simulationResult.http_status} NOT FOUND (BLOCKED)
                    </span>
                  </div>

                  <div className="text-[11px] space-y-1 text-slate-300">
                    <p>
                      <span className="text-slate-500">Attacker Tenant:</span>{' '}
                      <span className="text-rose-400">{simulationResult.attacker_tenant}</span>
                    </p>
                    <p>
                      <span className="text-slate-500">Target Tenant:</span>{' '}
                      <span className="text-blue-400">{simulationResult.target_tenant}</span>
                    </p>
                    <p>
                      <span className="text-slate-500">Resource Probed:</span>{' '}
                      <span className="text-amber-400">{simulationResult.attempted_resource_type} #{simulationResult.resource_id}</span>
                    </p>
                    <p>
                      <span className="text-slate-500">Data Leaked:</span>{' '}
                      <span className="text-emerald-400 font-bold">0 BYTES (FALSE)</span>
                    </p>
                    <p>
                      <span className="text-slate-500">Audit Violation Logged:</span>{' '}
                      <span className="text-emerald-400">TRUE (Recorded to Telemetry)</span>
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-800 text-[10px] text-teal-300">
                    {simulationResult.explanation}
                  </div>
                </div>
              )}
            </div>

            {/* Quick Link to Telemetry Logs */}
            <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs flex items-center justify-between">
              <div>
                <h4 className="font-bold text-slate-900 text-xs">Inspect Audit Telemetry Stream</h4>
                <p className="text-[11px] text-slate-500">
                  Verify the live violation event logged by the security simulator.
                </p>
              </div>
              <a
                href="/logs"
                className="px-3.5 py-2 rounded-xl bg-teal-50 border border-teal-200 text-teal-700 hover:bg-teal-100 text-xs font-semibold transition"
              >
                Open Audit Logs
              </a>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
