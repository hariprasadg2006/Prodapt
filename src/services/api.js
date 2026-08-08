// Thin wrapper around the AI Research Assistant backend described in
// the integration guide. Every function throws a plain Error with a
// human-readable message on failure, so callers can catch once and
// show err.message directly in the UI.

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function parseErrorOrThrow(res, fallback) {
  let detail = fallback;
  try {
    const body = await res.json();
    if (body?.detail) detail = body.detail;
  } catch {
    // response wasn't JSON — fall back to the generic message
  }
  throw new Error(detail);
}

/** Verify the backend is up before showing the workspace. */
export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Backend is not available");
  return res.json(); // { status: "ok" }
}

/**
 * Upload documents (PDF, DOCX, TXT).
 * @param {File[]} files
 * @returns {Promise<{session_id: string, documents: Array}>}
 */
export async function uploadDocuments(files) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) await parseErrorOrThrow(res, "Upload failed");
  return res.json();
}

/**
 * Get a summary for one document, or all documents when docId is omitted.
 * @param {string} sessionId
 * @param {string|null} docId
 */
export async function getSummary(sessionId, docId = null) {
  const body = { session_id: sessionId };
  if (docId) body.doc_id = docId;

  const res = await fetch(`${API_BASE}/summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) await parseErrorOrThrow(res, "Summary failed");
  return res.json();
}

/**
 * Extract key insights for one document, or all documents when docId is omitted.
 * @param {string} sessionId
 * @param {string|null} docId
 */
export async function getInsights(sessionId, docId = null) {
  const body = { session_id: sessionId };
  if (docId) body.doc_id = docId;

  const res = await fetch(`${API_BASE}/insights`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) await parseErrorOrThrow(res, "Insights extraction failed");
  return res.json();
}

/**
 * Ask a question over the uploaded documents (RAG chat).
 * @param {string} sessionId
 * @param {string} question
 * @param {Array<{question: string, answer: string}>} chatHistory
 */
export async function askQuestion(sessionId, question, chatHistory = []) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      question,
      chat_history: chatHistory,
    }),
  });

  if (!res.ok) await parseErrorOrThrow(res, "Chat failed");
  return res.json();
}

/** Rehydrate a session (e.g. after a page refresh) by id. */
export async function getSessionInfo(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}`);
  if (!res.ok) await parseErrorOrThrow(res, "Session not found");
  return res.json();
}
