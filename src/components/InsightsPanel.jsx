import { useState } from "react";
import { getInsights } from "../services/api.js";
import { mockInsights } from "../services/mockData.js";

export default function InsightsPanel({ sessionId, docId, demoMode }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [documents, setDocuments] = useState(null);

  async function handleExtract() {
    setLoading(true);
    setError("");
    try {
      const data = demoMode ? await mockInsights(docId) : await getInsights(sessionId, docId);
      setDocuments(data.documents);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      <div className="panel__actions">
        <button type="button" className="btn-primary btn-primary--inline" onClick={handleExtract} disabled={loading}>
          {loading ? "Extracting…" : documents ? "Re-extract insights" : "Extract insights"}
        </button>
        <p className="panel__hint">
          {docId ? "Pulls insights from the selected document." : "Pulls insights from every document."}
          {demoMode && " (Demo Mode — showing sample output)"}
        </p>
      </div>

      {loading && (
        <div className="skeleton-block" aria-hidden="true">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="skeleton-line" style={{ width: `${88 - i * 8}%` }} />
          ))}
        </div>
      )}

      {error && (
        <p className="panel__error" role="alert">
          {error}
        </p>
      )}

      {!loading && documents && (
        <div className="insights-list">
          {documents.map((doc) => (
            <div className="insights-doc" key={doc.doc_id}>
              <h4 className="insights-doc__title">{doc.filename}</h4>
              <ul className="insights-doc__items">
                {doc.insights.map((insight, i) => (
                  <li key={i} className="insight-item">
                    <span className="insight-item__text">{insight.text}</span>
                    {insight.page != null && (
                      <span className="insight-item__page">p. {insight.page}</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      {!loading && !documents && !error && (
        <p className="panel__empty">Extract insights to see key takeaways with page references.</p>
      )}
    </div>
  );
}
