import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { api } from "../api";

export default function Chat({ messages, setMessages }) {
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  async function send(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;
    setError("");
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setSending(true);
    try {
      const res = await api.chat(text);
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="chat">
      <div className="chat-log">
        {messages.length === 0 && <p className="muted">No messages yet. Say hello, or analyze a repo from the sidebar.</p>}
        {messages.map((m, i) => (
          <div key={i} className={"bubble " + m.role}>
            {m.role === "assistant" ? <ReactMarkdown>{m.content}</ReactMarkdown> : m.content}
          </div>
        ))}
        {sending && <div className="bubble assistant muted">Thinking…</div>}
        <div ref={endRef} />
      </div>
      {error && <p className="error">{error}</p>}
      <form className="chat-input" onSubmit={send}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          maxLength={4000}
        />
        <button className="btn primary" disabled={sending || !input.trim()}>Send</button>
      </form>
    </div>
  );
}
