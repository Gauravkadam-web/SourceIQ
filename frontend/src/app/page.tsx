"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useWorkspace } from "../context/WorkspaceContext";
import { api, QueryResponse, CitationDetail, DocumentItem } from "../lib/api";
import AnswerCard from "../components/AnswerCard";
import AbstentionNotice from "../components/AbstentionNotice";
import EvidenceDrawer from "../components/EvidenceDrawer";
import { Sparkles, Search, Files, ArrowRight, Loader2, HelpCircle, ShieldCheck } from "lucide-react";

export default function HomePage() {
  const { activeWorkspace, isLoading: wsLoading } = useWorkspace();
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<CitationDetail | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load documents for current workspace
  useEffect(() => {
    if (activeWorkspace) {
      api
        .listDocuments(activeWorkspace.id)
        .then((docs) => setDocuments(docs.filter((d) => d.status === "READY")))
        .catch((err) => console.error("Failed to load documents:", err));
    }
  }, [activeWorkspace]);

  const handleQuery = async (queryText?: string) => {
    const q = (queryText || question).trim();
    if (!q || !activeWorkspace) return;

    setLoading(true);
    setErrorMessage(null);
    setResponse(null);

    try {
      const res = await api.queryQA(
        activeWorkspace.id,
        q,
        selectedDocIds.length > 0 ? selectedDocIds : undefined
      );
      setResponse(res);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to process query.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  const samplePrompts = [
    "What was the enterprise cloud revenue and growth rate in 2024?",
    "What were the operating margins and R&D expenditures?",
    "What was the company's rocket launch velocity on Mars in 2024?",
  ];

  if (wsLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "400px" }}>
        <Loader2 size={36} className="animate-spin" style={{ color: "var(--accent-cyan)" }} />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* Hero Banner */}
      <div style={{ textAlign: "center", padding: "20px 0 10px" }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "6px 14px",
            borderRadius: "var(--radius-full)",
            backgroundColor: "rgba(6, 182, 212, 0.1)",
            border: "1px solid rgba(6, 182, 212, 0.3)",
            color: "var(--accent-cyan)",
            fontSize: "0.85rem",
            fontWeight: 500,
            marginBottom: "16px",
          }}
        >
          <ShieldCheck size={16} />
          <span>Evidence-First Document Intelligence</span>
        </div>
        <h1
          style={{
            fontSize: "2.5rem",
            fontWeight: 700,
            letterSpacing: "-0.02em",
            marginBottom: "10px",
            background: "linear-gradient(135deg, #ffffff 40%, #94a3b8 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          AI Answers. Verifiable Sources.
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "1.05rem", maxWidth: "600px", margin: "0 auto" }}>
          Ask questions across your PDFs. Every fact is validated against stored evidence with exact page numbers.
        </p>
      </div>

      {/* Query Search Card */}
      <div className="glass-panel" style={{ padding: "24px" }}>
        <div style={{ position: "relative", marginBottom: "14px" }}>
          <Search
            size={20}
            style={{
              position: "absolute",
              left: "16px",
              top: "50%",
              transform: "translateY(-50%)",
              color: "var(--text-muted)",
            }}
          />
          <input
            type="text"
            className="input-field"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              documents.length > 0
                ? "Ask a question about your uploaded documents..."
                : "Please upload documents first in the Documents tab..."
            }
            disabled={loading || !activeWorkspace}
            style={{
              paddingLeft: "48px",
              paddingRight: "120px",
              fontSize: "1rem",
              height: "52px",
            }}
          />
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => handleQuery()}
            disabled={loading || !question.trim() || !activeWorkspace}
            style={{
              position: "absolute",
              right: "8px",
              top: "50%",
              transform: "translateY(-50%)",
              height: "38px",
              padding: "0 16px",
            }}
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <>
                <span>Ask</span>
                <Sparkles size={15} />
              </>
            )}
          </button>
        </div>

        {/* Document Scope & Stats Bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "12px",
            fontSize: "0.85rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-muted)" }}>
            <Files size={16} />
            <span>Workspace: <strong>{activeWorkspace?.name}</strong></span>
            <span>({documents.length} {documents.length === 1 ? "document ready" : "documents ready"})</span>
          </div>

          {documents.length === 0 && (
            <Link
              href="/documents"
              style={{
                color: "var(--accent-cyan)",
                textDecoration: "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                fontWeight: 500,
              }}
            >
              Upload PDF Documents <ArrowRight size={14} />
            </Link>
          )}
        </div>

        {/* Suggestion Prompts */}
        {documents.length > 0 && (
          <div style={{ marginTop: "18px", borderTop: "1px solid var(--border-subtle)", paddingTop: "14px" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginBottom: "8px" }}>
              Suggested inquiries:
            </span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {samplePrompts.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setQuestion(p);
                    handleQuery(p);
                  }}
                  className="btn btn-secondary"
                  style={{ fontSize: "0.8rem", padding: "6px 12px", borderRadius: "var(--radius-full)" }}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div
          style={{
            padding: "16px 20px",
            backgroundColor: "var(--accent-rose-bg)",
            border: "1px solid var(--accent-rose)",
            borderRadius: "var(--radius-md)",
            color: "var(--accent-rose)",
            fontSize: "0.9rem",
          }}
        >
          {errorMessage}
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="glass-panel" style={{ padding: "32px", textAlign: "center" }}>
          <Loader2 size={32} className="animate-spin" style={{ margin: "0 auto 12px", color: "var(--accent-cyan)" }} />
          <h3 style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>
            Retrieving Verifiable Evidence...
          </h3>
          <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            Querying pgvector embeddings & validating source page citations on server.
          </p>
        </div>
      )}

      {/* Grounded Answer Response */}
      {response && response.status === "GROUNDED" && (
        <AnswerCard response={response} onSelectCitation={(cit) => setSelectedCitation(cit)} />
      )}

      {/* Honest Abstention Banner */}
      {response && response.status === "INSUFFICIENT_EVIDENCE" && (
        <AbstentionNotice
          question={response.question}
          explanation="SourceIQ searched the vector database for your query, but could not find high-confidence evidence in the uploaded documents. Rather than speculating or hallucinating, the system abstains."
        />
      )}

      {/* Evidence Drawer */}
      <EvidenceDrawer citation={selectedCitation} onClose={() => setSelectedCitation(null)} />
    </div>
  );
}
