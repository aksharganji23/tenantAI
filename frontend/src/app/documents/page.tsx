'use client';

import React, { useState, useEffect } from 'react';
import AppLayout from '@/components/AppLayout';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { DocumentItem, DocumentDetail } from '@/lib/types';
import {
  FileText,
  Upload,
  Trash2,
  Eye,
  CheckCircle2,
  Clock,
  AlertCircle,
  RefreshCw,
  HardDrive,
  FileCheck,
  Search,
} from 'lucide-react';

export default function DocumentsPage() {
  const { tenant } = useAuth();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<DocumentDetail | null>(null);
  const [viewLoading, setViewLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Drag and drop state
  const [isDragging, setIsDragging] = useState(false);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await api.documents.list();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleFileUpload = async (file: File) => {
    setUploadError(null);
    setUploadSuccess(null);
    setUploading(true);

    try {
      const newDoc = await api.documents.upload(file);
      setUploadSuccess(`Document '${newDoc.title}' uploaded and indexed into ${newDoc.chunk_count} chunks.`);
      await loadDocuments();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Upload failed.';
      setUploadError(message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: number, title: string) => {
    if (!confirm(`Are you sure you want to delete '${title}'? All chunks and vector indexes will be removed.`)) {
      return;
    }
    try {
      await api.documents.delete(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      if (selectedDoc?.id === docId) {
        setSelectedDoc(null);
      }
    } catch (err) {
      alert(`Deletion failed: ${err}`);
    }
  };

  const handleViewDetails = async (docId: number) => {
    setViewLoading(true);
    try {
      const detail = await api.documents.get(docId);
      setSelectedDoc(detail);
    } catch (err) {
      alert(`Could not load document chunks: ${err}`);
    } finally {
      setViewLoading(false);
    }
  };

  const filteredDocs = documents.filter(
    (d) =>
      d.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black tracking-tight text-slate-900">
              Knowledge Documents
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Manage uploaded corporate files strictly isolated to {tenant?.name || 'this workspace'}.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadDocuments}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-semibold shadow-2xs transition cursor-pointer"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Quota & Upload Zone */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Drag & Drop Upload Card */}
          <div className="md:col-span-2 rounded-2xl bg-white p-6 border-2 border-dashed border-slate-200 hover:border-teal-400 transition">
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                  handleFileUpload(e.dataTransfer.files[0]);
                }
              }}
              className={`flex flex-col items-center justify-center text-center p-6 rounded-xl transition ${
                isDragging ? 'bg-teal-50/60' : 'bg-transparent'
              }`}
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-50 text-teal-600 mb-3">
                <Upload className="h-6 w-6" />
              </div>
              <h3 className="text-sm font-bold text-slate-900">
                Drag & Drop corporate files or click to browse
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Supports PDF, TXT, MD up to 15 MB. Files are automatically chunked and embedded into pgvector.
              </p>

              <label className="mt-4 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-sm transition inline-flex items-center gap-2 cursor-pointer">
                <span>Select Document</span>
                <input
                  type="file"
                  accept=".pdf,.txt,.md"
                  className="hidden"
                  disabled={uploading}
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileUpload(e.target.files[0]);
                    }
                  }}
                />
              </label>

              {uploading && (
                <div className="mt-3 flex items-center gap-2 text-xs text-teal-600 font-semibold animate-pulse">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Parsing text chunks and indexing vector embeddings...</span>
                </div>
              )}

              {uploadSuccess && (
                <div className="mt-3 p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                  <span>{uploadSuccess}</span>
                </div>
              )}

              {uploadError && (
                <div className="mt-3 p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-rose-600 shrink-0" />
                  <span>{uploadError}</span>
                </div>
              )}
            </div>
          </div>

          {/* Quotas & Security Policy Card */}
          <div className="rounded-2xl bg-white p-6 border border-slate-200/80 shadow-2xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Storage & Quota
                </span>
                <HardDrive className="h-4 w-4 text-slate-400" />
              </div>

              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs text-slate-600 mb-1">
                    <span>Document Limit</span>
                    <span className="font-semibold text-slate-900">
                      {documents.length} / {tenant?.quota_docs || 100}
                    </span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                    <div
                      className="h-full bg-teal-600 rounded-full"
                      style={{
                        width: `${Math.min(
                          100,
                          (documents.length / (tenant?.quota_docs || 100)) * 100
                        )}%`,
                      }}
                    ></div>
                  </div>
                </div>

                <div className="pt-2 text-xs text-slate-500 space-y-1">
                  <div className="flex justify-between">
                    <span>Workspace Plan:</span>
                    <span className="font-semibold text-slate-700 capitalize">
                      {tenant?.plan || 'Enterprise'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Chunk Size:</span>
                    <span className="font-mono text-slate-700">600 tokens</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Overlap:</span>
                    <span className="font-mono text-slate-700">120 tokens</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-500 flex items-start gap-2">
              <FileCheck className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>
                All chunks are labeled with <code>tenant_id={tenant?.id}</code> in database vectors to prevent IDOR leaks.
              </span>
            </div>
          </div>
        </div>

        {/* Documents Table */}
        <div className="rounded-2xl bg-white border border-slate-200/80 shadow-2xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="relative flex-1 max-w-sm">
              <Search className="h-4 w-4 absolute left-3 top-3 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search documents by title or filename..."
                className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 outline-none transition"
              />
            </div>

            <span className="text-xs text-slate-400">
              Showing {filteredDocs.length} of {documents.length} files
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 text-slate-500 font-semibold border-b border-slate-100 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-4">Document Title</th>
                  <th className="py-3 px-4">Filename</th>
                  <th className="py-3 px-4">Size</th>
                  <th className="py-3 px-4">Chunks</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Uploaded</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      Loading documents...
                    </td>
                  </tr>
                ) : filteredDocs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      No documents found matching &ldquo;{searchTerm}&rdquo;.
                    </td>
                  </tr>
                ) : (
                  filteredDocs.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-50/60 transition">
                      <td className="py-3 px-4 font-semibold text-slate-900">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-teal-600 shrink-0" />
                          <span>{doc.title}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                        {doc.filename}
                      </td>
                      <td className="py-3 px-4">
                        {(doc.file_size / 1024).toFixed(1)} KB
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-semibold text-slate-800 bg-slate-100 px-2 py-0.5 rounded text-[11px]">
                          {doc.chunk_count}
                        </span>
                      </td>
                      <td className="py-3 px-4">
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
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-[11px]">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleViewDetails(doc.id)}
                            className="p-1.5 rounded-lg text-slate-500 hover:text-teal-700 hover:bg-slate-100 transition cursor-pointer"
                            title="Inspect Chunks"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(doc.id, doc.title)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition cursor-pointer"
                            title="Delete Document"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Document Chunks Inspector Modal */}
        {selectedDoc && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
            <div className="w-full max-w-2xl max-h-[85vh] rounded-2xl bg-white p-6 shadow-2xl border border-slate-200 flex flex-col">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100 shrink-0">
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">
                    {selectedDoc.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {selectedDoc.chunk_count} Semantic Chunks • File: {selectedDoc.filename}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="text-slate-400 hover:text-slate-600 text-base font-bold p-1 cursor-pointer"
                >
                  ✕
                </button>
              </div>

              <div className="flex-1 overflow-y-auto py-4 space-y-3">
                {selectedDoc.chunks && selectedDoc.chunks.length > 0 ? (
                  selectedDoc.chunks.map((ch) => (
                    <div
                      key={ch.id}
                      className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs"
                    >
                      <div className="flex items-center justify-between font-semibold text-slate-700 mb-2">
                        <span className="font-mono text-teal-700">Chunk #{ch.chunk_index}</span>
                        <span className="text-[10px] text-slate-500 bg-white border px-2 py-0.5 rounded">
                          Page {ch.page_number} • {ch.token_count} tokens
                        </span>
                      </div>
                      <p className="text-slate-700 whitespace-pre-wrap leading-relaxed text-[11px] font-sans">
                        {ch.content}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 text-center py-6">
                    No chunk content available.
                  </p>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex justify-end shrink-0">
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
