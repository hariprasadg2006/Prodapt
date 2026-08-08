# ResearchAI — Frontend (auth + workspace)

A React + plain CSS frontend for "ResearchAI", themed in Prodapt's red and
white identity. It has two parts:

1. **Sign In / Sign Up** — frontend-only, no real auth (unchanged from the
   original demo — validates locally, never calls a backend).
2. **Workspace** — the real thing. After signing in/up, the user lands in a
   workspace that talks to the FastAPI backend described in your
   integration guide: upload documents, generate summaries, extract
   insights, and chat with citations.

## Where each file goes

```
researchai-auth/
├── index.html, package.json, vite.config.js, .env.example
└── src/
    ├── main.jsx, App.jsx, index.css
    ├── services/
    │   └── api.js                  ← fetch wrappers for every backend endpoint
    ├── utils/
    │   └── validation.js           ← sign in/up field validation
    └── components/
        ├── Logo.jsx, FormInput.jsx, PasswordInput.jsx
        ├── AuthLayout.jsx, AuthIllustration.jsx
        ├── SignIn.jsx, SignUp.jsx
        └── Workspace.jsx            ← post-login screen, composes:
            ├── FileUpload.jsx        (drag/drop, .pdf/.docx/.txt only)
            ├── DocumentList.jsx      (per-doc status, "All documents" mode)
            ├── SummaryPanel.jsx      (POST /summary)
            ├── InsightsPanel.jsx     (POST /insights, page refs)
            └── ChatPanel.jsx         (POST /chat, multi-turn + sources)
```

## Running it against your backend

```bash
cp .env.example .env       # defaults to http://localhost:8000
npm install
npm run dev
```

Start your FastAPI backend separately (`uvicorn main:app --reload`), then
sign in/up in the app — you'll land in the workspace, which calls the real
API from there on.

## Notes

- `session_id` is kept only in React state (`Workspace.jsx`), never in
  `localStorage`, per the guide — refreshing the page starts a new session.
- Every API call goes through `src/services/api.js`; errors surface as
  `err.message` directly in the relevant panel rather than crashing anything.
- Unsupported file types are filtered out client-side before upload; failed
  documents (e.g. encrypted PDFs) show a "Failed" badge and can't be
  selected for summary/insights/chat.
- Sign In / Sign Up remain frontend-only — no account is actually created,
  by design.

## Theme

Palette lives in `src/index.css` custom properties: `--accent` (#d1001f,
Prodapt red), `--accent-2` (#9c0016, deeper red for gradients),
`--accent-tint` (#ffe8ea, tint for highlights/badges), on a white
(`--bg`/`--surface`) background. The auth side-panel illustration includes a
triangular grid motif echoing Prodapt's mark.
