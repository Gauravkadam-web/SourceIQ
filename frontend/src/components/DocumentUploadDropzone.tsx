"use client";

import React, { useState, useRef, DragEvent, ChangeEvent } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { api, DocumentItem } from "../lib/api";

interface DocumentUploadDropzoneProps {
  workspaceId: string;
  onUploadSuccess?: (doc: DocumentItem) => void;
}

export default function DocumentUploadDropzone({
  workspaceId,
  onUploadSuccess,
}: DocumentUploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const pollDocumentStatus = async (docId: string) => {
    let attempts = 0;
    const maxAttempts = 30; // 30 seconds max polling
    const interval = 1000;

    const poll = async () => {
      attempts++;
      try {
        const doc = await api.getDocument(workspaceId, docId);
        if (doc.status === "READY") {
          setIsUploading(false);
          setUploadStatus("Ingestion complete! Document ready for retrieval.");
          if (onUploadSuccess) onUploadSuccess(doc);
          setTimeout(() => setUploadStatus(null), 4000);
          return;
        } else if (doc.status === "FAILED") {
          setIsUploading(false);
          setErrorMessage(doc.error_message || "Document processing failed.");
          return;
        } else {
          setUploadStatus(`Processing: ${doc.status.toLowerCase()} (${attempts}s)...`);
          if (attempts < maxAttempts) {
            setTimeout(poll, interval);
          } else {
            setIsUploading(false);
            setUploadStatus("Processing is taking longer in the background. Check document list shortly.");
          }
        }
      } catch (err: any) {
        setIsUploading(false);
        setErrorMessage(err.message || "Failed to poll document status.");
      }
    };

    poll();
  };

  const handleFile = async (file: File) => {
    setErrorMessage(null);
    setUploadStatus(null);

    // Validate type
    if (!file.name.toLowerCase().endsWith(".pdf") && file.type !== "application/pdf") {
      setErrorMessage("Unsupported file type. SourceIQ only accepts text-based PDF documents.");
      return;
    }

    // Validate size (10 MB max)
    const maxBytes = 10 * 1024 * 1024;
    if (file.size > maxBytes) {
      setErrorMessage(`File is too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Maximum allowed size is 10 MB.`);
      return;
    }

    setIsUploading(true);
    setUploadStatus("Uploading PDF to workspace storage...");

    try {
      const doc = await api.uploadDocument(workspaceId, file);
      setUploadStatus("Parsing text & generating page-aware vector embeddings...");
      await pollDocumentStatus(doc.id);
    } catch (err: any) {
      setIsUploading(false);
      setErrorMessage(err.message || "Upload failed. Please check backend connection.");
    }
  };

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div style={{ width: "100%" }}>
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${isDragging ? "var(--accent-cyan)" : "var(--border-active)"}`,
          borderRadius: "var(--radius-lg)",
          backgroundColor: isDragging ? "var(--accent-cyan-glow)" : "rgba(19, 27, 42, 0.4)",
          padding: "48px 24px",
          textAlign: "center",
          cursor: isUploading ? "wait" : "pointer",
          transition: "all var(--transition-normal)",
          position: "relative",
          backdropFilter: "blur(12px)",
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          onChange={onFileChange}
          style={{ display: "none" }}
          disabled={isUploading}
        />

        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "14px" }}>
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "50%",
              backgroundColor: isDragging ? "var(--accent-cyan)" : "var(--bg-secondary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: isDragging ? "#000" : "var(--accent-cyan)",
              border: "1px solid var(--border-subtle)",
              transition: "all var(--transition-fast)",
            }}
          >
            {isUploading ? (
              <Loader2 size={28} className="animate-spin" style={{ animation: "spin 1s linear infinite" }} />
            ) : (
              <UploadCloud size={28} />
            )}
          </div>

          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>
              {isUploading ? "Ingesting Document..." : "Drop your PDF document here"}
            </h3>
            <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>
              {isUploading
                ? uploadStatus
                : "Supports digital text-based PDFs up to 10 MB. Page provenance is automatically preserved."}
            </p>
          </div>

          {!isUploading && (
            <button
              type="button"
              className="btn btn-secondary"
              style={{ marginTop: "8px", pointerEvents: "none" }}
            >
              <FileText size={16} />
              Browse PDF File
            </button>
          )}
        </div>
      </div>

      {/* Success Notification */}
      {uploadStatus && !isUploading && (
        <div
          style={{
            marginTop: "12px",
            padding: "12px 16px",
            backgroundColor: "var(--accent-emerald-bg)",
            border: "1px solid var(--accent-emerald)",
            borderRadius: "var(--radius-md)",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            color: "var(--accent-emerald)",
            fontSize: "0.875rem",
          }}
        >
          <CheckCircle2 size={18} />
          <span>{uploadStatus}</span>
        </div>
      )}

      {/* Error Notification */}
      {errorMessage && (
        <div
          style={{
            marginTop: "12px",
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
  );
}
