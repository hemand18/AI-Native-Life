import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import Groq

load_dotenv()

app = FastAPI(title="AI-Native Life API", version="1.0.0")

origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_client = (
    Groq(api_key=os.environ["GROQ_API_KEY"])
    if os.getenv("GROQ_API_KEY")
    else None
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


@app.get("/")
def root():
    return {"message": "AI-Native Life API is running"}


@app.get("/health")
def health():
    return {"ok": True, "status": "healthy"}


@app.post("/chat")
def chat(body: ChatRequest):
    if groq_client is None:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured",
        )

    try:
        result = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": body.message}],
        )
        return {"reply": result.choices[0].message.content or ""}
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Groq request failed. Check server logs and API quota.",
        )
