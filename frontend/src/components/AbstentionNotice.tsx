"use client";

import React from "react";
import { AlertCircle, FileSearch, HelpCircle } from "lucide-react";

interface AbstentionNoticeProps {
  question: string;
  answerText?: string;
  explanation?: string;
}

export default function AbstentionNotice({ question, answerText, explanation }: AbstentionNoticeProps) {
  const displayText = explanation || answerText || "I could not find sufficient evidence in the uploaded documents to answer your question.";
  return (
    <div
      className="glass-panel"
      style={{
        padding: "24px",
        marginTop: "24px",
        borderLeft: "4px solid var(--accent-amber)",
        background: "rgba(245, 158, 11, 0.05)",
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: "16px" }}>
        <div
          style={{
            width: "36px",
            height: "36px",
            borderRadius: "10px",
            background: "var(--accent-amber-bg)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          <AlertCircle size={20} color="var(--accent-amber)" />
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--text-primary)" }}>
              Honest Abstention: Insufficient Supporting Evidence
            </h3>
            <span className="badge badge-pending">ABSTAINED</span>
          </div>

          <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)", lineHeight: "1.6", marginBottom: "14px" }}>
            {displayText}
          </p>

          <div
            style={{
              padding: "12px 16px",
              borderRadius: "var(--radius-md)",
              background: "var(--bg-card)",
              border: "1px solid var(--border-subtle)",
              display: "flex",
              flexDirection: "column",
              gap: "6px",
              fontSize: "0.8rem",
              color: "var(--text-muted)",
            }}
          >
            <div style={{ fontWeight: 600, color: "var(--text-secondary)", display: "flex", alignItems: "center", gap: "6px" }}>
              <HelpCircle size={14} color="var(--accent-cyan)" /> How SourceIQ Handles Uncertainty:
            </div>
            <div>• Unlike conventional web assistants, SourceIQ will not guess or extrapolate ungrounded claims.</div>
            <div>• Ensure the target document is uploaded to the active workspace and has finished processing.</div>
            <div>• Try broadening the question or querying specific sections of the document.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
