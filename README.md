# AI-Native Life

> A personal AI workspace with persistent memory, retrieval, tool-using agents and self-evaluation. Not just a chatbot.

**Live app:** [ai-os-frontend.vercel.app](https://ai-os-frontend.vercel.app)
**API docs:** [ai-native-life.onrender.com/docs](https://ai-native-life.onrender.com/docs)

> The backend runs on a free tier and sleeps when idle, so the first request after a quiet period can take up to a minute.

<!--
Add two screenshots to a docs/ folder, then uncomment these lines:
![Chat with a repo analysis](docs/screenshot-chat.png)
![Goals and notes](docs/screenshot-goals.png)
-->

## What it does

Sign up, then point the system at any public GitHub repository. It pulls the real repo data (metadata, README, file list), reasons over it with an LLM, checks its own answer for accuracy, and tells you what to fix before you put the project on a resume. Around that core sits a workspace the agents can read from and write to:

- **Chat** with history that persists across sessions and devices
- **Repo analysis**: resume-readiness score, strengths, weaknesses and next steps, grounded in the actual repo
- **Resume bullets**: 3-4 bullet points written only from what the repo evidences
- **Goals and planning**: turn a goal into a 4-week plan, saved as a note
- **Notes and preferences**: stored per user and fed into every agent prompt
- **Autonomous memory**: after an analysis, the agent can decide on its own that something is worth saving as a note or goal

## Architecture

```
 Browser: React (Vite) on Vercel
        |  HTTPS + JWT
        v
 FastAPI backend on Render  (api.py)
        |
        +--> agent.py ........ analysis, evaluation, resume bullets, planning
        |        +--> github_tool.py ... GitHub REST API (public repos)
        |        +--> Groq LLM ......... openai/gpt-oss-20b
        |
        +--> memory.py ....... users, messages, notes, preferences, goals, usage
        |        +--> PostgreSQL on Aiven
        |
        +--> rag.py .......... ChromaDB retrieval (optional, local only)
```

### How an analysis works

1. **Act:** fetch repo metadata, README and top-level files from the GitHub API.
2. **Reason:** build a prompt from the repo data plus the user's saved preferences and active goals.
3. **Evaluate:** a second model call reviews the draft for invented claims and generic advice.
4. **Revise:** if the reviewer rejects it, the model rewrites the answer using the critique.
5. **Remember:** a final call decides whether one note or goal is worth saving automatically.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React 18, Vite, react-markdown (hosted on Vercel) |
| Backend | FastAPI, Uvicorn (hosted on Render) |
| LLM | Groq API, `openai/gpt-oss-20b` |
| Database | PostgreSQL (Aiven free tier) |
| Retrieval | ChromaDB with local embeddings |
| Auth | bcrypt password hashes, JWT bearer tokens |
| Tools | GitHub REST API |

## Security and limits

- Passwords are stored as bcrypt hashes. Sessions use signed JWTs that expire after 7 days.
- Every database query for messages, notes, preferences and goals is filtered by the logged-in user's id, so accounts cannot see each other's data.
- Request bodies are validated (lengths, and a strict pattern for GitHub owner and repo names).
- Each user has a daily AI budget (30 units by default, set with `DAILY_AI_LIMIT`). Chat, bullets and plans cost 1; a repo analysis costs 3. Usage is stored in Postgres and resets at 00:00 UTC.
- All secrets live on the backend only. The frontend contains just the public API address.

Known limitations: the limit is per account, not per person; the ChromaDB store is local-only and is not part of the deployed backend; chat sends the most recent 30 messages to the model.

## Run it locally

You need Python 3.11+, Node.js 18+, a free [Groq API key](https://console.groq.com) and a PostgreSQL database.

**Backend**

```bash
git clone https://github.com/hemand18/AI-Native-Life.git
cd AI-Native-Life
python -m pip install -r requirements-api.txt
# optional, enables local document retrieval:
python -m pip install chromadb
```

Copy `.env.example` to `.env` and fill in the values, then:

```bash
python -m uvicorn api:app --reload --port 8000
```

Open `http://localhost:8000/docs` to try the API.

**Frontend**

```bash
cd ai-os-frontend
npm install
npm run dev
```

Open `http://localhost:5173`. In development the app calls `http://localhost:8000` automatically.

### Environment variables

| Variable | Where | Purpose |
|---|---|---|
| `GROQ_API_KEY` | backend | LLM access |
| `PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE` | backend | PostgreSQL connection |
| `JWT_SECRET` | backend | Signs login tokens. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALLOWED_ORIGINS` | backend | Comma-separated frontend addresses allowed by CORS |
| `DAILY_AI_LIMIT` | backend, optional | Daily AI units per user (default 30) |
| `VITE_API_URL` | frontend, optional | Override the backend address |

## Project layout

```
api.py              FastAPI routes, auth, rate limiting
agent.py            analysis, evaluation, writing and planning agents
memory.py           PostgreSQL access, per-user data
github_tool.py      GitHub API tool
rag.py              ChromaDB retrieval
app.py              original Streamlit prototype (first UI for the same backend logic)
ai-os-frontend/     React frontend
```

## What I learned building this

I built it layer by layer to understand what agent frameworks hide:

- How retrieval works under the hood: chunking, embeddings, similarity search
- How to hand-write an agent loop and an evaluate-then-revise step instead of reaching for a framework
- Why separating memory, agents, tools and interface made two complete UI rewrites (Streamlit, then React) cheap
- Real deployment problems: environment-variable scoping, a database moved from SQLite to MySQL to PostgreSQL, CORS, build-time versus run-time configuration, and recovering from an API key caught by GitHub's secret scanning

## License

MIT. See [LICENSE](LICENSE).