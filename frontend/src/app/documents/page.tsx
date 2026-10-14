"use client";

import React, { useState, useEffect } from "react";
import { useWorkspace } from "../../context/WorkspaceContext";
import { api, DocumentItem } from "../../lib/api";
import DocumentUploadDropzone from "../../components/DocumentUploadDropzone";
import DocumentList from "../../components/DocumentList";
import { Files, Layers, ShieldCheck, RefreshCw, Loader2 } from "lucide-react";

export default function DocumentsPage() {
  const { activeWorkspace, isLoading: wsLoading } = useWorkspace();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);

  const fetchDocuments = async () => {
    if (!activeWorkspace) return;
    setLoadingDocs(true);
    try {
      const list = await api.listDocuments(activeWorkspace.id);
      setDocuments(list);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [activeWorkspace]);

  if (wsLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "400px" }}>
        <Loader2 size={36} className="animate-spin" style={{ color: "var(--accent-cyan)" }} />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "32px" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
            <Files size={24} style={{ color: "var(--accent-cyan)" }} />
            <h1 style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--text-primary)" }}>
              Document Management
            </h1>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            Upload PDFs to <strong>{activeWorkspace?.name || "Active Workspace"}</strong>. Text is extracted with exact page provenance and chunked into vector embeddings.
          </p>
        </div>

        <button
          type="button"
          onClick={fetchDocuments}
          disabled={loadingDocs}
          className="btn btn-secondary"
          title="Refresh document list"
        >
          <RefreshCw size={16} className={loadingDocs ? "animate-spin" : ""} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Upload Dropzone */}
      {activeWorkspace && (
        <DocumentUploadDropzone
          workspaceId={activeWorkspace.id}
          onUploadSuccess={() => fetchDocuments()}
        />
      )}

      {/* Ingested Documents List */}
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
          <h2 style={{ fontSize: "1.15rem", fontWeight: 600, color: "var(--text-primary)" }}>
            Ingested Documents ({documents.length})
          </h2>
          <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
            Max 10 documents per workspace
          </span>
        </div>

        {activeWorkspace && (
          <DocumentList
            documents={documents}
            workspaceId={activeWorkspace.id}
            onDocumentDeleted={() => fetchDocuments()}
          />
        )}
      </div>
    </div>
  );
}
