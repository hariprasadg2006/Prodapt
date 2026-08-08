// Sample data used only in Demo Mode, when there's no backend to talk to
// yet. Nothing here is fetched from a server — it's just enough canned
// content so the UI (tabs, panels, chat) can be clicked through and
// demoed. Swap these out once the real API is connected.

export const DEMO_SESSION_ID = "demo-session";

export const DEMO_DOCUMENTS = [
  { doc_id: "demo-1", filename: "Q2_Market_Research.pdf", page_count: 14, status: "ok" },
  { doc_id: "demo-2", filename: "Competitor_Analysis.docx", page_count: 8, status: "ok" },
  { doc_id: "demo-3", filename: "User_Interview_Notes.txt", page_count: 3, status: "ok" },
];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function mockSummary(docId = null) {
  await delay(700);
  const docs = docId ? DEMO_DOCUMENTS.filter((d) => d.doc_id === docId) : DEMO_DOCUMENTS;
  return {
    cross_document_summary: docId
      ? null
      : "Across the uploaded materials, demand for the product is strongest among mid-market buyers, competitors are converging on usage-based pricing, and interviewed users consistently ask for faster onboarding and clearer reporting.",
    summaries: docs.map((d) => ({
      doc_id: d.doc_id,
      filename: d.filename,
      summary:
        "This is placeholder summary text standing in for the real 150–250 word summary your friend's backend will generate for " +
        d.filename +
        ". Once the /summary endpoint is connected, this panel will show the model's actual output here.",
    })),
  };
}

export async function mockInsights(docId = null) {
  await delay(700);
  const docs = docId ? DEMO_DOCUMENTS.filter((d) => d.doc_id === docId) : DEMO_DOCUMENTS;
  return {
    documents: docs.map((d) => ({
      doc_id: d.doc_id,
      filename: d.filename,
      insights: [
        { text: "Sample key insight one extracted from " + d.filename + ".", page: 2 },
        { text: "Sample key insight two, for demoing the layout.", page: 5 },
        { text: "Sample key insight three with a page reference.", page: null },
      ],
    })),
  };
}

export async function mockChat(question) {
  await delay(900);
  return {
    answer:
      'This is a placeholder answer to "' +
      question +
      '". Once the backend /chat endpoint is connected, real answers grounded in your uploaded documents will appear here, along with source citations.',
    sources: [
      { filename: DEMO_DOCUMENTS[0].filename, page: 4 },
      { filename: DEMO_DOCUMENTS[1].filename, page: 1 },
    ],
  };
}
