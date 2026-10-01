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

export default function Workspace() {
  const [user, setUser] = useState(auth.token ? auth.username : null);
  const [tab, setTab] = useState("chat");
  const [messages, setMessages] = useState([]);
  const [collapsed, setCollapsed] = useState(false);
  const [theme, setTheme] = useState(document.documentElement.dataset.theme || "light");

  useEffect(() => {
    document.title = "Workspace | AI-Native Life";
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("ai_os_theme", theme);
    } catch {}
  }, [theme]);

  function logout() {
    auth.clear();
    setUser(null);
    setMessages([]);
    setTab("chat");
  }

  useEffect(() => {
    setUnauthorizedHandler(logout);
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
    setMessages((m) => [...m, { role: "user", content: userText }, { role: "assistant", content: reply }]);
    setTab("chat");
  }

  if (!user) return <Login onLogin={handleLogin} />;

  return (
    <div className={"layout" + (collapsed ? " collapsed" : "")}>
      <header className="topbar">
        <button className="icon-btn" aria-label="Toggle sidebar" onClick={() => setCollapsed((c) => !c)}>☰</button>
        <Link to="/" aria-label="Back to the home page"><Logo /></Link>
        <span className="grow" />
        <button className="icon-btn" aria-label="Switch theme" onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}>
          {theme === "dark" ? "☀️" : "🌙"}
        </button>
      </header>
      <div className="body">
        <Sidebar username={user} onLogout={logout} onResult={addExchange} />
        <main className="main">
          <nav className="tabs" role="tablist">
            {TABS.map((t) => (
              <button key={t.id} role="tab" aria-selected={tab === t.id} className={"tab" + (tab === t.id ? " active" : "")} onClick={() => setTab(t.id)}>
                {t.label}
              </button>
            ))}
          </nav>
          <section className="panel" key={tab}>
            {tab === "chat" && <Chat messages={messages} setMessages={setMessages} />}
            {tab === "notes" && <Notes />}
            {tab === "prefs" && <Preferences />}
            {tab === "goals" && <Goals />}
          </section>
        </main>
      </div>
    </div>
  );
}
