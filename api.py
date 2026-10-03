import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

import memory
from agent import analyze_repo_for_resume, draft_resume_bullets, plan_goal

try:
    from rag import query_documents
except Exception:
    def query_documents(query_text, n_results=3):
        return []

MODEL = "openai/gpt-oss-20b"

try:
    from groq import Groq
    _key = os.environ.get("GROQ_API_KEY")
    groq_client = Groq(api_key=_key) if _key else None
except Exception:
    groq_client = None

JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    JWT_SECRET = secrets.token_hex(32)
    print("WARNING: JWT_SECRET is not set. Using a temporary secret, so logins reset on every restart.")
JWT_ALGO = "HS256"
TOKEN_HOURS = 24 * 7

# Daily AI budget per user, in "units". Chat/bullets/plan cost 1, a repo analysis costs 3
# (it makes several model calls). Change it with the DAILY_AI_LIMIT environment variable.
DAILY_LIMIT = max(int(os.environ.get("DAILY_AI_LIMIT", "30")), 3)


def init_usage_table():
    conn = memory.get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_usage (
                user_id INT NOT NULL,
                day DATE NOT NULL,
                used INT NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, day)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def spend_quota(user_id, cost):
    """Atomically add `cost` to today's usage. Returns False if that would pass the limit."""
    day = datetime.now(timezone.utc).date()
    conn = memory.get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO ai_usage (user_id, day, used) VALUES (%s, %s, %s)
            ON CONFLICT (user_id, day) DO UPDATE SET used = ai_usage.used + %s
            WHERE ai_usage.used + %s <= %s
            RETURNING used
        """, (user_id, day, cost, cost, cost, DAILY_LIMIT))
        row = c.fetchone()
        conn.commit()
        return row is not None
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app):
    app.state.db_startup_error = None
    try:
        memory.init_db()
        init_usage_table()
    except Exception as exc:
        app.state.db_startup_error = str(exc)
        print(f"WARNING: database startup failed: {exc}")
    yield


app = FastAPI(title="AI-Native Life API", lifespan=lifespan)

origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

bearer = HTTPBearer(auto_error=False)


# ---------- auth helpers ----------

def make_token(user_id, username):
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if creds is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    try:
        data = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
        return {"user_id": int(data["sub"]), "username": data["username"]}
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Session expired, please log in again")


def quota(cost):
    """Dependency for AI endpoints: logs the user in and charges `cost` units against today's limit."""
    def dep(user=Depends(current_user)):
        if not spend_quota(user["user_id"], cost):
            raise HTTPException(
                status_code=429,
                detail=f"Daily AI limit reached ({DAILY_LIMIT} units). It resets at 00:00 UTC.",
            )
        return user
    return dep


def run_ai(fn, *args):
    """Run an AI call and turn any failure into a clean 502 instead of a crash."""
    try:
        return fn(*args)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"The AI request failed ({type(e).__name__}). Check the backend logs.")


# ---------- request models ----------

GITHUB_NAME = r"^[A-Za-z0-9_.-]{1,100}$"


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class RepoIn(BaseModel):
    owner: str = Field(pattern=GITHUB_NAME)
    repo: str = Field(pattern=GITHUB_NAME)


class NoteIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=20000)


class PrefIn(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=1000)


class GoalIn(BaseModel):
    title: str = Field(min_length=1, max_length=500)


class GoalStatusIn(BaseModel):
    status: Literal["active", "done"]


# ---------- routes ----------

@app.get("/health")
def health():
    try:
        conn = memory.get_connection()
        conn.close()
        database_ready = True
    except Exception:
        database_ready = False
    return {
        "ok": True,
        "ai_configured": groq_client is not None,
        "database_ready": database_ready,
    }

@app.post("/auth/signup", status_code=201)
def signup(body: Credentials):
    if not memory.create_user(body.username.strip(), body.password):
        raise HTTPException(status_code=409, detail="That username is taken")
    return {"ok": True}


@app.post("/auth/login")
def login(body: Credentials):
    uid = memory.verify_user(body.username.strip(), body.password)
    if uid is None:
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {"token": make_token(uid, body.username.strip()), "username": body.username.strip()}


# chat

@app.get("/messages")
def get_messages(user=Depends(current_user)):
    return memory.load_messages(user["user_id"])


@app.post("/chat")
def chat(body: ChatIn, user=Depends(quota(1))):
    if groq_client is None:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured on the server")
    uid = user["user_id"]
    text = body.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message is empty")

    memory.save_message(uid, "user", text)
    history = memory.load_messages(uid)[-30:]

    try:
        chunks = query_documents(text)
    except Exception:
        chunks = []

    messages = list(history)
    if chunks:
        messages.insert(0, {"role": "system", "content": "Use this context if relevant:\n\n" + "\n\n".join(chunks)})

    def call():
        r = groq_client.chat.completions.create(model=MODEL, messages=messages)
        return r.choices[0].message.content

    reply = run_ai(call)
    memory.save_message(uid, "assistant", reply)
    return {"reply": reply}


@app.post("/analyze")
def analyze(body: RepoIn, user=Depends(quota(3))):
    uid = user["user_id"]
    memory.save_message(uid, "user", f"Analyze {body.owner}/{body.repo}")
    reply = run_ai(analyze_repo_for_resume, uid, body.owner, body.repo)
    memory.save_message(uid, "assistant", reply)
    return {"reply": reply}


@app.post("/bullets")
def bullets(body: RepoIn, user=Depends(quota(1))):
    uid = user["user_id"]
    memory.save_message(uid, "user", f"Draft resume bullets for {body.owner}/{body.repo}")
    reply = run_ai(draft_resume_bullets, uid, body.owner, body.repo)
    memory.save_message(uid, "assistant", reply)
    return {"reply": reply}


# notes

@app.get("/notes")
def get_notes(user=Depends(current_user)):
    return memory.load_notes(user["user_id"])


@app.post("/notes", status_code=201)
def add_note(body: NoteIn, user=Depends(current_user)):
    memory.save_note(user["user_id"], body.title.strip(), body.content.strip())
    return {"ok": True}


@app.delete("/notes/{note_id}")
def remove_note(note_id: int, user=Depends(current_user)):
    memory.delete_note(user["user_id"], note_id)
    return {"ok": True}


# preferences

@app.get("/preferences")
def get_preferences(user=Depends(current_user)):
    prefs = memory.load_preferences(user["user_id"])
    return [{"key": k, "value": v} for k, v in prefs.items()]


@app.put("/preferences")
def put_preference(body: PrefIn, user=Depends(current_user)):
    memory.save_preference(user["user_id"], body.key.strip(), body.value.strip())
    return {"ok": True}


@app.delete("/preferences/{key}")
def remove_preference(key: str, user=Depends(current_user)):
    memory.delete_preference(user["user_id"], key)
    return {"ok": True}


# goals

@app.get("/goals")
def get_goals(user=Depends(current_user)):
    return memory.load_goals(user["user_id"])


@app.post("/goals", status_code=201)
def add_goal(body: GoalIn, user=Depends(current_user)):
    memory.save_goal(user["user_id"], body.title.strip())
    return {"ok": True}


@app.patch("/goals/{goal_id}")
def set_goal_status(goal_id: int, body: GoalStatusIn, user=Depends(current_user)):
    memory.update_goal_status(user["user_id"], goal_id, body.status)
    return {"ok": True}


@app.delete("/goals/{goal_id}")
def remove_goal(goal_id: int, user=Depends(current_user)):
    memory.delete_goal(user["user_id"], goal_id)
    return {"ok": True}


@app.post("/goals/{goal_id}/plan")
def plan_for_goal(goal_id: int, user=Depends(quota(1))):
    uid = user["user_id"]
    goal = next((g for g in memory.load_goals(uid) if g["id"] == goal_id), None)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    plan = run_ai(plan_goal, uid, goal["title"])
    memory.save_note(uid, f"Plan: {goal['title']}", plan)
    return {"note_title": f"Plan: {goal['title']}"}