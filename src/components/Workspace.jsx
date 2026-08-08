import { useEffect, useState } from "react";
import Logo from "./Logo.jsx";
import FileUpload from "./FileUpload.jsx";
import DocumentList from "./DocumentList.jsx";
import SummaryPanel from "./SummaryPanel.jsx";
import InsightsPanel from "./InsightsPanel.jsx";
import ChatPanel from "./ChatPanel.jsx";
import { uploadDocuments, checkHealth, getSessionInfo } from "../services/api.js";
import { DEMO_SESSION_ID, DEMO_DOCUMENTS } from "../services/mockData.js";

const TABS = [
  {
    id: "chat",
    label: "Ask & Chat (RAG)",
    icon: (
      <path
        d="M4 5.5h16v10H8.5L5 19v-3.5H4v-10Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    ),
    emptyTitle: "Ask & Chat (RAG)",
    emptyBody:
      "Upload documents, then ask natural-language questions and get answers grounded in your files, complete with source citations.",
  },
  {
    id: "summary",
    label: "Document Summaries",
    icon: (
      <>
        <path
          d="M7 3.5h7l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1v-16a1 1 0 0 1 1-1Z"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        <path d="M14 3.5V8h4" stroke="currentColor" strokeWidth="1.5" />
      </>
    ),
    emptyTitle: "Document Summarizer",
    emptyBody:
      "Upload documents to automatically generate concise 150–250 word summaries and multi-document synthesis reports.",
  },
  {
    id: "insights",
    label: "Key Insights",
    icon: (
      <path
        d="M12 3.5a5.5 5.5 0 0 0-3 10.1c.6.4 1 1.1 1 1.9v.5h4v-.5c0-.8.4-1.5 1-1.9A5.5 5.5 0 0 0 12 3.5ZM10 18.5h4M10.5 20.5h3"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    ),
    emptyTitle: "Key Insights Extraction",
    emptyBody:
      "Upload documents to automatically pull out key takeaways and findings, each linked back to the page it came from.",
  },
];

// Emoji-free "book" glyph used for the big empty-state icon, matching
// whichever tab is active.
function TabIcon({ tab, size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      {tab.icon}
    </svg>
  );
}

export default function Workspace({ userName, onSignOut }) {
  // session_id lives only in memory — it's lost on refresh, and that's
  // fine for this demo. A real session survives via the backend's
  // /session/:id endpoint (see getSessionInfo in services/api.js).
  const [sessionId, setSessionId] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [activeTab, setActiveTab] = useState("chat");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  // Backend connectivity + demo mode. There's no backend wired up yet,
  // so this defaults to "disconnected" and flips to "connected" only if
  // a real /health endpoint answers. Demo Mode lets the whole UI be
  // clicked through with sample data in the meantime — once the
  // backend is live, Demo Mode can just be switched off.
  const [backendStatus, setBackendStatus] = useState("checking"); // checking | connected | disconnected
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    let cancelled = false;
    checkHealth()
      .then(() => {
        if (!cancelled) setBackendStatus("connected");
      })
      .catch(() => {
        if (!cancelled) {
          setBackendStatus("disconnected");
          setDemoMode(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleUpload(files) {
    if (demoMode) {
      // No backend to send files to — just reflect them in the file
      // list so the UI feels responsive while in Demo Mode.
      const fakeDocs = files.map((file, i) => ({
        doc_id: `local-${Date.now()}-${i}`,
        filename: file.name,
        page_count: Math.max(1, Math.round(file.size / 50000)) || 1,
        status: "ok",
      }));
      setSessionId((prev) => prev || DEMO_SESSION_ID);
      setDocuments((prev) => [...prev, ...fakeDocs]);
      return;
    }

    setUploading(true);
    setUploadError("");
    try {
      const result = await uploadDocuments(files);
      setSessionId(result.session_id);
      setDocuments((prev) => [...prev, ...result.documents]);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleLoadSession() {
    if (demoMode) {
      setSessionId(DEMO_SESSION_ID);
      setDocuments(DEMO_DOCUMENTS);
      setUploadError("");
      return;
    }

    const id = window.prompt("Enter a session ID to load:");
    if (!id) return;

    setUploadError("");
    try {
      const info = await getSessionInfo(id);
      setSessionId(id);
      setDocuments(info.documents || []);
    } catch (err) {
      setUploadError(err.message);
    }
  }

  const hasDocs = documents.length > 0;
  const usableDocs = documents.filter((d) => !d.status || d.status === "ok");
  const activeTabInfo = TABS.find((t) => t.id === activeTab);

  const statusLabel =
    backendStatus === "connected"
      ? "Backend Connected"
      : backendStatus === "checking"
      ? "Checking Backend…"
      : "Backend Disconnected";

  return (
    <div className="workspace">
      <header className="workspace__header">
        <div className="workspace__brand">
          <Logo />
          <span className="badge-product">PRODAPT RAG</span>
        </div>
        <div className="workspace__header-right">
          <span className={`status-pill status-pill--${backendStatus}`}>
            <span className="status-pill__dot" aria-hidden="true" />
            {statusLabel}
          </span>
          <button
            type="button"
            className={`demo-toggle${demoMode ? " demo-toggle--active" : ""}`}
            onClick={() => setDemoMode((v) => !v)}
            title="Toggle sample data on/off"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M13 2 3 14h6l-1 8 11-13h-7l1-7Z" />
            </svg>
            Demo Mode
          </button>
          {userName && <span className="workspace__user">Signed in as {userName}</span>}
          <button type="button" className="btn-secondary" onClick={onSignOut}>
            Sign out
          </button>
        </div>
      </header>

      <div className="workspace__body">
        <aside className="workspace__sidebar">
          <FileUpload onUpload={handleUpload} loading={uploading} />
          {uploadError && (
            <p className="panel__error" role="alert">
              {uploadError}
            </p>
          )}

          <div className="sidebar-section-header">
            <h2 className="workspace__sidebar-title">Session Files ({documents.length})</h2>
            <button type="button" className="btn-link-icon" onClick={handleLoadSession}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M4 12a8 8 0 1 1 2.4 5.7M4 12V6m0 6h6"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              Load Session
            </button>
          </div>

          <DocumentList
            documents={documents}
            selectedDocId={selectedDocId}
            onSelect={setSelectedDocId}
          />
        </aside>

        <main className="workspace__main">
          <nav className="tabs">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={`tab${activeTab === tab.id ? " tab--active" : ""}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <TabIcon tab={tab} size={16} />
                {tab.label}
              </button>
            ))}
          </nav>

          {!hasDocs ? (
            <div className="tab-empty">
              <span className="tab-empty__icon" aria-hidden="true">
                <TabIcon tab={activeTabInfo} size={30} />
              </span>
              <h2>{activeTabInfo.emptyTitle}</h2>
              <p>{activeTabInfo.emptyBody}</p>
            </div>
          ) : usableDocs.length === 0 ? (
            <p className="panel__error">
              None of the uploaded files could be processed. Try uploading a different file.
            </p>
          ) : (
            <>
              {activeTab === "summary" && (
                <SummaryPanel sessionId={sessionId} docId={selectedDocId} demoMode={demoMode} />
              )}
              {activeTab === "insights" && (
                <InsightsPanel sessionId={sessionId} docId={selectedDocId} demoMode={demoMode} />
              )}
              {activeTab === "chat" && <ChatPanel sessionId={sessionId} demoMode={demoMode} />}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
