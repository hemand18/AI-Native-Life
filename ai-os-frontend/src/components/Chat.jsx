import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { api } from "../api";

const STARTERS = [
  "What can you help me with?",
  "Explain retrieval-augmented generation simply",
  "Give me tips for a strong GitHub README",
];

function Copy({ text }) {
  const [done, setDone] = useState(false);
  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setDone(true);
      setTimeout(() => setDone(false), 1500);
    } catch {}
  }
  return (
    <button className="copy" onClick={copy} aria-label="Copy reply">
      {done ? "Copied" : "Copy"}
    </button>
  );
}

export default function Chat({ messages, setMessages }) {
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: sending ? "auto" : "smooth" });
  }, [messages, sending]);

  async function send(raw) {
    const text = (raw ?? input).trim();
    if (!text || sending) return;
    setError("");
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }, { role: "assistant", content: "" }]);
    setSending(true);
    try {
      await api.chatStream(text, (chunk) =>
        setMessages((m) => {
          const copy = [...m];
          const last = copy[copy.length - 1];
          copy[copy.length - 1] = { ...last, content: last.content + chunk };
          return copy;
        })
      );
    } catch (err) {
      setError(err.message);
      // drop the empty placeholder if nothing was received
      setMessages((m) => {
        const last = m[m.length - 1];
        return last && last.role === "assistant" && last.content === "" ? m.slice(0, -1) : m;
      });
    } finally {
      setSending(false);
    }
  }

  function onKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="chat">
      <div className="chat-log">
        {messages.length === 0 && (
          <div className="empty">
            <h2>What are we working on?</h2>
            <p className="muted">Ask a question, or analyze a repo from the sidebar.</p>
            <div className="chips">
              {STARTERS.map((s) => (
                <button key={s} className="chip" onClick={() => send(s)}>{s}</button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={"bubble " + m.role}>
            {m.role === "user" ? (
              m.content
            ) : !m.content && sending ? (
              <span className="dots" aria-label="Thinking"><i /><i /><i /></span>
            ) : (
              <>
                <ReactMarkdown>{m.content}</ReactMarkdown>
                {m.content && !(sending && i === messages.length - 1) && <Copy text={m.content} />}
              </>
            )}
          </div>
        ))}
        <div ref={endRef} />
      </div>
      {error && <p className="error">{error}</p>}
      <div className="chat-input">
        <textarea
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKey}
          placeholder="Ask something… (Enter to send, Shift+Enter for a new line)"
          maxLength={4000}
        />
        <button className="btn primary" disabled={sending || !input.trim()} onClick={() => send()}>Send</button>
      </div>
    </div>
  );
}
