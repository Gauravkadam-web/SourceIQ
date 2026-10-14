"use client";

import React, { useState, useEffect } from "react";
import { useWorkspace } from "../../context/WorkspaceContext";
import { api, DocumentItem, CitationDetail } from "../../lib/api";
import ComparisonView from "../../components/ComparisonView";
import EvidenceDrawer from "../../components/EvidenceDrawer";
import { GitCompare, Loader2 } from "lucide-react";

export default function ComparePage() {
  const { activeWorkspace, isLoading: wsLoading } = useWorkspace();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedCitation, setSelectedCitation] = useState<CitationDetail | null>(null);

  useEffect(() => {
    if (activeWorkspace) {
      api
        .listDocuments(activeWorkspace.id)
        .then((docs) => setDocuments(docs))
        .catch((err) => console.error("Failed to load documents for comparison:", err));
    }
  }, [activeWorkspace]);

  if (wsLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "400px" }}>
        <Loader2 size={36} className="animate-spin" style={{ color: "var(--accent-cyan)" }} />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "28px" }}>
      {activeWorkspace && (
        <ComparisonView
          workspaceId={activeWorkspace.id}
          documents={documents}
          onSelectCitation={(cit) => setSelectedCitation(cit)}
        />
      )}

      {/* Evidence Drawer */}
      <EvidenceDrawer citation={selectedCitation} onClose={() => setSelectedCitation(null)} />
    </div>
  );
}
