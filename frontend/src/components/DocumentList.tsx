"use client";

import React, { useState } from "react";
import { DocumentItem, api } from "../lib/api";
import { FileText, Trash2, CheckCircle2, Clock, AlertTriangle, Layers, BookOpen, CheckSquare, Square } from "lucide-react";

interface DocumentListProps {
  documents: DocumentItem[];
  workspaceId: string;
  selectedIds?: string[];
  onToggleSelect?: (id: string) => void;
  onDocumentDeleted?: (id: string) => void;
  selectable?: boolean;
}

export default function DocumentList({
  documents,
  workspaceId,
  selectedIds = [],
  onToggleSelect,
  onDocumentDeleted,
  selectable = false,
}: DocumentListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleDelete = async (docId: string, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"? All extracted chunks and vectors will be removed.`)) {
      return;
    }

    setDeletingId(docId);
    try {
      await api.deleteDocument(workspaceId, docId);
      if (onDocumentDeleted) {
        onDocumentDeleted(docId);
      }
    } catch (err: any) {
      alert(`Failed to delete document: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const getStatusBadge = (status: DocumentItem["status"]) => {
    switch (status) {
      case "READY":
        return (
          <span className="badge badge-success">
            <CheckCircle2 size={12} /> Ready
          </span>
        );
      case "PARSING":
      case "EMBEDDING":
      case "PENDING":
        return (
          <span className="badge badge-warning">
            <Clock size={12} className="animate-spin" /> {status}
          </span>
        );
      case "FAILED":
        return (
          <span className="badge badge-danger">
            <AlertTriangle size={12} /> Failed
          </span>
        );
      default:
        return <span className="badge badge-secondary">{status}</span>;
    }
  };

  if (documents.length === 0) {
    return (
      <div
        className="glass-panel"
        style={{
          padding: "40px 24px",
          textAlign: "center",
          color: "var(--text-muted)",
        }}
      >
        <FileText size={40} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
        <p style={{ fontWeight: 500, color: "var(--text-secondary)", marginBottom: "4px" }}>
          No documents in this workspace yet
        </p>
        <p style={{ fontSize: "0.85rem" }}>
          Upload a PDF above to begin grounded document Q&A and cross-document comparison.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px", width: "100%" }}>
      {documents.map((doc) => {
        const isSelected = selectedIds.includes(doc.id);

        return (
          <div
            key={doc.id}
            className="glass-panel"
            style={{
              padding: "16px 20px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              border: isSelected ? "1px solid var(--accent-cyan)" : "1px solid var(--border-subtle)",
              backgroundColor: isSelected ? "rgba(6, 182, 212, 0.04)" : "var(--bg-glass)",
              transition: "all var(--transition-fast)",
            }}
          >
            {/* Left: Checkbox & File Info */}
            <div style={{ display: "flex", alignItems: "center", gap: "14px", flex: 1, minWidth: 0 }}>
              {selectable && onToggleSelect && (
                <button
                  type="button"
                  onClick={() => onToggleSelect(doc.id)}
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: isSelected ? "var(--accent-cyan)" : "var(--text-muted)",
                    display: "flex",
                    alignItems: "center",
                  }}
                  title={isSelected ? "Deselect document" : "Select document"}
                >
                  {isSelected ? <CheckSquare size={20} /> : <Square size={20} />}
                </button>
              )}

              <div
                style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: "var(--radius-md)",
                  backgroundColor: "rgba(6, 182, 212, 0.1)",
                  color: "var(--accent-cyan)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <FileText size={20} />
              </div>

              <div style={{ minWidth: 0, flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
                  <span
                    style={{
                      fontWeight: 600,
                      color: "var(--text-primary)",
                      fontSize: "0.95rem",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      maxWidth: "400px",
                    }}
                    title={doc.filename}
                  >
                    {doc.filename}
                  </span>
                  {getStatusBadge(doc.status)}
                </div>

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "16px",
                    fontSize: "0.8rem",
                    color: "var(--text-muted)",
                  }}
                >
                  <span>{formatFileSize(doc.file_size_bytes)}</span>
                  <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <BookOpen size={13} /> {doc.page_count} {doc.page_count === 1 ? "page" : "pages"}
                  </span>
                  <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <Layers size={13} /> {doc.chunk_count} {doc.chunk_count === 1 ? "chunk" : "chunks"}
                  </span>
                </div>
              </div>
            </div>

            {/* Right: Actions */}
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <button
                type="button"
                onClick={() => handleDelete(doc.id, doc.filename)}
                disabled={deletingId === doc.id}
                className="btn btn-secondary"
                style={{
                  padding: "8px 12px",
                  color: "var(--accent-rose)",
                  borderColor: "rgba(244, 63, 94, 0.2)",
                }}
                title="Delete document and cascaded vectors"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
