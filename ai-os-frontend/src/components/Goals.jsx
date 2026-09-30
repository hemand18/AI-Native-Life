import { useCallback, useEffect, useState } from "react";
import { api } from "../api";

export default function Goals() {
  const [goals, setGoals] = useState([]);
  const [title, setTitle] = useState("");
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  const load = useCallback(async () => {
    try {
      setGoals(await api.goals());
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function add(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setError("");
    setInfo("");
    try {
      await api.addGoal(title.trim());
      setTitle("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function act(fn) {
    setError("");
    setInfo("");
    try {
      await fn();
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function plan(id) {
    setError("");
    setInfo("");
    setBusyId(id);
    try {
      await api.planGoal(id);
      setInfo("Plan saved to Notes.");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  const active = goals.filter((g) => g.status === "active");
  const done = goals.filter((g) => g.status === "done");

  return (
    <div>
      <h2>Goals</h2>
      <form className="card row" onSubmit={add}>
        <input
          className="grow"
          placeholder="New goal"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={500}
        />
        <button className="btn primary">Add Goal</button>
      </form>
      {error && <p className="error">{error}</p>}
      {info && <p className="ok">{info}</p>}

      <h3>Active ({active.length})</h3>
      {active.map((g) => (
        <div key={g.id} className="card row">
          <span className="grow">{g.title}</span>
          <button className="btn" disabled={busyId === g.id} onClick={() => plan(g.id)}>
            {busyId === g.id ? "Planning…" : "📅 Plan"}
          </button>
          <button className="btn" onClick={() => act(() => api.setGoalStatus(g.id, "done"))}>✅ Done</button>
          <button className="btn danger" onClick={() => act(() => api.deleteGoal(g.id))}>🗑️</button>
        </div>
      ))}

      {done.length > 0 && (
        <>
          <h3>Completed ({done.length})</h3>
          {done.map((g) => (
            <div key={g.id} className="card row">
              <span className="grow done">{g.title}</span>
              <button className="btn" onClick={() => act(() => api.setGoalStatus(g.id, "active"))}>Reopen</button>
              <button className="btn danger" onClick={() => act(() => api.deleteGoal(g.id))}>🗑️</button>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
