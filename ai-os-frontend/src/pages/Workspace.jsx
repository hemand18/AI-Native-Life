
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, auth, setUnauthorizedHandler } from "../api";
import Logo from "../components/Logo.jsx";
import Login from "../components/Login.jsx";
import Sidebar from "../components/Sidebar.jsx";
import Chat from "../components/Chat.jsx";
import Notes from "../components/Notes.jsx";
import Preferences from "../components/Preferences.jsx";
import Goals from "../components/Goals.jsx";

const TABS = [
  { id: "chat", label: "💬 Chat" },
  { id: "notes", label: "📝 Notes" },
  { id: "prefs", label: "⚙️ Preferences" },
  { id: "goals", label: "🎯 Goals" },
];

function getSavedTheme() {
  try {
    return localStorage.getItem("ai_os_theme") === "dark" ? "dark" : "light";
  } catch {
    return "light";
  }
}

export default function Workspace() {
  const [user, setUser] = useState(auth.token ? auth.username : null);
  const [tab, setTab] = useState("chat");
  const [messages, setMessages] = useState([]);
  const [collapsed, setCollapsed] = useState(false);
  const [theme, setTheme] = useState(getSavedTheme);

  useEffect(() => {
    document.title = "Workspace | AI-Native Life";
    document.documentElement.dataset.theme = theme;

    try {
      localStorage.setItem("ai_os_theme", theme);
    } catch {
      // The theme still works for the current session if storage is unavailable.
    }
  }, [theme]);

  function toggleTheme() {
    setTheme((current) => (current === "dark" ? "light" : "dark"));
  }

  function logout() {
    auth.clear();
    setUser(null);
    setMessages([]);
    setTab("chat");
  }

  useEffect(() => {
    setUnauthorizedHandler(logout);
    return () => setUnauthorizedHandler(null);
  }, []);

  useEffect(() => {
    if (!user) return;
    api.messages().then(setMessages).catch(() => {});
  }, [user]);

  function handleLogin(token, username) {
    auth.save(token, username);
    setUser(username);
  }

  function addExchange(userText, reply) {
    setMessages((current) => [
      ...current,
      { role: "user", content: userText },
      { role: "assistant", content: reply },
    ]);
    setTab("chat");
  }

  if (!user) {
    return (
      <Login
        onLogin={handleLogin}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
    );
  }

  return (
    <div className={"layout" + (collapsed ? " collapsed" : "")}>
      <header className="topbar">
        <button
          className="icon-btn"
          aria-label="Toggle sidebar"
          aria-expanded={!collapsed}
          onClick={() => setCollapsed((current) => !current)}
        >
          ☰
        </button>

        <Link to="/" aria-label="Back to the home page">
          <Logo />
        </Link>

        <span className="grow" />

        <button
          className="icon-btn"
          aria-label={
            theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
          }
          title={theme === "dark" ? "Light mode" : "Dark mode"}
          onClick={toggleTheme}
        >
          {theme === "dark" ? "☀️" : "🌙"}
        </button>
      </header>

      <div className="body">
        <Sidebar
          username={user}
          onLogout={logout}
          onResult={addExchange}
        />

        <main className="main">
          <nav className="tabs" role="tablist" aria-label="Workspace sections">
            {TABS.map((item) => (
              <button
                key={item.id}
                role="tab"
                aria-selected={tab === item.id}
                className={"tab" + (tab === item.id ? " active" : "")}
                onClick={() => setTab(item.id)}
              >
                {item.label}
              </button>
            ))}
          </nav>

          <section className="panel" key={tab}>
            {tab === "chat" && (
              <Chat messages={messages} setMessages={setMessages} />
            )}
            {tab === "notes" && <Notes />}
            {tab === "prefs" && <Preferences />}
            {tab === "goals" && <Goals />}
          </section>
        </main>
      </div>
    </div>
  );
}
