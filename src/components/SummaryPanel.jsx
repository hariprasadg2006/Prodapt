import { useState } from "react";
import { getSummary } from "../services/api.js";
import { mockSummary } from "../services/mockData.js";

export default function SummaryPanel({ sessionId, docId, demoMode }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function handleGenerate() {
    setLoading(true);
    setError("");
    try {
      const data = demoMode ? await mockSummary(docId) : await getSummary(sessionId, docId);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      <div className="panel__actions">
        <button type="button" className="btn-primary btn-primary--inline" onClick={handleGenerate} disabled={loading}>
          {loading ? "Summarizing…" : result ? "Regenerate summary" : "Generate summary"}
        </button>
        <p className="panel__hint">
          {docId ? "Summarizes the selected document." : "Summarizes every document in this session."}
          {demoMode && " (Demo Mode — showing sample output)"}
        </p>
      </div>

      {loading && <SkeletonLines count={4} />}

      {error && (
        <p className="panel__error" role="alert">
          {error}
        </p>
      )}

      {!loading && result && (
        <div className="summary-list">
          {result.cross_document_summary && (
            <div className="summary-card summary-card--cross">
              <h4>Across all documents</h4>
              <p>{result.cross_document_summary}</p>
            </div>
          )}
          {result.summaries.map((s) => (
            <div className="summary-card" key={s.doc_id}>
              <h4>{s.filename}</h4>
              <p>{s.summary}</p>
            </div>
          ))}
        </div>
      )}

      {!loading && !result && !error && (
        <p className="panel__empty">Generate a summary to see it here.</p>
      )}
    </div>
  );
}

function SkeletonLines({ count }) {
  return (
    <div className="skeleton-block" aria-hidden="true">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-line" style={{ width: `${90 - i * 12}%` }} />
      ))}
    </div>
  );
}
