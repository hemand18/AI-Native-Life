import { useState } from "react";
import { api } from "../api";

export default function Sidebar({ username, onLogout, onResult }) {
  const [owner, setOwner] = useState("");
  const [repo, setRepo] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  async function run(kind) {
    if (!owner.trim() || !repo.trim()) {
      setError("Enter both an owner and a repo name.");
      return;
    }
    setError("");
    setBusy(kind);
    try {
      if (kind === "analyze") {
        const res = await api.analyze(owner.trim(), repo.trim());
        onResult(`Analyze ${owner.trim()}/${repo.trim()}`, res.reply);
      } else {
        const res = await api.bullets(owner.trim(), repo.trim());
        onResult(`Draft resume bullets for ${owner.trim()}/${repo.trim()}`, res.reply);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy("");
    }
  }

  return (
    <aside className="sidebar">
      <p className="muted small">Logged in as {username}</p>
      <button className="btn" onClick={onLogout}>Log out</button>
      <hr />
      <h3>Analyze a GitHub repo</h3>
      <label>
        Owner (username)
        <input value={owner} onChange={(e) => setOwner(e.target.value)} />
      </label>
      <label>
        Repo name
        <input value={repo} onChange={(e) => setRepo(e.target.value)} />
      </label>
      <button className="btn primary" disabled={!!busy} onClick={() => run("analyze")}>
        {busy === "analyze" ? "Analyzing…" : "Analyze"}
      </button>
      <button className="btn" disabled={!!busy} onClick={() => run("bullets")}>
        {busy === "bullets" ? "Drafting…" : "Draft Resume Bullets"}
      </button>
      {error && <p className="error">{error}</p>}
    </aside>
  );
}
