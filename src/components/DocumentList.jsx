export default function DocumentList({ documents, selectedDocId, onSelect }) {
  if (documents.length === 0) {
    return (
      <p className="doc-list__empty">
        No documents uploaded in this session yet. Upload a file above to begin analysis.
      </p>
    );
  }

  return (
    <ul className="doc-list">
      <li>
        <button
          type="button"
          className={`doc-item doc-item--all${selectedDocId === null ? " doc-item--active" : ""}`}
          onClick={() => onSelect(null)}
        >
          <span className="doc-item__name">All documents</span>
          <span className="doc-item__meta">{documents.length} file{documents.length > 1 ? "s" : ""}</span>
        </button>
      </li>
      {documents.map((doc) => {
        const failed = doc.status && doc.status !== "ok";
        return (
          <li key={doc.doc_id}>
            <button
              type="button"
              className={`doc-item${selectedDocId === doc.doc_id ? " doc-item--active" : ""}${
                failed ? " doc-item--failed" : ""
              }`}
              onClick={() => !failed && onSelect(doc.doc_id)}
              disabled={failed}
              title={failed ? doc.status : doc.filename}
            >
              <span className="doc-item__name">{doc.filename}</span>
              <span className="doc-item__meta">
                {failed ? (
                  <span className="status-badge status-badge--error">Failed</span>
                ) : (
                  <span className="status-badge status-badge--ok">
                    {doc.page_count} page{doc.page_count === 1 ? "" : "s"}
                  </span>
                )}
              </span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
