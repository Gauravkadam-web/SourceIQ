"use client";

import React, { useState } from "react";
import { DocumentItem, ComparisonResponse, CitationDetail, api } from "../lib/api";
import { GitCompare, Sparkles, CheckCircle2, AlertTriangle, AlertCircle, Info, Clock, CheckSquare, Square, ChevronRight } from "lucide-react";

interface ComparisonViewProps {
  workspaceId: string;
  documents: DocumentItem[];
  onSelectCitation: (citation: CitationDetail) => void;
}

export default function ComparisonView({
  workspaceId,
  documents,
  onSelectCitation,
}: ComparisonViewProps) {
  const [topic, setTopic] = useState("");
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [comparisonResult, setComparisonResult] = useState<ComparisonResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const readyDocuments = documents.filter((d) => d.status === "READY");

  const toggleDocument = (id: string) => {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((dId) => dId !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    if (selectedDocIds.length === readyDocuments.length) {
      setSelectedDocIds([]);
    } else {
      setSelectedDocIds(readyDocuments.map((d) => d.id));
    }
  };

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    if (selectedDocIds.length < 2) {
      setErrorMessage("Multi-document comparison requires selecting at least 2 documents.");
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setComparisonResult(null);

    try {
      const res = await api.compareDocuments(workspaceId, topic.trim(), selectedDocIds);
      setComparisonResult(res);
    } catch (err: any) {
      setErrorMessage(err.message || "Comparison failed. Please verify documents contain relevant text.");
    } finally {
      setLoading(false);
    }
  };

  const getRelationshipBadge = (rel: ComparisonResponse["relationship"]) => {
    switch (rel) {
      case "AGREEMENT":
        return (
          <span className="badge badge-success" style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
            <CheckCircle2 size={14} /> Full Agreement
          </span>
        );
      case "DIFFERENCE":
        return (
          <span className="badge badge-warning" style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
            <Info size={14} /> Material Difference
          </span>
        );
      case "CONTRADICTION":
        return (
          <span className="badge badge-danger" style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
            <AlertCircle size={14} /> Contradiction Detected
          </span>
        );
      case "DIFFERENT_SCOPES":
        return (
          <span
            className="badge"
            style={{
              fontSize: "0.85rem",
              padding: "6px 12px",
              backgroundColor: "rgba(99, 102, 241, 0.15)",
              color: "var(--accent-indigo)",
              border: "1px solid var(--accent-indigo)",
            }}
          >
            <AlertTriangle size={14} /> Incompatible Scopes / Contexts
          </span>
        );
      case "INSUFFICIENT_EVIDENCE":
      default:
        return (
          <span className="badge badge-secondary" style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
            <AlertCircle size={14} /> Insufficient Evidence
          </span>
        );
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* Configuration Card */}
      <div className="glass-panel" style={{ padding: "28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "var(--radius-md)",
              backgroundColor: "rgba(6, 182, 212, 0.1)",
              color: "var(--accent-cyan)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <GitCompare size={20} />
          </div>
          <div>
            <h2 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text-primary)" }}>
              Multi-Document Comparison (FR-07)
            </h2>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
              Compare specific topics across 2+ selected documents with evidence-backed findings and scope awareness.
            </p>
          </div>
        </div>

        <form onSubmit={handleCompare}>
          {/* Document Selection Checklist */}
          <div style={{ marginBottom: "20px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
              <label style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                Select Documents to Compare (Min 2 required):
              </label>
              {readyDocuments.length > 0 && (
                <button
                  type="button"
                  onClick={selectAll}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--accent-cyan)",
                    fontSize: "0.8rem",
                    cursor: "pointer",
                    textDecoration: "underline",
                  }}
                >
                  {selectedDocIds.length === readyDocuments.length ? "Deselect All" : "Select All"}
                </button>
              )}
            </div>

            {readyDocuments.length === 0 ? (
              <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontStyle: "italic" }}>
                No ingested documents ready in this workspace. Upload at least 2 PDFs in the Documents tab.
              </p>
            ) : (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
                  gap: "10px",
                }}
              >
                {readyDocuments.map((doc) => {
                  const isChecked = selectedDocIds.includes(doc.id);
                  return (
                    <div
                      key={doc.id}
                      onClick={() => toggleDocument(doc.id)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                        padding: "10px 14px",
                        borderRadius: "var(--radius-md)",
                        backgroundColor: isChecked ? "rgba(6, 182, 212, 0.08)" : "var(--bg-secondary)",
                        border: `1px solid ${isChecked ? "var(--accent-cyan)" : "var(--border-subtle)"}`,
                        cursor: "pointer",
                        transition: "all var(--transition-fast)",
                      }}
                    >
                      <span style={{ color: isChecked ? "var(--accent-cyan)" : "var(--text-muted)" }}>
                        {isChecked ? <CheckSquare size={18} /> : <Square size={18} />}
                      </span>
                      <span
                        style={{
                          fontSize: "0.875rem",
                          fontWeight: 500,
                          color: "var(--text-primary)",
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                        }}
                        title={doc.filename}
                      >
                        {doc.filename}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Topic Input */}
          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", fontSize: "0.9rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px" }}>
              Comparison Topic:
            </label>
            <input
              type="text"
              className="input-field"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Compare revenue growth, cloud operating margins, or risk factors"
              disabled={loading || readyDocuments.length < 2}
            />
          </div>

          {/* Submit Button */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              Selected: {selectedDocIds.length} of {readyDocuments.length} document(s)
            </span>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || selectedDocIds.length < 2 || !topic.trim()}
            >
              <Sparkles size={16} />
              {loading ? "Comparing Documents..." : "Run Evidence Comparison"}
            </button>
          </div>
        </form>

        {errorMessage && (
          <div
            style={{
              marginTop: "16px",
              padding: "12px 16px",
              backgroundColor: "var(--accent-rose-bg)",
              border: "1px solid var(--accent-rose)",
              borderRadius: "var(--radius-md)",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              color: "var(--accent-rose)",
              fontSize: "0.875rem",
            }}
          >
            <AlertCircle size={18} />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>

      {/* Comparison Results */}
      {comparisonResult && (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* Executive Synthesis Card */}
          <div className="glass-panel" style={{ padding: "28px" }}>
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
              <div>
                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Comparative Synthesis
                </span>
                <h3 style={{ fontSize: "1.2rem", fontWeight: 600, color: "var(--text-primary)" }}>
                  Topic: "{comparisonResult.topic}"
                </h3>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                {getRelationshipBadge(comparisonResult.relationship)}
                <span style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  <Clock size={13} /> {(comparisonResult.latency_ms / 1000).toFixed(2)}s
                </span>
              </div>
            </div>

            <p style={{ fontSize: "1rem", lineHeight: 1.7, color: "var(--text-primary)", marginBottom: "16px" }}>
              {comparisonResult.synthesis}
            </p>

            {comparisonResult.scope_notes && (
              <div
                style={{
                  padding: "12px 16px",
                  borderRadius: "var(--radius-md)",
                  backgroundColor: "rgba(99, 102, 241, 0.08)",
                  border: "1px solid rgba(99, 102, 241, 0.3)",
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "10px",
                  fontSize: "0.875rem",
                  color: "#c7d2fe",
                }}
              >
                <Info size={18} style={{ flexShrink: 0, marginTop: "2px" }} />
                <div>
                  <strong style={{ color: "#fff" }}>Scope Caveat: </strong>
                  {comparisonResult.scope_notes}
                </div>
              </div>
            )}
          </div>

          {/* Per-Document Findings */}
          <div>
            <h4 style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "16px" }}>
              Individual Document Findings ({comparisonResult.document_findings.length})
            </h4>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "16px" }}>
              {comparisonResult.document_findings.map((finding) => (
                <div
                  key={finding.document_id}
                  className="glass-panel"
                  style={{
                    padding: "20px",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
                      <span
                        style={{
                          fontWeight: 600,
                          fontSize: "0.95rem",
                          color: "var(--accent-cyan)",
                          whiteSpace: "nowrap",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          maxWidth: "240px",
                        }}
                        title={finding.document_name}
                      >
                        {finding.document_name}
                      </span>
                      {finding.has_sufficient_evidence ? (
                        <span className="badge badge-success" style={{ fontSize: "0.75rem" }}>
                          Evidence Found
                        </span>
                      ) : (
                        <span className="badge badge-secondary" style={{ fontSize: "0.75rem" }}>
                          No Direct Evidence
                        </span>
                      )}
                    </div>

                    <p style={{ fontSize: "0.875rem", color: "var(--text-primary)", lineHeight: 1.6, marginBottom: "16px" }}>
                      {finding.summary}
                    </p>
                  </div>

                  {/* Citations */}
                  {finding.citations.length > 0 && (
                    <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "12px" }}>
                      <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginBottom: "8px" }}>
                        Referenced Sources:
                      </span>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                        {finding.citations.map((cit, idx) => (
                          <button
                            key={idx}
                            type="button"
                            className="citation-badge"
                            onClick={() => onSelectCitation(cit)}
                            title={`Inspect Page ${cit.page_number} chunk in ${cit.document_name}`}
                          >
                            [{cit.citation_key}] Page {cit.page_number}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
