const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface Workspace {
  id: string;
  name: string;
  description?: string;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  workspace_id: string;
  filename: string;
  file_size_bytes: number;
  status: "PENDING" | "PARSING" | "EMBEDDING" | "READY" | "FAILED";
  page_count: number;
  chunk_count: number;
  error_message?: string;
  created_at: string;
  updated_at?: string;
}

export interface CitationDetail {
  citation_key: string;
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_number: number;
  similarity_score: number;
  quoted_snippet: string;
  claim?: string;
}

export interface QueryResponse {
  query_id: string;
  question: string;
  answer: string;
  status: "GROUNDED" | "INSUFFICIENT_EVIDENCE" | "CITATION_FAILED";
  latency_ms: number;
  citations: CitationDetail[];
}

export interface EvidenceDetail {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_number: number;
  chunk_index: number;
  content: string;
  surrounding_context?: string;
}

export interface DocumentFinding {
  document_id: string;
  document_name: string;
  has_sufficient_evidence: boolean;
  summary: string;
  citations: CitationDetail[];
}

export interface ComparisonResponse {
  comparison_id: string;
  workspace_id: string;
  topic: string;
  status: string;
  relationship: "AGREEMENT" | "DIFFERENCE" | "CONTRADICTION" | "DIFFERENT_SCOPES" | "INSUFFICIENT_EVIDENCE";
  synthesis: string;
  scope_notes?: string;
  document_findings: DocumentFinding[];
  latency_ms: number;
}

export interface EvalItemResult {
  id: string;
  question: string;
  category: string;
  expected_behavior: string;
  actual_behavior: string;
  passed: boolean;
  details?: string;
}

export interface EvalReportResponse {
  total_questions: number;
  passed_count: number;
  retrieval_hit_rate_pct: number;
  citation_validity_pct: number;
  negative_control_abstention_pct: number;
  average_latency_ms: number;
  is_model_judged: boolean;
  results: EvalItemResult[];
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!res.ok) {
    let errorDetail = "API request failed";
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json();
}

export const api = {
  // Workspaces
  async listWorkspaces(): Promise<Workspace[]> {
    return request<Workspace[]>("/workspaces/");
  },

  async createWorkspace(name: string, description: string = ""): Promise<Workspace> {
    return request<Workspace>("/workspaces/", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    });
  },

  async deleteWorkspace(workspaceId: string): Promise<void> {
    return request<void>(`/workspaces/${workspaceId}`, {
      method: "DELETE",
    });
  },

  // Documents
  async listDocuments(workspaceId: string): Promise<DocumentItem[]> {
    return request<DocumentItem[]>(`/workspaces/${workspaceId}/documents`);
  },

  async uploadDocument(workspaceId: string, file: File): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/workspaces/${workspaceId}/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(errJson.detail || "Upload failed");
    }

    return res.json();
  },

  async getDocument(workspaceId: string, documentId: string): Promise<DocumentItem> {
    return request<DocumentItem>(`/workspaces/${workspaceId}/documents/${documentId}`);
  },

  async deleteDocument(workspaceId: string, documentId: string): Promise<void> {
    return request<void>(`/workspaces/${workspaceId}/documents/${documentId}`, {
      method: "DELETE",
    });
  },

  // Grounded Q&A
  async queryQA(
    workspaceId: string,
    question: string,
    documentIds?: string[],
    topK: number = 5
  ): Promise<QueryResponse> {
    return request<QueryResponse>(`/workspaces/${workspaceId}/qa/query`, {
      method: "POST",
      body: JSON.stringify({
        question,
        document_ids: documentIds && documentIds.length > 0 ? documentIds : null,
        top_k: topK,
      }),
    });
  },

  // Multi-Document Comparison
  async compareDocuments(
    workspaceId: string,
    topic: string,
    documentIds: string[],
    topKPerDoc: number = 3
  ): Promise<ComparisonResponse> {
    return request<ComparisonResponse>(`/workspaces/${workspaceId}/comparison/query`, {
      method: "POST",
      body: JSON.stringify({
        topic,
        document_ids: documentIds,
        top_k_per_document: topKPerDoc,
      }),
    });
  },

  // Evidence Inspection
  async getEvidence(chunkId: string): Promise<EvidenceDetail> {
    return request<EvidenceDetail>(`/evidence/${chunkId}`);
  },

  // Curated Benchmark Evaluation
  async runEvaluation(): Promise<EvalReportResponse> {
    return request<EvalReportResponse>("/evaluation/run", {
      method: "POST",
      body: JSON.stringify({ run_llm_judge: false }),
    });
  },
};
