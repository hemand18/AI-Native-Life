
import { useEffect, useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import Logo from "./Logo.jsx";

const LINKS = [
  { to: "/", label: "Home", end: true },
  { to: "/features", label: "Features" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
];

function readTheme() {
  try {
    return localStorage.getItem("ai_os_theme") === "dark" ? "dark" : "light";
  } catch {
    return "light";
  }
}

function Navbar() {
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState(readTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;

    try {
      localStorage.setItem("ai_os_theme", theme);
    } catch {
      // Theme remains usable during the current session.
    }
  }, [theme]);

  function toggleTheme() {
    setTheme((current) => (current === "dark" ? "light" : "dark"));
  }

  return (
    <header className="site-nav">
      <Link
        to="/"
        aria-label="AI-Native Life home"
        onClick={() => setOpen(false)}
      >
        <Logo />
      </Link>

      <button
        className="icon-btn menu-btn"
        aria-label="Toggle menu"
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}
      >
        {open ? "✕" : "☰"}
      </button>

      <nav className={"nav-links" + (open ? " open" : "")}>
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            onClick={() => setOpen(false)}
            className={({ isActive }) =>
              "nav-link" + (isActive ? " active" : "")
            }
          >
            {link.label}
          </NavLink>
        ))}

        <button
          type="button"
          className="icon-btn theme-toggle"
          onClick={toggleTheme}
          aria-label={
            theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
          }
          title={theme === "dark" ? "Light mode" : "Dark mode"}
        >
          {theme === "dark" ? "☀️" : "🌙"}
        </button>

        <Link
          to="/app"
          className="btn primary"
          onClick={() => setOpen(false)}
        >
          Open app
        </Link>
      </nav>
    </header>
  );
}

function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-grid">
        <div>
          <Logo />
          <p className="muted small">
            An AI workspace with memory, goals and repo analysis. A student
            project, built in the open.
          </p>
        </div>

        <div>
          <h4>Product</h4>
          <Link to="/features">Features</Link>
          <Link to="/app">Open app</Link>
        </div>

        <div>
          <h4>About</h4>
          <Link to="/about">About</Link>
          <Link to="/contact">Contact</Link>
          <a
            href="https://github.com/hemand18/AI-Native-Life"
            target="_blank"
            rel="noreferrer"
          >
            GitHub
          </a>
        </div>

        <div>
          <h4>Legal</h4>
          <Link to="/privacy">Privacy</Link>
          <Link to="/terms">Terms</Link>
        </div>
      </div>

      <p className="muted small copyright">
        © {new Date().getFullYear()} AI-Native Life
      </p>
    </footer>
  );
}

export default function PublicLayout() {
  return (
    <div className="site">
      <Navbar />
      <main className="page">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
