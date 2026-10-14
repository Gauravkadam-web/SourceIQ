"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useWorkspace } from "../context/WorkspaceContext";
import { ShieldCheck, MessageSquare, GitCompare, Files, Activity, Plus, ChevronDown, Check } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();
  const { workspaces, activeWorkspace, setActiveWorkspace, createWorkspace } = useWorkspace();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [newWsName, setNewWsName] = useState("");

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWsName.trim()) return;
    await createWorkspace(newWsName.trim());
    setNewWsName("");
    setShowModal(false);
  };

  const navLinks = [
    { href: "/", label: "Grounded Q&A", icon: MessageSquare },
    { href: "/compare", label: "Multi-Doc Compare", icon: GitCompare },
    { href: "/documents", label: "Documents", icon: Files },
    { href: "/evaluation", label: "Benchmark Suite", icon: Activity },
  ];

  return (
    <>
      <header
        style={{
          borderBottom: "1px solid var(--border-subtle)",
          background: "rgba(10, 14, 23, 0.8)",
          backdropFilter: "blur(12px)",
          position: "sticky",
          top: 0,
          zIndex: 40,
        }}
      >
        <div
          style={{
            maxWidth: "1400px",
            margin: "0 auto",
            padding: "0 24px",
            height: "64px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          {/* Logo & Tagline */}
          <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
            <Link href="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "10px" }}>
              <div
                style={{
                  width: "36px",
                  height: "36px",
                  borderRadius: "10px",
                  background: "linear-gradient(135deg, #06b6d4, #6366f1)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 0 15px rgba(6, 182, 212, 0.3)",
                }}
              >
                <ShieldCheck size={22} color="#07090e" strokeWidth={2.5} />
              </div>
              <div>
                <span
                  style={{
                    fontSize: "1.2rem",
                    fontWeight: 700,
                    letterSpacing: "-0.02em",
                    color: "var(--text-primary)",
                  }}
                >
                  Source<span style={{ color: "var(--accent-cyan)" }}>IQ</span>
                </span>
                <span
                  style={{
                    display: "block",
                    fontSize: "0.65rem",
                    color: "var(--text-muted)",
                    fontWeight: 500,
                    letterSpacing: "0.02em",
                    marginTop: "-2px",
                  }}
                >
                  AI Answers. Verifiable Sources.
                </span>
              </div>
            </Link>

            {/* Navigation Tabs */}
            <nav style={{ display: "flex", alignItems: "center", gap: "6px", marginLeft: "16px" }}>
              {navLinks.map((tab) => {
                const Icon = tab.icon;
                const isActive = pathname === tab.href;
                return (
                  <Link
                    key={tab.href}
                    href={tab.href}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      padding: "8px 14px",
                      borderRadius: "var(--radius-md)",
                      fontSize: "0.85rem",
                      fontWeight: 500,
                      textDecoration: "none",
                      color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                      background: isActive ? "rgba(6, 182, 212, 0.12)" : "transparent",
                      border: isActive ? "1px solid rgba(6, 182, 212, 0.3)" : "1px solid transparent",
                      transition: "all var(--transition-fast)",
                    }}
                  >
                    <Icon size={16} color={isActive ? "var(--accent-cyan)" : "var(--text-muted)"} />
                    {tab.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Workspace Switcher & Status */}
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div style={{ position: "relative" }}>
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="btn btn-secondary"
                style={{ padding: "7px 14px", fontSize: "0.82rem" }}
              >
                <span
                  style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    background: "var(--accent-emerald)",
                    boxShadow: "0 0 8px var(--accent-emerald)",
                  }}
                />
                <span style={{ maxWidth: "160px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {activeWorkspace?.name || "Select Workspace"}
                </span>
                <ChevronDown size={14} color="var(--text-muted)" />
              </button>

              {dropdownOpen && (
                <div
                  style={{
                    position: "absolute",
                    right: 0,
                    top: "calc(100% + 8px)",
                    width: "240px",
                    background: "var(--bg-card)",
                    border: "1px solid var(--border-subtle)",
                    borderRadius: "var(--radius-md)",
                    boxShadow: "var(--shadow-lg)",
                    zIndex: 50,
                    overflow: "hidden",
                  }}
                >
                  <div style={{ padding: "8px 12px", borderBottom: "1px solid var(--border-subtle)", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    Workspaces ({workspaces.length})
                  </div>
                  <div style={{ maxHeight: "200px", overflowY: "auto" }}>
                    {workspaces.map((ws) => (
                      <button
                        key={ws.id}
                        onClick={() => {
                          setActiveWorkspace(ws);
                          setDropdownOpen(false);
                        }}
                        style={{
                          width: "100%",
                          padding: "10px 12px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          background: ws.id === activeWorkspace?.id ? "rgba(6, 182, 212, 0.1)" : "transparent",
                          border: "none",
                          color: ws.id === activeWorkspace?.id ? "var(--accent-cyan)" : "var(--text-primary)",
                          fontSize: "0.84rem",
                          cursor: "pointer",
                          textAlign: "left",
                        }}
                      >
                        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{ws.name}</span>
                        {ws.id === activeWorkspace?.id && <Check size={14} />}
                      </button>
                    ))}
                  </div>
                  <div style={{ borderTop: "1px solid var(--border-subtle)", padding: "6px" }}>
                    <button
                      onClick={() => {
                        setDropdownOpen(false);
                        setShowModal(true);
                      }}
                      style={{
                        width: "100%",
                        padding: "8px",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        background: "transparent",
                        border: "none",
                        color: "var(--accent-cyan)",
                        fontSize: "0.82rem",
                        cursor: "pointer",
                        fontWeight: 500,
                      }}
                    >
                      <Plus size={14} /> New Workspace
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* New Workspace Modal */}
      {showModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0, 0, 0, 0.75)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          }}
        >
          <div
            className="glass-panel"
            style={{ width: "400px", padding: "24px", background: "var(--bg-card)" }}
          >
            <h3 style={{ fontSize: "1.1rem", marginBottom: "8px", fontWeight: 600 }}>Create New Workspace</h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "16px" }}>
              Workspaces isolate documents, vectors, queries, and citations.
            </p>
            <form onSubmit={handleCreate}>
              <input
                type="text"
                value={newWsName}
                onChange={(e) => setNewWsName(e.target.value)}
                placeholder="Workspace name (e.g. Q4 Financials)"
                autoFocus
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  background: "var(--bg-primary)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "var(--radius-md)",
                  color: "var(--text-primary)",
                  fontSize: "0.9rem",
                  marginBottom: "20px",
                  outline: "none",
                }}
              />
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={!newWsName.trim()} className="btn btn-primary">
                  Create Workspace
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
