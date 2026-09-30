const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const TOKEN_KEY = "ai_os_token";
const USER_KEY = "ai_os_user";

export const auth = {
  get token() {
    return localStorage.getItem(TOKEN_KEY);
  },
  get username() {
    return localStorage.getItem(USER_KEY);
  },
  save(token, username) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, username);
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

let onUnauthorized = () => {};
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

async function request(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth.token) headers.Authorization = `Bearer ${auth.token}`;

  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error("Can't reach the server. Is the backend running?");
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    // empty or non-JSON response
  }

  if (!res.ok) {
    if (res.status === 401 && !path.startsWith("/auth/")) onUnauthorized();
    const detail = data && data.detail;
    throw new Error(typeof detail === "string" ? detail : "Invalid input. Please check what you entered.");
  }
  return data;
}

export const api = {
  signup: (username, password) => request("/auth/signup", { method: "POST", body: { username, password } }),
  login: (username, password) => request("/auth/login", { method: "POST", body: { username, password } }),

  messages: () => request("/messages"),
  chat: (message) => request("/chat", { method: "POST", body: { message } }),
  analyze: (owner, repo) => request("/analyze", { method: "POST", body: { owner, repo } }),
  bullets: (owner, repo) => request("/bullets", { method: "POST", body: { owner, repo } }),

  notes: () => request("/notes"),
  addNote: (title, content) => request("/notes", { method: "POST", body: { title, content } }),
  deleteNote: (id) => request(`/notes/${id}`, { method: "DELETE" }),

  preferences: () => request("/preferences"),
  savePreference: (key, value) => request("/preferences", { method: "PUT", body: { key, value } }),
  deletePreference: (key) => request(`/preferences/${encodeURIComponent(key)}`, { method: "DELETE" }),

  goals: () => request("/goals"),
  addGoal: (title) => request("/goals", { method: "POST", body: { title } }),
  setGoalStatus: (id, status) => request(`/goals/${id}`, { method: "PATCH", body: { status } }),
  deleteGoal: (id) => request(`/goals/${id}`, { method: "DELETE" }),
  planGoal: (id) => request(`/goals/${id}/plan`, { method: "POST" }),
};
