import {
  User,
  Tenant,
  DocumentItem,
  DocumentDetail,
  ConversationItem,
  MessageItem,
  ChatResponse,
  UsageLog,
  PlatformStats,
  TenantUsageSummary,
  CrossTenantSimulationResult,
  DemoAccount,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
const API_PREFIX = '/api/v1';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('tenantai_token');
}

export function setStoredToken(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('tenantai_token', token);
  }
}

export function clearStoredToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('tenantai_token');
    localStorage.removeItem('tenantai_user');
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers || {});

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const url = `${API_BASE}${API_PREFIX}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || JSON.stringify(errorJson);
    } catch {
      errorDetail = await response.text();
    }
    const err = new Error(errorDetail);
    (err as unknown as { status: number }).status = response.status;
    throw err;
  }

  return response.json();
}

export const api = {
  auth: {
    login: async (email: string, password: string): Promise<{ access_token: string; token_type: string; user: User }> => {
      const res = await request<{ access_token: string; token_type: string; user: User }>(
        '/auth/login',
        {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        }
      );
      setStoredToken(res.access_token);
      if (typeof window !== 'undefined') {
        localStorage.setItem('tenantai_user', JSON.stringify(res.user));
      }
      return res;
    },
    me: async (): Promise<User> => {
      return request<User>('/auth/me');
    },
    logout: async (): Promise<{ message: string }> => {
      try {
        await request<{ message: string }>('/auth/logout', { method: 'POST' });
      } finally {
        clearStoredToken();
      }
      return { message: 'Logged out' };
    },
  },

  demo: {
    getAccounts: async (): Promise<{ accounts: DemoAccount[] }> => {
      return request<{ accounts: DemoAccount[] }>('/demo/accounts');
    },
    resetSeed: async (): Promise<{ message: string }> => {
      return request<{ message: string }>('/demo/reset-seed', { method: 'POST' });
    },
  },

  tenants: {
    getCurrent: async (): Promise<Tenant> => {
      return request<Tenant>('/tenants/current');
    },
    updateCurrent: async (data: { name?: string; domain?: string }): Promise<Tenant> => {
      return request<Tenant>('/tenants/current', {
        method: 'PATCH',
        body: JSON.stringify(data),
      });
    },
    listAll: async (): Promise<Tenant[]> => {
      return request<Tenant[]>('/tenants');
    },
  },

  documents: {
    list: async (): Promise<DocumentItem[]> => {
      return request<DocumentItem[]>('/documents');
    },
    get: async (id: number): Promise<DocumentDetail> => {
      return request<DocumentDetail>(`/documents/${id}`);
    },
    upload: async (file: File, title?: string): Promise<DocumentItem> => {
      const formData = new FormData();
      formData.append('file', file);
      if (title) formData.append('title', title);

      return request<DocumentItem>('/documents/upload', {
        method: 'POST',
        body: formData,
      });
    },
    delete: async (id: number): Promise<{ message: string }> => {
      return request<{ message: string }>(`/documents/${id}`, {
        method: 'DELETE',
      });
    },
  },

  chat: {
    sendMessage: async (
      message: string,
      conversationId?: number,
      topK = 4
    ): Promise<ChatResponse> => {
      return request<ChatResponse>('/chat/message', {
        method: 'POST',
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          top_k: topK,
        }),
      });
    },
    listConversations: async (): Promise<ConversationItem[]> => {
      return request<ConversationItem[]>('/chat/conversations');
    },
    getMessages: async (conversationId: number): Promise<MessageItem[]> => {
      return request<MessageItem[]>(`/chat/conversations/${conversationId}/messages`);
    },
    deleteConversation: async (conversationId: number): Promise<{ message: string }> => {
      return request<{ message: string }>(`/chat/conversations/${conversationId}`, {
        method: 'DELETE',
      });
    },
  },

  logs: {
    getLogs: async (params?: { action?: string; outcome?: string; limit?: number; offset?: number }): Promise<UsageLog[]> => {
      const searchParams = new URLSearchParams();
      if (params?.action) searchParams.set('action', params.action);
      if (params?.outcome) searchParams.set('outcome', params.outcome);
      if (params?.limit) searchParams.set('limit', params.limit.toString());
      if (params?.offset) searchParams.set('offset', params.offset.toString());
      const queryStr = searchParams.toString();
      return request<UsageLog[]>(`/logs${queryStr ? `?${queryStr}` : ''}`);
    },
  },

  admin: {
    getStats: async (): Promise<PlatformStats> => {
      return request<PlatformStats>('/admin/stats');
    },
    getTenantsSummary: async (): Promise<TenantUsageSummary[]> => {
      return request<TenantUsageSummary[]>('/admin/tenants/summary');
    },
    createTenant: async (data: {
      name: string;
      slug: string;
      domain?: string;
      plan: string;
      quota_docs: number;
      quota_queries: number;
    }): Promise<Tenant> => {
      return request<Tenant>('/admin/tenants', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    simulateCrossTenantAttack: async (params?: {
      source_tenant_slug?: string;
      target_tenant_slug?: string;
      resource_type?: 'document' | 'conversation';
    }): Promise<CrossTenantSimulationResult> => {
      const searchParams = new URLSearchParams();
      if (params?.source_tenant_slug) searchParams.set('source_tenant_slug', params.source_tenant_slug);
      if (params?.target_tenant_slug) searchParams.set('target_tenant_slug', params.target_tenant_slug);
      if (params?.resource_type) searchParams.set('resource_type', params.resource_type);
      const queryStr = searchParams.toString();
      return request<CrossTenantSimulationResult>(
        `/admin/security/simulate-cross-tenant-attack${queryStr ? `?${queryStr}` : ''}`,
        { method: 'POST' }
      );
    },
  },
};
