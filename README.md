# AI-Native Life — Personal AI Operating System

> An AI system that actually helps run your digital work — not just a chatbot.

**Live demo:** [ai-native-life-gzfw4zaenxnmgh8drzl7ia.streamlit.app](https://ai-native-life-gzfw4zaenxnmgh8drzl7ia.streamlit.app)
**Repo:** [github.com/hemand18/AI-Native-Life](https://github.com/hemand18/AI-Native-Life)

## What this is

AI-Native Life is a personal AI platform built from scratch to explore what a real "AI operating system" looks like under the hood — not a wrapper around a chat API, but a system with persistent memory, retrieval, tool-calling, agentic reasoning, and self-evaluation working together.

The flagship example: point it at any public GitHub repository, and it pulls the real repo data (README, file structure, metadata), reasons over it with an LLM, checks its own output for accuracy, and tells you exactly what to fix before putting that project on your resume.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    Interface                      │
│         Streamlit — Chat / Notes / Prefs / Goals  │
└───────────────────────┬───────────────────────────┘
                         │
┌───────────────────────▼───────────────────────────┐
│                      Agent                         │
│   Repo Analysis Agent (ACT → OBSERVE → REASON)     │
└──────┬──────────────┬──────────────┬───────────────┘
       │              │              │
┌──────▼─────┐  ┌─────▼──────┐  ┌────▼────────┐
│   Tools    │  │    RAG     │  │  Evaluation  │
│ GitHub API │  │  ChromaDB  │  │ Self-critique │
└────────────┘  └────────────┘  │  + revision   │
                                 └──────────────┘
       │
┌──────▼──────────────────────────────────────────┐
│                    Memory                         │
│  PostgreSQL — Messages · Notes · Preferences ·    │
│  Goals — including autonomous writes by the agent │
└────────────────────────────────────────────────────┘
```

## Features

- **Persistent chat memory** — every conversation survives restarts (PostgreSQL, not session state)
- **Retrieval-augmented generation** — answers grounded in real documents via a local vector store
- **Real tool use** — pulls live data from the GitHub API (repo metadata, README, file listing)
- **Agentic reasoning** — a working ACT → OBSERVE → REASON loop, hand-built rather than framework-dependent
- **Self-evaluation** — a second LLM pass critiques the first response for accuracy and specificity before it's shown to the user, and triggers a revision if needed
- **Preferences & Goals** — the agent reads stored preferences and active goals and factors them into its recommendations
- **Autonomous memory writing** — the agent can decide on its own that something is worth remembering and save it as a note or goal, without manual input

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| LLM | [Groq API](https://groq.com) (`openai/gpt-oss-20b`) | Free tier, fast inference |
| Memory | PostgreSQL via [Aiven](https://aiven.io) | Free managed cloud database |
| Retrieval | [ChromaDB](https://www.trychroma.com/) | Local, free vector store with built-in embeddings |
| Interface | [Streamlit](https://streamlit.io) | Fast to build, free hosting on Streamlit Community Cloud |
| Tools | GitHub REST API | Free, no auth needed for public repos |

Every component in this stack is free — no paid API keys or hosting required to run or extend this project.

## Setup

```bash
git clone https://github.com/hemand18/AI-Native-Life.git
cd AI-Native-Life
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your-groq-key
PG_HOST=your-postgres-host
PG_PORT=your-postgres-port
PG_USER=your-postgres-user
PG_PASSWORD=your-postgres-password
PG_DATABASE=your-postgres-database
```

Run it:
```bash
python -m streamlit run app.py
```

## What I learned building this

This project was built step by step, layer by layer, specifically to understand what's actually happening inside "agentic AI" systems rather than relying on a framework to hide the details:

- How retrieval-augmented generation actually works under the hood (chunking, embeddings, vector similarity search)
- How to hand-build an agent loop (tool call → observation → reasoning) without LangChain or similar frameworks
- Why evaluation/self-critique loops matter for reducing hallucinated or generic AI output
- Real production debugging: environment variable scoping, database migrations (SQLite → MySQL → PostgreSQL), and secret management (including recovering from an exposed API key caught by GitHub's push protection)

## License

MIT