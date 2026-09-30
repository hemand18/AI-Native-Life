import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

export default function Preferences() {
  const [prefs, setPrefs] = useState([]);
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setPrefs(await api.preferences());
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function save(e) {
    e.preventDefault();
    if (!key.trim() || !value.trim()) return;
    setError("");
    try {
      await api.savePreference(key.trim(), value.trim());
      setKey("");
      setValue("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(k) {
    try {
      await api.deletePreference(k);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h2>Preferences</h2>
      <p className="muted">These get included whenever the system responds or analyzes something.</p>
      <form className="card stack" onSubmit={save}>
        <label>
          Setting name (e.g. "tone", "focus_area")
          <input value={key} onChange={(e) => setKey(e.target.value)} maxLength={100} />
        </label>
        <label>
          Value (e.g. "concise and direct", "backend projects")
          <input value={value} onChange={(e) => setValue(e.target.value)} maxLength={1000} />
        </label>
        <button className="btn primary">Save Preference</button>
      </form>
      {error && <p className="error">{error}</p>}
      {prefs.length === 0 && <p className="muted">No preferences set yet.</p>}
      {prefs.map((p) => (
        <div key={p.key} className="card row">
          <span>
            <strong>{p.key}</strong>: {p.value}
          </span>
          <button className="btn danger" onClick={() => remove(p.key)}>Delete</button>
        </div>
      ))}
    </div>
  );
}
