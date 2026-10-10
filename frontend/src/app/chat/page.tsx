'use client';

import React, { useState, useEffect, useRef, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import AppLayout from '@/components/AppLayout';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { ConversationItem, MessageItem, Citation } from '@/lib/types';
import {
  MessageSquare,
  Send,
  Plus,
  Trash2,
  FileText,
  Building2,
  Sparkles,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Cpu,
  Clock,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
} from 'lucide-react';

function ChatContent() {
  const { user, tenant, demoAccounts } = useAuth();
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q');
  const initialConvId = searchParams.get('id');

  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [activeConvId, setActiveConvId] = useState<number | null>(
    initialConvId ? parseInt(initialConvId) : null
  );
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputMessage, setInputMessage] = useState(initialQuery || '');
  const [isSending, setIsSending] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [expandedCitations, setExpandedCitations] = useState<{ [msgId: number]: boolean }>({});
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested prompts for current workspace
  const currentDemoAcc = demoAccounts.find((a) => a.slug === tenant?.slug);
  const suggestedPrompts = currentDemoAcc?.recommended_prompts || [
    'What is the warranty coverage for the battery?',
    'What is the return window for purchases?',
    'Summarize our workspace knowledge base.',
  ];

  // Cross-tenant probe test suggestion
  const crossTenantProbe = currentDemoAcc?.cross_tenant_test || 'Ask for unauthorized data from another tenant.';

  // Load conversations on mount
  useEffect(() => {
    async function loadConversations() {
      try {
        const convList = await api.chat.listConversations();
        setConversations(convList);
        if (convList.length > 0 && !activeConvId) {
          setActiveConvId(convList[0].id);
        }
      } catch (err) {
        console.error('Failed to load conversations:', err);
      }
    }
    loadConversations();
  }, []);

  // Load messages whenever active conversation changes
  useEffect(() => {
    if (!activeConvId) {
      setMessages([]);
      return;
    }

    async function loadMessages() {
      setLoadingMessages(true);
      try {
        const msgList = await api.chat.getMessages(activeConvId!);
        setMessages(msgList);
      } catch (err) {
        console.error('Failed to load messages:', err);
      } finally {
        setLoadingMessages(false);
      }
    }
    loadMessages();
  }, [activeConvId]);

  // Auto-send if initial query provided via URL
  useEffect(() => {
    if (initialQuery && !isSending && messages.length === 0) {
      handleSendMessage(initialQuery);
    }
  }, [initialQuery]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || isSending) return;

    const userText = text.trim();
    setInputMessage('');
    setIsSending(true);

    // Optimistically append user message
    const tempUserMsg: MessageItem = {
      id: Date.now(),
      conversation_id: activeConvId || 0,
      sender: 'user',
      content: userText,
      tokens_used: 0,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await api.chat.sendMessage(userText, activeConvId || undefined);

      // If this was a new conversation, update activeConvId and refresh conv list
      if (!activeConvId || activeConvId !== response.conversation_id) {
        setActiveConvId(response.conversation_id);
        const convList = await api.chat.listConversations();
        setConversations(convList);
      }

      // Append assistant message
      const asstMsg: MessageItem = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        sender: 'assistant',
        content: response.content,
        citations: response.citations,
        confidence_score: response.confidence_score,
        latency_ms: response.latency_ms,
        tokens_used: response.tokens_used,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, asstMsg]);

      // Auto-expand citations if available
      if (response.citations && response.citations.length > 0) {
        setExpandedCitations((prev) => ({ ...prev, [response.message_id]: true }));
      }
    } catch (err: unknown) {
      const errorDetail = err instanceof Error ? err.message : 'Chat query failed.';
      const errMsg: MessageItem = {
        id: Date.now() + 1,
        conversation_id: activeConvId || 0,
        sender: 'assistant',
        content: `Error: ${errorDetail}`,
        tokens_used: 0,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsSending(false);
    }
  };

  const handleNewConversation = () => {
    setActiveConvId(null);
    setMessages([]);
  };

  const handleDeleteConversation = async (convId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this conversation?')) return;

    try {
      await api.chat.deleteConversation(convId);
      const updated = conversations.filter((c) => c.id !== convId);
      setConversations(updated);
      if (activeConvId === convId) {
        setActiveConvId(updated.length > 0 ? updated[0].id : null);
      }
    } catch (err) {
      alert(`Failed to delete conversation: ${err}`);
    }
  };

  const toggleCitations = (msgId: number) => {
    setExpandedCitations((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

  const copyToClipboard = (text: string, id: number) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <AppLayout>
      <div className="flex h-[calc(100vh-8.5rem)] rounded-2xl bg-white border border-slate-200/80 shadow-2xs overflow-hidden">
        {/* Left: Conversation Threads Sidebar */}
        <div className="w-72 border-r border-slate-200 bg-slate-50/50 flex flex-col shrink-0">
          <div className="p-3.5 border-b border-slate-200">
            <button
              onClick={handleNewConversation}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-2xs transition cursor-pointer"
            >
              <Plus className="h-4 w-4" />
              <span>New Conversation</span>
            </button>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {conversations.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-400">
                No conversations yet. Start a new thread!
              </div>
            ) : (
              conversations.map((c) => {
                const isActive = activeConvId === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => setActiveConvId(c.id)}
                    className={`group flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition cursor-pointer ${
                      isActive
                        ? 'bg-teal-50 border border-teal-200 text-teal-900 shadow-2xs font-semibold'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <MessageSquare
                        className={`h-3.5 w-3.5 shrink-0 ${
                          isActive ? 'text-teal-600' : 'text-slate-400'
                        }`}
                      />
                      <span className="truncate">{c.title}</span>
                    </div>

                    <button
                      onClick={(e) => handleDeleteConversation(c.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-600 transition"
                      title="Delete Conversation"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                );
              })
            )}
          </div>

          {/* Sidebar Isolation Footer */}
          <div className="p-3 border-t border-slate-200 text-[11px] text-slate-500 bg-white">
            <div className="flex items-center gap-1.5 text-teal-800 font-semibold mb-0.5">
              <Building2 className="h-3.5 w-3.5 text-teal-600" />
              <span className="truncate">{tenant?.name || 'Workspace'}</span>
            </div>
            <span>Thread isolation strictly locked to Tenant #{tenant?.id}.</span>
          </div>
        </div>

        {/* Right: Main Chat Window */}
        <div className="flex-1 flex flex-col min-w-0 bg-white">
          {/* Chat Header */}
          <div className="h-14 border-b border-slate-200 px-6 flex items-center justify-between bg-white shrink-0">
            <div className="flex items-center gap-2">
              <span className="inline-block h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
              <span className="text-xs font-bold text-slate-900">
                {activeConvId
                  ? conversations.find((c) => c.id === activeConvId)?.title || 'Active Conversation'
                  : 'New Conversation'}
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-[11px] text-slate-500">
                Workspace: <span className="font-semibold text-slate-700">{tenant?.name}</span>
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-full bg-teal-50 border border-teal-200 text-teal-700 text-[10px] font-semibold">
                RAG Grounded Citations
              </span>
            </div>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto py-8">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-50 text-teal-600 mb-4">
                  <Sparkles className="h-6 w-6" />
                </div>
                <h3 className="text-base font-bold text-slate-900">
                  Ask AI About {tenant?.name || 'Your Company'}
                </h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  Questions are resolved using verified retrieval against uploaded documents. All answers provide verifiable source citations.
                </p>

                {/* Suggested Prompts */}
                <div className="mt-6 w-full space-y-2 text-left">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    Suggested Questions for Jury Demo:
                  </span>
                  {suggestedPrompts.map((p, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(p)}
                      className="w-full p-2.5 rounded-xl border border-slate-200 hover:border-teal-400 hover:bg-teal-50/50 text-xs text-slate-700 font-medium text-left transition flex items-center justify-between group cursor-pointer"
                    >
                      <span className="truncate">&ldquo;{p}&rdquo;</span>
                      <Send className="h-3 w-3 text-slate-400 group-hover:text-teal-600 shrink-0 ml-2" />
                    </button>
                  ))}

                  {/* Cross-Tenant Probe Button */}
                  <div className="mt-3 pt-3 border-t border-slate-100">
                    <span className="text-[10px] font-bold text-rose-500 uppercase tracking-wider block mb-1">
                      Test Cross-Tenant Isolation:
                    </span>
                    <button
                      onClick={() =>
                        handleSendMessage(
                          tenant?.slug === 'technova'
                            ? "What is GreenLeaf's 30-day refund policy?"
                            : 'What is the TechNova UltraBook battery warranty?'
                        )
                      }
                      className="w-full p-2.5 rounded-xl border border-rose-200 bg-rose-50/50 hover:bg-rose-100 text-xs text-rose-800 font-medium text-left transition flex items-center justify-between cursor-pointer"
                    >
                      <span className="truncate">
                        Probe unauthorized document: &ldquo;
                        {tenant?.slug === 'technova'
                          ? "What is GreenLeaf's 30-day refund policy?"
                          : 'What is the TechNova UltraBook battery warranty?'}
                        &rdquo;
                      </span>
                      <ShieldAlert className="h-3.5 w-3.5 text-rose-600 shrink-0 ml-2" />
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              messages.map((msg) => {
                const isUser = msg.sender === 'user';
                const hasCitations = msg.citations && msg.citations.length > 0;
                const isExpanded = !!expandedCitations[msg.id];

                return (
                  <div
                    key={msg.id}
                    className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    {!isUser && (
                      <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-600 text-white shrink-0 text-xs font-bold shadow-2xs">
                        AI
                      </div>
                    )}

                    <div
                      className={`max-w-2xl rounded-2xl p-4 text-xs ${
                        isUser
                          ? 'bg-teal-600 text-white rounded-tr-xs shadow-2xs'
                          : 'bg-slate-50 border border-slate-200/80 text-slate-800 rounded-tl-xs'
                      }`}
                    >
                      {/* Message Content */}
                      <div className="leading-relaxed whitespace-pre-wrap font-sans text-[13px]">
                        {msg.content}
                      </div>

                      {/* Assistant Telemetry & Grounding Metadata */}
                      {!isUser && (
                        <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-500">
                          <div className="flex items-center gap-2">
                            {msg.latency_ms !== undefined && msg.latency_ms !== null && (
                              <span className="flex items-center gap-1 font-mono">
                                <Clock className="h-3 w-3 text-slate-400" />
                                {msg.latency_ms}ms
                              </span>
                            )}
                            {msg.tokens_used !== undefined && (
                              <span className="flex items-center gap-1 font-mono">
                                <Cpu className="h-3 w-3 text-slate-400" />
                                {msg.tokens_used} tokens
                              </span>
                            )}
                            {msg.confidence_score !== undefined && msg.confidence_score !== null && (
                              <span className="flex items-center gap-1 font-semibold text-teal-700 bg-teal-50 px-1.5 py-0.5 rounded">
                                Score: {msg.confidence_score}
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => copyToClipboard(msg.content, msg.id)}
                              className="text-slate-400 hover:text-slate-600 p-1 transition"
                              title="Copy Answer"
                            >
                              {copiedId === msg.id ? (
                                <Check className="h-3 w-3 text-emerald-600" />
                              ) : (
                                <Copy className="h-3 w-3" />
                              )}
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Expandable Citations Drawer */}
                      {hasCitations && (
                        <div className="mt-3 pt-2 border-t border-slate-200/60">
                          <button
                            onClick={() => toggleCitations(msg.id)}
                            className="flex items-center gap-1.5 text-[11px] font-bold text-teal-700 hover:text-teal-800 transition cursor-pointer"
                          >
                            <FileText className="h-3.5 w-3.5 text-teal-600" />
                            <span>
                              {msg.citations!.length} Source Citation
                              {msg.citations!.length > 1 ? 's' : ''}
                            </span>
                            {isExpanded ? (
                              <ChevronUp className="h-3.5 w-3.5" />
                            ) : (
                              <ChevronDown className="h-3.5 w-3.5" />
                            )}
                          </button>

                          {isExpanded && (
                            <div className="mt-2.5 space-y-2">
                              {msg.citations!.map((cit, idx) => (
                                <div
                                  key={idx}
                                  className="p-3 rounded-xl bg-white border border-slate-200 text-[11px] shadow-2xs"
                                >
                                  <div className="flex items-center justify-between font-semibold text-slate-900 mb-1">
                                    <span className="text-teal-700 truncate max-w-sm">
                                      {cit.document_title}
                                    </span>
                                    <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px]">
                                      Page {cit.page_number}
                                    </span>
                                  </div>
                                  <p className="text-slate-600 italic bg-slate-50 p-2 rounded-lg border border-slate-100/80 text-[11px]">
                                    &ldquo;{cit.excerpt}&rdquo;
                                  </p>
                                  <div className="mt-1.5 text-[10px] text-slate-400 flex justify-between">
                                    <span>Chunk #{cit.chunk_index}</span>
                                    <span>Relevance: {(cit.score * 100).toFixed(1)}%</span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    {isUser && (
                      <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-slate-200 text-slate-700 shrink-0 text-xs font-bold shadow-2xs">
                        {user?.full_name?.charAt(0) || 'U'}
                      </div>
                    )}
                  </div>
                );
              })
            )}

            {/* AI Generating Indicator */}
            {isSending && (
              <div className="flex gap-3.5 justify-start">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-600 text-white shrink-0 text-xs font-bold shadow-2xs animate-pulse">
                  AI
                </div>
                <div className="rounded-2xl rounded-tl-xs p-4 bg-slate-50 border border-slate-200 text-xs text-slate-500 flex items-center gap-2">
                  <div className="h-3 w-3 animate-spin rounded-full border-2 border-teal-600 border-t-transparent"></div>
                  <span>Performing isolated semantic vector retrieval & synthesizing grounded answer...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Composer Input Bar */}
          <div className="p-4 border-t border-slate-200 bg-white">
            <div className="flex gap-2">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                rows={1}
                placeholder={`Ask TenantAI regarding ${tenant?.name || 'workspace'} documents...`}
                className="flex-1 px-4 py-3 rounded-xl border border-slate-200 text-xs focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 outline-none resize-none transition"
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputMessage.trim() || isSending}
                className="px-5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-sm transition flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                <Send className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>
            <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
              <span>Press <kbd className="px-1 py-0.5 rounded bg-slate-100 border text-[10px]">Enter</kbd> to send, <kbd className="px-1 py-0.5 rounded bg-slate-100 border text-[10px]">Shift+Enter</kbd> for newline</span>
              <span className="flex items-center gap-1 text-emerald-600 font-medium">
                <CheckCircle2 className="h-3 w-3" /> Tenant Knowledge Locked
              </span>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <AppLayout>
          <div className="min-h-[50vh] flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-teal-600 border-t-transparent"></div>
              <span className="text-xs text-slate-500">Loading chat workspace...</span>
            </div>
          </div>
        </AppLayout>
      }
    >
      <ChatContent />
    </Suspense>
  );
}
