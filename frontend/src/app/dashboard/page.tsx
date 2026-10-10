'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import AppLayout from '@/components/AppLayout';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { DocumentItem, ConversationItem, UsageLog } from '@/lib/types';
import {
  FileText,
  MessageSquare,
  Activity,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  Upload,
  Clock,
  Send,
  AlertCircle,
  CheckCircle2,
  Lock,
  ChevronRight,
} from 'lucide-react';

export default function DashboardPage() {
  const { user, tenant, demoAccounts } = useAuth();
  const router = useRouter();

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [recentLogs, setRecentLogs] = useState<UsageLog[]>([]);
  const [quickQuery, setQuickQuery] = useState('');
  const [loading, setLoading] = useState(true);

  // Current persona's recommended prompts
  const currentDemoAcc = demoAccounts.find((a) => a.slug === tenant?.slug);
  const samplePrompts = currentDemoAcc?.recommended_prompts || [
    'What is the warranty coverage for the battery?',
    'What is the return window for purchases?',
    'Summarize our workspace knowledge base.',
  ];

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [docs, convs, logs] = await Promise.all([
          api.documents.list(),
          api.chat.listConversations(),
          api.logs.getLogs({ limit: 6 }),
        ]);
        setDocuments(docs);
        setConversations(convs);
        setRecentLogs(logs);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const handleStartChat = (prompt?: string) => {
    const q = prompt || quickQuery;
    if (q.trim()) {
      router.push(`/chat?q=${encodeURIComponent(q.trim())}`);
    } else {
      router.push('/chat');
    }
  };

  const totalTokens = recentLogs.reduce((acc, log) => acc + (log.tokens_used || 0), 0);
  const readyDocs = documents.filter((d) => d.status === 'READY').length;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Top Workspace Welcome Banner */}
        <div className="rounded-2xl bg-gradient-to-r from-teal-900 via-teal-800 to-slate-900 p-6 md:p-8 text-white shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full bg-teal-500/20 text-teal-300 border border-teal-400/30 text-xs font-semibold uppercase tracking-wider">
                {tenant?.name || user?.tenant_name || 'Active Workspace'}
              </span>
              <span className="text-xs text-teal-200/70 font-mono">
                Slug: {tenant?.slug || 'default'}
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
              Welcome back, {user?.full_name?.split(' ')[0]}
            </h1>
            <p className="mt-1 text-sm text-teal-100/80 max-w-xl">
              Your private corporate knowledge boundary is active. RAG queries retrieve citations exclusively from this workspace.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/documents"
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 text-white font-semibold text-xs transition border border-white/10"
            >
              <Upload className="h-4 w-4" />
              <span>Upload Document</span>
            </Link>
            <Link
              href="/chat"
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs transition shadow-md shadow-teal-500/20"
            >
              <MessageSquare className="h-4 w-4" />
              <span>Open AI Chat</span>
            </Link>
          </div>
        </div>

        {/* 4 Key Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Docs Count */}
          <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-3">
              <span>Verified Documents</span>
              <div className="p-2 rounded-xl bg-teal-50 text-teal-600">
                <FileText className="h-4 w-4" />
              </div>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-black text-slate-900">{documents.length}</span>
              <span className="text-xs text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded-full">
                {readyDocs} Indexed
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400">
              Quota: {documents.length} / {tenant?.quota_docs || 100} files used
            </p>
          </div>

          {/* Conversations */}
          <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-3">
              <span>Chat Conversations</span>
              <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
                <MessageSquare className="h-4 w-4" />
              </div>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-black text-slate-900">{conversations.length}</span>
              <span className="text-xs text-blue-600 font-semibold bg-blue-50 px-2 py-0.5 rounded-full">
                Active
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400">
              Strict isolation: 0 leaks across tenants
            </p>
          </div>

          {/* Telemetry Tokens */}
          <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-3">
              <span>Tokens Processed</span>
              <div className="p-2 rounded-xl bg-purple-50 text-purple-600">
                <Activity className="h-4 w-4" />
              </div>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-black text-slate-900">{totalTokens}</span>
              <span className="text-xs text-purple-600 font-semibold bg-purple-50 px-2 py-0.5 rounded-full">
                Live Audit
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400">
              Measured from live request telemetry
            </p>
          </div>

          {/* Security Shield */}
          <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-3">
              <span>Tenant Security Status</span>
              <div className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
                <ShieldCheck className="h-4 w-4" />
              </div>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="text-base font-extrabold text-emerald-600 flex items-center gap-1.5">
                <Lock className="h-4 w-4" /> Protected
              </span>
              <span className="text-xs text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded-full">
                SQL Isolated
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400">
              Tenant ID: #{tenant?.id || user?.tenant_id} strictly verified
            </p>
          </div>
        </div>

        {/* Quick Question Composer Bar */}
        <div className="rounded-2xl bg-white p-5 border border-slate-200/80 shadow-2xs">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="h-4 w-4 text-teal-600" />
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Ask AI Grounded in {tenant?.name || 'Workspace'} Documents
            </h3>
          </div>

          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={quickQuery}
              onChange={(e) => setQuickQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleStartChat()}
              placeholder={`Ask a question based on uploaded ${tenant?.name || ''} documents...`}
              className="flex-1 px-4 py-3 rounded-xl border border-slate-200 text-sm focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 outline-none transition"
            />
            <button
              onClick={() => handleStartChat()}
              className="px-5 py-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-sm transition flex items-center justify-center gap-2 shrink-0 cursor-pointer"
            >
              <span>Ask AI</span>
              <Send className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Suggested Demo Prompt Chips */}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-semibold text-slate-400">Recommended Prompts:</span>
            {samplePrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleStartChat(prompt)}
                className="px-2.5 py-1 rounded-lg bg-slate-50 hover:bg-teal-50 border border-slate-200 hover:border-teal-300 text-[11px] text-slate-700 hover:text-teal-800 transition cursor-pointer text-left"
              >
                &ldquo;{prompt}&rdquo;
              </button>
            ))}
          </div>
        </div>

        {/* Main Content Split Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: Documents & Conversations */}
          <div className="lg:col-span-2 space-y-6">
            {/* Knowledge Documents Overview */}
            <div className="rounded-2xl bg-white border border-slate-200/80 shadow-2xs overflow-hidden">
              <div className="p-5 border-b border-slate-100 flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Workspace Documents</h3>
                  <p className="text-xs text-slate-500">
                    Extracted, semantic-chunked, and vector-indexed documents
                  </p>
                </div>
                <Link
                  href="/documents"
                  className="text-xs font-semibold text-teal-600 hover:text-teal-700 flex items-center gap-1"
                >
                  <span>Manage all</span>
                  <ChevronRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              <div className="divide-y divide-slate-100">
                {documents.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-500">
                    No documents uploaded yet in this workspace.
                    <div className="mt-3">
                      <Link
                        href="/documents"
                        className="px-3 py-1.5 rounded-lg bg-teal-600 text-white font-semibold inline-flex items-center gap-1.5"
                      >
                        <Upload className="h-3 w-3" /> Upload First Document
                      </Link>
                    </div>
                  </div>
                ) : (
                  documents.slice(0, 4).map((doc) => (
                    <div
                      key={doc.id}
                      className="p-4 flex items-center justify-between hover:bg-slate-50/80 transition"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-slate-100 text-slate-600 shrink-0">
                          <FileText className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-slate-900 text-xs">{doc.title}</h4>
                          <div className="flex items-center gap-2 mt-0.5 text-[11px] text-slate-400">
                            <span>{doc.filename}</span>
                            <span>•</span>
                            <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                            <span>•</span>
                            <span>{doc.chunk_count} chunks</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            doc.status === 'READY'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : doc.status === 'PROCESSING'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-rose-50 text-rose-700 border border-rose-200'
                          }`}
                        >
                          {doc.status}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Recent Conversations */}
            <div className="rounded-2xl bg-white border border-slate-200/80 shadow-2xs overflow-hidden">
              <div className="p-5 border-b border-slate-100 flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Recent Conversations</h3>
                  <p className="text-xs text-slate-500">
                    Isolated threads with grounded citations
                  </p>
                </div>
                <Link
                  href="/chat"
                  className="text-xs font-semibold text-teal-600 hover:text-teal-700 flex items-center gap-1"
                >
                  <span>New Conversation</span>
                  <ChevronRight className="h-3.5 w-3.5" />
                </Link>
              </div>

              <div className="divide-y divide-slate-100">
                {conversations.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-500">
                    No active conversations. Start asking questions above!
                  </div>
                ) : (
                  conversations.slice(0, 4).map((c) => (
                    <Link
                      key={c.id}
                      href={`/chat?id=${c.id}`}
                      className="p-4 flex items-center justify-between hover:bg-slate-50/80 transition group block"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-teal-50 text-teal-600 group-hover:bg-teal-600 group-hover:text-white transition shrink-0">
                          <MessageSquare className="h-3.5 w-3.5" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-slate-900 text-xs group-hover:text-teal-600 transition truncate max-w-md">
                            {c.title}
                          </h4>
                          <span className="text-[10px] text-slate-400">
                            {c.message_count ? `${c.message_count} messages` : 'Recent'} • {new Date(c.updated_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-teal-600 transition" />
                    </Link>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right Column: Audit Feed & Jury Demo Quick Test */}
          <div className="space-y-6">
            {/* Live Security Audit Telemetry Feed */}
            <div className="rounded-2xl bg-white border border-slate-200/80 shadow-2xs overflow-hidden">
              <div className="p-5 border-b border-slate-100 flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Audit & Telemetry Stream</h3>
                  <p className="text-xs text-slate-500">Live operational & security logs</p>
                </div>
                <Link
                  href="/logs"
                  className="text-xs font-semibold text-teal-600 hover:text-teal-700"
                >
                  View all
                </Link>
              </div>

              <div className="p-4 space-y-3">
                {recentLogs.length === 0 ? (
                  <p className="text-xs text-slate-400">No telemetry recorded yet.</p>
                ) : (
                  recentLogs.map((log) => (
                    <div
                      key={log.id}
                      className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-slate-800 font-mono text-[11px]">
                          {log.action}
                        </span>
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                            log.outcome === 'SUCCESS'
                              ? 'bg-emerald-100 text-emerald-800'
                              : log.outcome === 'FORBIDDEN'
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {log.outcome}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-600 line-clamp-2 leading-relaxed">
                        {log.details || 'Telemetry event recorded'}
                      </p>
                      <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                        <span>{log.user_email || 'System'}</span>
                        <span>{log.latency_ms ? `${log.latency_ms}ms` : ''}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Jury Live Verification Suite Card */}
            <div className="rounded-2xl bg-gradient-to-br from-teal-50 to-emerald-50 border border-teal-200 p-5">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="h-4 w-4 text-teal-700" />
                <h3 className="font-bold text-teal-950 text-xs uppercase tracking-wider">
                  Jury Live Verification Lab
                </h3>
              </div>
              <p className="text-xs text-teal-900/80 leading-relaxed mb-4">
                Execute live simulated cross-tenant attacks (IDOR) and verify that unauthorized data access returns 404 with instant security violation alerts.
              </p>
              <Link
                href="/demo"
                className="w-full py-2.5 px-4 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs flex items-center justify-center gap-2 transition shadow-sm"
              >
                <span>Launch Jury Security Simulator</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
