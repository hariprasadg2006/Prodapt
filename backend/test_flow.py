"""
End-to-end test script for the AI Research Assistant backend.

Usage:
    1. Start the server: uvicorn main:app --reload
    2. Run this script: python test_flow.py

This is NOT a pytest test — it's a runnable script that exercises every endpoint
and prints responses for manual verification.
"""

import httpx
import sys
import tempfile
import os

BASE_URL = "http://127.0.0.1:8000"


def main():
    client = httpx.Client(base_url=BASE_URL, timeout=120.0)

    # ── 0. Health check ─────────────────────────────────────────────────
    print("=" * 60)
    print("Step 0: Health check")
    print("=" * 60)
    resp = client.get("/health")
    print(f"  Status: {resp.status_code}")
    print(f"  Body:   {resp.json()}")
    assert resp.status_code == 200, "Health check failed!"
    print()

    # ── 1. Upload a sample TXT file ─────────────────────────────────────
    print("=" * 60)
    print("Step 1: Upload a sample TXT document")
    print("=" * 60)

    sample_text = """
    Artificial Intelligence and Machine Learning: A Research Overview

    Page 1: Introduction
    Artificial intelligence (AI) is a branch of computer science focused on building
    machines capable of performing tasks that typically require human intelligence.
    Machine learning (ML) is a subset of AI that enables systems to learn and improve
    from experience without being explicitly programmed.

    Page 2: Key Concepts
    Supervised learning uses labeled training data to learn a mapping from inputs to
    outputs. Unsupervised learning finds hidden patterns in data without labeled
    responses. Reinforcement learning trains agents to make decisions by rewarding
    desired behaviors.

    Page 3: Applications
    AI is transforming healthcare through medical image analysis and drug discovery.
    In finance, ML models detect fraud and predict market trends. Natural language
    processing powers chatbots, translation, and text summarization.

    Page 4: Challenges
    Key challenges include data privacy, algorithmic bias, model interpretability,
    and the environmental cost of training large models. Ethical AI frameworks are
    being developed to address these concerns.

    Page 5: Future Directions
    Emerging trends include multimodal AI, federated learning for privacy-preserving
    ML, and the development of artificial general intelligence (AGI). Responsible AI
    governance will be critical as these technologies mature.
    """

    # Write to a temp file
    tmp_path = os.path.join(tempfile.gettempdir(), "sample_research.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(sample_text)

    with open(tmp_path, "rb") as f:
        resp = client.post("/upload", files=[("files", ("sample_research.txt", f, "text/plain"))])

    print(f"  Status: {resp.status_code}")
    upload_data = resp.json()
    print(f"  Session ID: {upload_data['session_id']}")
    for doc in upload_data["documents"]:
        print(f"  Doc: {doc['filename']} | pages: {doc['page_count']} | status: {doc['status']}")
    assert resp.status_code == 200, "Upload failed!"

    session_id = upload_data["session_id"]
    doc_id = upload_data["documents"][0]["doc_id"]
    print()

    # ── 2. Session info ─────────────────────────────────────────────────
    print("=" * 60)
    print("Step 2: Get session info")
    print("=" * 60)
    resp = client.get(f"/session/{session_id}")
    print(f"  Status: {resp.status_code}")
    print(f"  Body:   {resp.json()}")
    print()

    # ── 3. Summary ──────────────────────────────────────────────────────
    print("=" * 60)
    print("Step 3: Get document summary")
    print("=" * 60)
    resp = client.post("/summary", json={"session_id": session_id, "doc_id": doc_id})
    print(f"  Status: {resp.status_code}")
    summary_data = resp.json()
    for s in summary_data.get("summaries", []):
        print(f"  [{s['filename']}] Summary:")
        print(f"    {s['summary'][:300]}...")
    print()

    # ── 4. Insights ─────────────────────────────────────────────────────
    print("=" * 60)
    print("Step 4: Extract key insights")
    print("=" * 60)
    resp = client.post("/insights", json={"session_id": session_id, "doc_id": doc_id})
    print(f"  Status: {resp.status_code}")
    insights_data = resp.json()
    for doc_insights in insights_data.get("documents", []):
        print(f"  Insights for doc {doc_insights['doc_id'][:8]}...:")
        for ins in doc_insights["insights"]:
            page_str = f" (page {ins['page']})" if ins.get("page") else ""
            print(f"    • {ins['text']}{page_str}")
    print()

    # ── 5. Chat ─────────────────────────────────────────────────────────
    print("=" * 60)
    print("Step 5: Ask a question (RAG chat)")
    print("=" * 60)
    question = "What are the main challenges of AI mentioned in the document?"
    resp = client.post("/chat", json={"session_id": session_id, "question": question})
    print(f"  Status: {resp.status_code}")
    chat_data = resp.json()
    print(f"  Question: {question}")
    print(f"  Answer:   {chat_data['answer'][:500]}")
    print(f"  Sources:")
    for src in chat_data.get("sources", []):
        page_str = f"page {src['page']}" if src.get("page") else "unknown page"
        print(f"    - {src['filename']}, {page_str}: {src['snippet'][:100]}...")
    print()

    # ── 6. Follow-up question with history ──────────────────────────────
    print("=" * 60)
    print("Step 6: Follow-up question with chat history")
    print("=" * 60)
    followup = "What solutions are being proposed for these challenges?"
    resp = client.post("/chat", json={
        "session_id": session_id,
        "question": followup,
        "chat_history": [{"question": question, "answer": chat_data["answer"]}],
    })
    print(f"  Status: {resp.status_code}")
    followup_data = resp.json()
    print(f"  Question: {followup}")
    print(f"  Answer:   {followup_data['answer'][:500]}")
    print()

    print("=" * 60)
    print("✅ All steps completed successfully!")
    print("=" * 60)

    # Cleanup
    os.remove(tmp_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
