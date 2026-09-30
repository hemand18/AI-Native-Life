import { useEffect, useState } from "react";
import { api, auth, setUnauthorizedHandler } from "./api";
import Login from "./components/Login.jsx";
import Sidebar from "./components/Sidebar.jsx";
import Chat from "./components/Chat.jsx";
import Notes from "./components/Notes.jsx";
import Preferences from "./components/Preferences.jsx";
import Goals from "./components/Goals.jsx";

const TABS = [
  { id: "chat", label: "💬 Chat" },
  { id: "notes", label: "📝 Notes" },
  { id: "prefs", label: "⚙️ Preferences" },
  { id: "goals", label: "🎯 Goals" },
];

export default function App() {
  const [user, setUser] = useState(auth.token ? auth.username : null);
  const [tab, setTab] = useState("chat");
  const [messages, setMessages] = useState([]);

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
    setMessages((m) => [
      ...m,
      { role: "user", content: userText },
      { role: "assistant", content: reply },
    ]);
    setTab("chat");
  }

  if (!user) return <Login onLogin={handleLogin} />;

  return (
    <div className="layout">
      <Sidebar username={user} onLogout={logout} onResult={addExchange} />
      <main className="main">
        <h1 className="title">My AI OS</h1>
        <nav className="tabs">
          {TABS.map((t) => (
            <button
              key={t.id}
              className={"tab" + (tab === t.id ? " active" : "")}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </nav>
        <section className="panel">
          {tab === "chat" && <Chat messages={messages} setMessages={setMessages} />}
          {tab === "notes" && <Notes />}
          {tab === "prefs" && <Preferences />}
          {tab === "goals" && <Goals />}
        </section>
      </main>
    </div>
  );
}
