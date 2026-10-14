"use client";

import React, { useState } from "react";
import { EvalReportResponse, api } from "../lib/api";
import { Activity, Play, CheckCircle2, XCircle, Clock, Target, ShieldAlert, Cpu } from "lucide-react";

export default function EvaluationDashboard() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<EvalReportResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleRunEvaluation = async () => {
    setLoading(true);
    setErrorMessage(null);

    try {
      const res = await api.runEvaluation();
      setReport(res);
    } catch (err: any) {
      setErrorMessage(err.message || "Evaluation failed to run.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* Header and Trigger Banner */}
      <div className="glass-panel" style={{ padding: "28px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div
              style={{
                width: "44px",
                height: "44px",
                borderRadius: "var(--radius-md)",
                backgroundColor: "rgba(6, 182, 212, 0.1)",
                color: "var(--accent-cyan)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Activity size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text-primary)" }}>
                Curated Evaluation Benchmark (FR-08)
              </h2>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Repeatable automated evaluation suite verifying retrieval recall, citation precision, and honest abstention.
              </p>
            </div>
          </div>

          <button
            type="button"
            className="btn btn-primary"
            onClick={handleRunEvaluation}
            disabled={loading}
          >
            <Play size={16} />
            {loading ? "Running Benchmark..." : "Execute Benchmark Suite"}
          </button>
        </div>

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
            <ShieldAlert size={18} />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>

      {/* KPI Cards Grid */}
      {report && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "16px",
            }}
          >
            {/* Overall Pass Rate */}
            <div className="glass-panel" style={{ padding: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontWeight: 500 }}>
                  Overall Pass Rate
                </span>
                <Target size={18} style={{ color: "var(--accent-cyan)" }} />
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "var(--text-primary)" }}>
                {report.total_questions > 0
                  ? ((report.passed_count / report.total_questions) * 100).toFixed(1)
                  : 0}
                %
              </div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                {report.passed_count} of {report.total_questions} questions passed
              </span>
            </div>

            {/* Retrieval Hit Rate */}
            <div className="glass-panel" style={{ padding: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontWeight: 500 }}>
                  Retrieval Hit Rate
                </span>
                <CheckCircle2 size={18} style={{ color: "var(--accent-emerald)" }} />
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "var(--accent-emerald)" }}>
                {report.retrieval_hit_rate_pct.toFixed(1)}%
              </div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Ground-truth evidence recalled
              </span>
            </div>

            {/* Citation Validity */}
            <div className="glass-panel" style={{ padding: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontWeight: 500 }}>
                  Citation Validity
                </span>
                <Target size={18} style={{ color: "var(--accent-cyan)" }} />
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "var(--accent-cyan)" }}>
                {report.citation_validity_pct.toFixed(1)}%
              </div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Verifiable source page matches
              </span>
            </div>

            {/* Negative Control Abstention */}
            <div className="glass-panel" style={{ padding: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontWeight: 500 }}>
                  Honest Abstention
                </span>
                <ShieldAlert size={18} style={{ color: "var(--accent-amber)" }} />
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "var(--accent-amber)" }}>
                {report.negative_control_abstention_pct.toFixed(1)}%
              </div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Zero hallucinations on ungrounded queries
              </span>
            </div>

            {/* Average Latency */}
            <div className="glass-panel" style={{ padding: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontWeight: 500 }}>
                  Avg Latency
                </span>
                <Clock size={18} style={{ color: "var(--text-muted)" }} />
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "var(--text-primary)" }}>
                {report.average_latency_ms.toFixed(0)} ms
              </div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Retrieval + Generation speed
              </span>
            </div>
          </div>

          {/* Detailed Results Table */}
          <div className="glass-panel" style={{ padding: "24px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-primary)" }}>
                Benchmark Test Cases ({report.results.length})
              </h3>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  fontSize: "0.75rem",
                  color: "var(--text-muted)",
                }}
              >
                <Cpu size={14} /> Deterministic Verification
              </span>
            </div>

            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border-subtle)", textAlign: "left" }}>
                    <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: 600 }}>Status</th>
                    <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: 600 }}>Category</th>
                    <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: 600 }}>Question</th>
                    <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: 600 }}>Expected Behavior</th>
                    <th style={{ padding: "12px 14px", color: "var(--text-muted)", fontWeight: 600 }}>Actual Behavior</th>
                  </tr>
                </thead>
                <tbody>
                  {report.results.map((item) => (
                    <tr
                      key={item.id}
                      style={{
                        borderBottom: "1px solid rgba(255, 255, 255, 0.04)",
                        transition: "background var(--transition-fast)",
                      }}
                    >
                      <td style={{ padding: "14px", verticalAlign: "top" }}>
                        {item.passed ? (
                          <span className="badge badge-success" style={{ fontSize: "0.75rem" }}>
                            <CheckCircle2 size={12} /> PASS
                          </span>
                        ) : (
                          <span className="badge badge-danger" style={{ fontSize: "0.75rem" }}>
                            <XCircle size={12} /> FAIL
                          </span>
                        )}
                      </td>
                      <td style={{ padding: "14px", color: "var(--accent-cyan)", verticalAlign: "top", fontWeight: 500 }}>
                        {item.category}
                      </td>
                      <td style={{ padding: "14px", color: "var(--text-primary)", verticalAlign: "top", maxWidth: "300px" }}>
                        {item.question}
                      </td>
                      <td style={{ padding: "14px", color: "var(--text-secondary)", verticalAlign: "top" }}>
                        {item.expected_behavior}
                      </td>
                      <td style={{ padding: "14px", color: "var(--text-muted)", verticalAlign: "top" }}>
                        {item.actual_behavior}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
