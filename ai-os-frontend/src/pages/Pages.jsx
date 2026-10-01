import { useEffect } from "react";
import { Link } from "react-router-dom";

function useTitle(t) {
  useEffect(() => {
    document.title = t ? `${t} | AI-Native Life` : "AI-Native Life";
  }, [t]);
}

const REPO = "https://github.com/hemand18/AI-Native-Life";

export function Home() {
  useTitle("");
  return (
    <>
      <section className="hero">
        <h1>Your AI workspace for projects, goals and notes</h1>
        <p className="lead">Chat with an assistant that remembers you, plan your goals, and get an honest review of any public GitHub repo before it goes on your resume.</p>
        <div className="row hero-cta">
          <Link to="/app" className="btn primary big">Open the app</Link>
          <Link to="/features" className="btn big">See what it does</Link>
        </div>
      </section>
      <section className="steps">
        <div><h3>Paste a repo</h3><p className="muted">Enter a GitHub owner and repo name in the sidebar.</p></div>
        <div><h3>Get an honest review</h3><p className="muted">A score, what is strong, what is missing, and what to do next, based on the real README and files.</p></div>
        <div><h3>Keep what matters</h3><p className="muted">Save notes, set goals, and turn a goal into a 4-week plan.</p></div>
      </section>
    </>
  );
}

export function Features() {
  useTitle("Features");
  const items = [
    ["Chat with memory", "Your conversation is saved to your account, so it is there when you come back on any device."],
    ["Repo analysis", "Pulls the repo's real metadata, README and files, then scores resume-readiness and lists concrete fixes. A second pass checks the answer for invented claims."],
    ["Resume bullets", "Drafts 3-4 bullets written only from what the repo actually shows, with no made-up numbers."],
    ["Goals and plans", "Add a goal and turn it into a 4-week plan that is saved to your notes."],
    ["Notes and preferences", "Store notes and set preferences such as tone or focus. They are used in every analysis."],
    ["Automatic memory", "After an analysis, the assistant can save one note or goal on its own when something stands out."],
  ];
  return (
    <>
      <h1>Features</h1>
      <div className="feature-grid">
        {items.map(([t, d]) => (
          <div key={t} className="card"><h3>{t}</h3><p className="muted">{d}</p></div>
        ))}
      </div>
    </>
  );
}

export function About() {
  useTitle("About");
  return (
    <div className="prose">
      <h1>About</h1>
      <p>AI-Native Life started as a question: what would an AI system look like if it could actually help run your digital work, instead of only answering one-off questions?</p>
      <p>It was built as a final-year BCA project, one layer at a time: an LLM connection, persistent memory, document retrieval, a tool that reads GitHub, an agent that reasons over the results, and an evaluation step that checks the agent's own output. Every part was built from scratch to understand how it works.</p>
      <p>The code is open. You can read it, run it yourself, or open an issue on <a href={REPO} target="_blank" rel="noreferrer">GitHub</a>.</p>
    </div>
  );
}

export function Contact() {
  useTitle("Contact");
  return (
    <div className="prose">
      <h1>Contact</h1>
      <p>The best way to reach the project is through GitHub.</p>
      <ul>
        <li><a href={`${REPO}/issues`} target="_blank" rel="noreferrer">Report a bug or suggest an idea</a></li>
        <li><a href={REPO} target="_blank" rel="noreferrer">Browse the source code</a></li>
        <li><a href="https://github.com/hemand18" target="_blank" rel="noreferrer">Author's GitHub profile</a></li>
      </ul>
    </div>
  );
}

export function Privacy() {
  useTitle("Privacy");
  return (
    <div className="prose">
      <h1>Privacy</h1>
      <p className="muted">A plain-language summary for a student project. It is not legal advice.</p>
      <h3>What is stored</h3>
      <p>Your username, a hashed version of your password (the password itself is never stored), and what you create in the app: chat messages, notes, goals and preferences. Each account only sees its own data.</p>
      <h3>Who else sees it</h3>
      <p>Your chat messages and repo details are sent to Groq, the AI provider, to produce replies. Repo data is fetched from GitHub's public API. The site loads fonts from Google Fonts.</p>
      <h3>Your choices</h3>
      <p>Please do not put passwords, private keys or other sensitive information into chats or notes. To have your account data removed, open an issue on <a href={`${REPO}/issues`} target="_blank" rel="noreferrer">GitHub</a>.</p>
    </div>
  );
}

export function Terms() {
  useTitle("Terms");
  return (
    <div className="prose">
      <h1>Terms</h1>
      <p className="muted">A plain-language summary for a student project. It is not legal advice.</p>
      <p>This app is provided as is, without any guarantee that it will be available, accurate or free of errors. AI replies can be wrong, so check anything important before relying on it.</p>
      <p>Each account has a daily limit on AI requests. Do not use the app to harm others, to break the law, or to try to get around the limits. Accounts that abuse the service may be removed.</p>
      <p>The source code is released under the MIT license.</p>
    </div>
  );
}

export function NotFound() {
  useTitle("Page not found");
  return (
    <div className="prose">
      <h1>Page not found</h1>
      <p>That address does not exist. Try the <Link to="/">home page</Link> or <Link to="/app">open the app</Link>.</p>
    </div>
  );
}
