import { useState } from "react";
import { api } from "../api";
import Logo from "./Logo.jsx";

export default function Login({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (username.trim().length < 3 || password.length < 8) {
      setError("Username needs 3+ characters and password 8+.");
      return;
    }
    setBusy(true);
    try {
      if (mode === "signup") await api.signup(username.trim(), password);
      const res = await api.login(username.trim(), password);
      onLogin(res.token, res.username);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-wrap">
      <form className="card login" onSubmit={submit}>
        <Logo size={44} />
        <p className="muted">Your AI workspace for projects, goals and notes.</p>
        <div className="tabs">
          <button type="button" className={"tab" + (mode === "login" ? " active" : "")} onClick={() => setMode("login")}>Log in</button>
          <button type="button" className={"tab" + (mode === "signup" ? " active" : "")} onClick={() => setMode("signup")}>Sign up</button>
        </div>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete={mode === "signup" ? "new-password" : "current-password"} />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn primary" disabled={busy}>
          {busy ? "Please wait… the server may be waking up" : mode === "signup" ? "Create account" : "Log in"}
        </button>
      </form>
    </div>
  );
}
