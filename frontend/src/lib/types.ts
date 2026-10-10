export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'superadmin' | 'tenant_admin' | 'tenant_user';
  tenant_id: number;
  tenant_name?: string;
  tenant_slug?: string;
  is_active: boolean;
}

export interface Tenant {
  id: number;
  name: string;
  slug: string;
  domain?: string;
  plan: string;
  is_active: boolean;
  quota_docs: number;
  quota_queries: number;
  created_at: string;
  user_count?: number;
  document_count?: number;
}

export interface DocumentChunk {
  id: number;
  chunk_index: number;
  content: string;
  page_number: number;
  token_count: number;
}

export interface DocumentItem {
  id: number;
  tenant_id: number;
  filename: string;
  file_type: string;
  file_size: number;
  title: string;
  status: 'PENDING' | 'PROCESSING' | 'READY' | 'FAILED';
  chunk_count: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentDetail extends DocumentItem {
  chunks: DocumentChunk[];
}

export interface Citation {
  document_id: number;
  document_title: string;
  page_number: number;
  chunk_index: number;
  excerpt: string;
  score: number;
}

export interface MessageItem {
  id: number;
  conversation_id: number;
  sender: 'user' | 'assistant';
  content: string;
  citations?: Citation[] | null;
  confidence_score?: number | null;
  latency_ms?: number | null;
  tokens_used: number;
  created_at: string;
}

export interface ConversationItem {
  id: number;
  tenant_id: number;
  user_id: number;
  title: string;
  message_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ChatResponse {
  message_id: number;
  conversation_id: number;
  role: 'assistant';
  content: string;
  citations: Citation[];
  confidence_score?: number | null;
  latency_ms: number;
  tokens_used: number;
  is_grounded: boolean;
  model_name: string;
}

export interface UsageLog {
  id: number;
  tenant_id?: number | null;
  tenant_name?: string | null;
  user_email?: string | null;
  action: string;
  outcome: 'SUCCESS' | 'FORBIDDEN' | 'ERROR' | 'DEGRADED';
  latency_ms?: number | null;
  tokens_used: number;
  model_name?: string | null;
  details?: string | null;
  ip_address?: string | null;
  created_at: string;
}

export interface PlatformStats {
  total_tenants: number;
  total_users: number;
  total_documents: number;
  total_queries: number;
  total_tokens: number;
  active_tenants: number;
  failed_documents: number;
}

export interface TenantUsageSummary {
  tenant_id: number;
  tenant_name: string;
  tenant_slug: string;
  documents_count: number;
  queries_count: number;
  total_tokens: number;
  last_active: string;
}

export interface CrossTenantSimulationResult {
  simulation_name: string;
  attacker_tenant: string;
  target_tenant: string;
  attempted_resource_type: string;
  resource_id: number;
  http_status: number;
  is_blocked: boolean;
  data_leaked: boolean;
  audit_logged: boolean;
  explanation: string;
}

export interface DemoAccount {
  company: string;
  slug: string;
  role: string;
  email: string;
  password: string;
  badge: string;
  sample_document: string;
  recommended_prompts: string[];
  cross_tenant_test: string;
}
