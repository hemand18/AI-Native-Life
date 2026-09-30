import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

export default function Notes() {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setNotes(await api.notes());
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function add(e) {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    setError("");
    try {
      await api.addNote(title.trim(), content.trim());
      setTitle("");
      setContent("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(id) {
    try {
      await api.deleteNote(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h2>Your Notes</h2>
      <form className="card stack" onSubmit={add}>
        <label>
          Title
          <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={255} />
        </label>
        <label>
          Content
          <textarea rows={4} value={content} onChange={(e) => setContent(e.target.value)} />
        </label>
        <button className="btn primary">Save Note</button>
      </form>
      {error && <p className="error">{error}</p>}
      {notes.length === 0 && <p className="muted">No notes yet. Add one above.</p>}
      {notes.map((n) => (
        <details key={n.id} className="card note">
          <summary>
            {n.title} <span className="muted small">— {n.timestamp.slice(0, 16).replace("T", " ")}</span>
          </summary>
          <p className="pre">{n.content}</p>
          <button className="btn danger" onClick={() => remove(n.id)}>Delete</button>
        </details>
      ))}
    </div>
  );
}
