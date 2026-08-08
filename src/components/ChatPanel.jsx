import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../services/api.js";
import { mockChat } from "../services/mockData.js";

export default function ChatPanel({ sessionId, demoMode }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const threadRef = useRef(null);

  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setError("");
    setLoading(true);

    try {
      const chatHistory = messages.map((m) => ({ question: m.question, answer: m.answer }));
      const data = demoMode ? await mockChat(question) : await askQuestion(sessionId, question, chatHistory);
      setMessages((prev) => [...prev, { question, answer: data.answer, sources: data.sources }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-panel">
      {demoMode && (
        <p className="panel__hint panel__hint--chat">Demo Mode — answers are sample text, not real RAG output.</p>
      )}
      <div className="chat-thread" ref={threadRef}>
        {messages.length === 0 && !loading && (
          <p className="panel__empty">Ask a question about your uploaded documents.</p>
        )}

        {messages.map((m, i) => (
          <div className="chat-exchange" key={i}>
            <div className="chat-message chat-message--user">{m.question}</div>
            <div className="chat-message chat-message--ai">
              <p>{m.answer}</p>
              {m.sources?.length > 0 && (
                <div className="chat-sources">
                  {m.sources.map((s, j) => (
                    <span className="source-chip" key={j}>
                      📄 {s.filename}
                      {s.page != null ? `, p. ${s.page}` : ""}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-exchange">
            <div className="chat-message chat-message--ai chat-message--pending">Thinking…</div>
          </div>
        )}
      </div>

      {error && (
        <p className="panel__error" role="alert">
          {error}
        </p>
      )}

      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about your documents…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn-primary btn-primary--inline" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
