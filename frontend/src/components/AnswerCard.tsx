"use client";

import React from "react";
import { QueryResponse, CitationDetail } from "../lib/api";
import { ShieldCheck, CheckCircle2, Clock, Copy, Check, ExternalLink } from "lucide-react";

interface AnswerCardProps {
  response: QueryResponse;
  onSelectCitation: (citation: CitationDetail) => void;
}

export default function AnswerCard({ response, onSelectCitation }: AnswerCardProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(response.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper to parse answer string and render interactive citation tags
  const renderFormattedAnswer = (text: string) => {
    // Regex for [CIT-X] or [DOCX-CIT-Y]
    const regex = /(\[(?:DOC\d+-)?CIT-\d+\])/g;
    const parts = text.split(regex);

    return parts.map((part, index) => {
      if (regex.test(part)) {
        const cleanKey = part.replace(/[\[\]]/g, "");
        const citation = response.citations.find((c) => c.citation_key === cleanKey);

        return (
          <button
            key={index}
            className="citation-badge"
            title={citation ? `Page ${citation.page_number} in ${citation.document_name}` : "Click to view evidence"}
            onClick={() => {
              if (citation) onSelectCitation(citation);
            }}
          >
            {part}
          </button>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="glass-panel" style={{ padding: "28px", marginTop: "24px" }}>
      {/* Header Bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid var(--border-subtle)",
          paddingBottom: "16px",
          marginBottom: "20px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "8px",
              background: "var(--accent-emerald-bg)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <ShieldCheck size={18} color="var(--accent-emerald)" />
          </div>
          <div>
            <h3 style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--text-primary)" }}>
              Grounded Answer
            </h3>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
              Traced to {response.citations.length} verified passage{response.citations.length !== 1 ? "s" : ""}
            </span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span className="badge badge-ready">
            <CheckCircle2 size={12} /> {response.status}
          </span>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "4px" }}>
            <Clock size={12} /> {Math.round(response.latency_ms)} ms
          </span>
          <button
            onClick={handleCopy}
            className="btn btn-secondary"
            style={{ padding: "6px 10px", fontSize: "0.75rem" }}
            title="Copy answer"
          >
            {copied ? <Check size={13} color="var(--accent-emerald)" /> : <Copy size={13} />}
          </button>
        </div>
      </div>

      {/* Answer Body */}
      <div
        style={{
          fontSize: "1rem",
          lineHeight: "1.75",
          color: "#f1f5f9",
          marginBottom: "28px",
        }}
      >
        {renderFormattedAnswer(response.answer)}
      </div>

      {/* Verifiable Citations Tray */}
      {response.citations.length > 0 && (
        <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "20px" }}>
          <div
            style={{
              fontSize: "0.8rem",
              fontWeight: 600,
              color: "var(--text-secondary)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              marginBottom: "14px",
            }}
          >
            Verifiable Source Evidence ({response.citations.length})
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
              gap: "14px",
            }}
          >
            {response.citations.map((cit) => (
              <div
                key={cit.chunk_id + cit.citation_key}
                style={{
                  background: "var(--bg-card)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "var(--radius-md)",
                  padding: "16px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  transition: "all var(--transition-fast)",
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                    <span className="citation-badge">{cit.citation_key}</span>
                    <span style={{ fontSize: "0.78rem", color: "var(--accent-cyan)", fontWeight: 500 }}>
                      Page {cit.page_number}
                    </span>
                  </div>

                  <div
                    style={{
                      fontSize: "0.82rem",
                      fontWeight: 600,
                      color: "var(--text-primary)",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      marginBottom: "8px",
                    }}
                  >
                    {cit.document_name}
                  </div>

                  <p
                    style={{
                      fontSize: "0.82rem",
                      color: "var(--text-secondary)",
                      lineHeight: "1.5",
                      fontStyle: "italic",
                      display: "-webkit-box",
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: "vertical",
                      overflow: "hidden",
                    }}
                  >
                    &ldquo;{cit.quoted_snippet}&rdquo;
                  </p>
                </div>

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginTop: "14px",
                    paddingTop: "10px",
                    borderTop: "1px solid rgba(255, 255, 255, 0.05)",
                  }}
                >
                  <span style={{ fontSize: "0.75rem", color: "var(--accent-emerald)" }}>
                    {Math.round(cit.similarity_score * 100)}% Similarity
                  </span>
                  <button
                    onClick={() => onSelectCitation(cit)}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "var(--accent-cyan)",
                      fontSize: "0.78rem",
                      fontWeight: 500,
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    Inspect Source <ExternalLink size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
