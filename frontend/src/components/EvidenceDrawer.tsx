"use client";

import React, { useEffect, useState } from "react";
import { api, CitationDetail, EvidenceDetail } from "../lib/api";
import { X, FileText, CheckCircle2, Bookmark, Layers, Loader2 } from "lucide-react";

interface EvidenceDrawerProps {
  citation: CitationDetail | null;
  onClose: () => void;
}

export default function EvidenceDrawer({ citation, onClose }: EvidenceDrawerProps) {
  const [evidence, setEvidence] = useState<EvidenceDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!citation) {
      setEvidence(null);
      return;
    }

    const fetchEvidence = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getEvidence(citation.chunk_id);
        setEvidence(data);
      } catch (err: any) {
        setError(err.message || "Failed to load evidence context");
      } finally {
        setLoading(false);
      }
    };

    fetchEvidence();
  }, [citation]);

  if (!citation) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 90,
        background: "rgba(0, 0, 0, 0.6)",
        backdropFilter: "blur(4px)",
        display: "flex",
        justifyContent: "flex-end",
      }}
      onClick={onClose}
    >
      <div
        className="slide-in-right"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "100%",
          maxWidth: "520px",
          height: "100%",
          background: "var(--bg-secondary)",
          borderLeft: "1px solid var(--border-subtle)",
          boxShadow: "-8px 0 25px rgba(0, 0, 0, 0.7)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "20px 24px",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            background: "rgba(19, 27, 42, 0.5)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span className="citation-badge" style={{ fontSize: "0.9rem", padding: "3px 10px" }}>
              {citation.citation_key}
            </span>
            <span style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>
              Evidence Provenance
            </span>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--text-muted)",
              cursor: "pointer",
              padding: "4px",
              borderRadius: "var(--radius-sm)",
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        <div style={{ padding: "24px", overflowY: "auto", flex: 1, display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Metadata Card */}
          <div
            style={{
              padding: "16px",
              borderRadius: "var(--radius-md)",
              background: "var(--bg-card)",
              border: "1px solid var(--border-subtle)",
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "12px",
            }}
          >
            <div>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Source Document
              </div>
              <div style={{ fontSize: "0.85rem", fontWeight: 500, color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "6px", marginTop: "4px" }}>
                <FileText size={15} color="var(--accent-cyan)" />
                <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {citation.document_name}
                </span>
              </div>
            </div>

            <div>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Source Page
              </div>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--accent-cyan)", marginTop: "4px" }}>
                Page {citation.page_number}
              </div>
            </div>

            <div>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Vector Similarity
              </div>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--accent-emerald)", marginTop: "4px" }}>
                {Math.round(citation.similarity_score * 100)}% Match
              </div>
            </div>

            <div>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Server Validation
              </div>
              <div style={{ fontSize: "0.85rem", fontWeight: 500, color: "var(--accent-emerald)", display: "flex", alignItems: "center", gap: "5px", marginTop: "4px" }}>
                <CheckCircle2 size={14} /> Verified Ground
              </div>
            </div>
          </div>

          {/* Supported Claim */}
          {citation.claim && (
            <div>
              <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
                <Bookmark size={14} color="var(--accent-cyan)" /> Supported Claim
              </div>
              <div
                style={{
                  padding: "12px 14px",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(6, 182, 212, 0.08)",
                  border: "1px solid rgba(6, 182, 212, 0.25)",
                  fontSize: "0.85rem",
                  color: "var(--text-primary)",
                  fontStyle: "italic",
                }}
              >
                &ldquo;{citation.claim}&rdquo;
              </div>
            </div>
          )}

          {/* Quoted Snippet */}
          <div>
            <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
              <FileText size={14} color="var(--accent-emerald)" /> Exact Quoted Passage
            </div>
            <div
              style={{
                padding: "16px",
                borderRadius: "var(--radius-md)",
                background: "var(--bg-card)",
                border: "1px solid var(--border-subtle)",
                fontSize: "0.88rem",
                lineHeight: "1.6",
                color: "#e2e8f0",
                borderLeft: "3px solid var(--accent-cyan)",
              }}
            >
              {citation.quoted_snippet}
            </div>
          </div>

          {/* Surrounding Context Section */}
          <div>
            <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px", display: "flex", alignItems: "center", gap: "6px" }}>
              <Layers size={14} color="var(--text-muted)" /> Adjacent Document Context
            </div>
            {loading ? (
              <div style={{ padding: "20px", display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", color: "var(--text-muted)", fontSize: "0.85rem" }}>
                <Loader2 size={16} className="animate-spin" /> Loading surrounding text...
              </div>
            ) : error ? (
              <div style={{ padding: "12px", color: "var(--accent-rose)", fontSize: "0.82rem" }}>{error}</div>
            ) : evidence?.surrounding_context ? (
              <div
                style={{
                  padding: "16px",
                  borderRadius: "var(--radius-md)",
                  background: "var(--bg-primary)",
                  border: "1px solid var(--border-subtle)",
                  fontSize: "0.82rem",
                  color: "var(--text-muted)",
                  lineHeight: "1.7",
                  whiteSpace: "pre-wrap",
                  fontFamily: "var(--font-mono)",
                  maxHeight: "220px",
                  overflowY: "auto",
                }}
              >
                {evidence.surrounding_context}
              </div>
            ) : null}
          </div>
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "16px 24px",
            borderTop: "1px solid var(--border-subtle)",
            background: "rgba(10, 14, 23, 0.6)",
            display: "flex",
            justifyContent: "flex-end",
          }}
        >
          <button onClick={onClose} className="btn btn-secondary" style={{ width: "100%" }}>
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
