
import { useState } from "react";
import { api } from "../api";
import Logo from "./Logo.jsx";

export default function Login({
  onLogin,
  theme = "light",
  onToggleTheme = () => {},
}) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");

    if (username.trim().length < 3 || password.length < 8) {
      setError("Username needs 3+ characters and password 8+.");
      return;
    }

    setBusy(true);

    try {
      if (mode === "signup") {
        await api.signup(username.trim(), password);
      }

      const result = await api.login(username.trim(), password);
      onLogin(result.token, result.username);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-wrap">
      <button
        type="button"
        className="icon-btn login-theme-toggle"
        aria-label={
          theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
        }
        title={theme === "dark" ? "Light mode" : "Dark mode"}
        onClick={onToggleTheme}
      >
        {theme === "dark" ? "☀️" : "🌙"}
      </button>

      <form className="card login" onSubmit={submit}>
        <Logo size={44} />

        <p className="muted">
          Your AI workspace for projects, goals and notes.
        </p>

        <div className="tabs">
          <button
            type="button"
            className={"tab" + (mode === "login" ? " active" : "")}
            onClick={() => {
              setMode("login");
              setError("");
            }}
          >
            Log in
          </button>

          <button
            type="button"
            className={"tab" + (mode === "signup" ? " active" : "")}
            onClick={() => {
              setMode("signup");
              setError("");
            }}
          >
            Sign up
          </button>
        </div>

        <label>
          Username
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            minLength={3}
            maxLength={50}
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete={
              mode === "signup" ? "new-password" : "current-password"
            }
            minLength={8}
            maxLength={72}
            required
          />
        </label>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <button className="btn primary" disabled={busy} type="submit">
          {busy
            ? "Please wait… the server may be waking up"
            : mode === "signup"
              ? "Create account"
              : "Log in"}
        </button>
      </form>
    </div>
  );
}
