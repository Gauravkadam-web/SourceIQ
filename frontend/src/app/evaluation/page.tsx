"use client";

import React from "react";
import EvaluationDashboard from "../../components/EvaluationDashboard";

export default function EvaluationPage() {
  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "28px" }}>
      <EvaluationDashboard />
    </div>
  );
}
