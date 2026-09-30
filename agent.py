import os
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from github_tool import get_repo_info, get_readme, get_file_list

try:
    from groq import Groq
except ImportError:  # pragma: no cover - optional dependency during local setup
    Groq = None

import memory

client = Groq(api_key=os.environ.get("GROQ_API_KEY")) if Groq and os.environ.get("GROQ_API_KEY") else None
MODEL = "openai/gpt-oss-20b"


def _ask(prompt):
    if client is None:
        return (
            "AI analysis is unavailable because GROQ_API_KEY is missing or the Groq SDK "
            "is not installed. Add your API key to the .env file or Streamlit secrets."
        )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def _prefs_text(user_id):
    prefs = memory.load_preferences(user_id)
    return "\n".join(f"- {k}: {v}" for k, v in prefs.items()) if prefs else "None set."


def _goals_text(user_id):
    goals = memory.load_goals(user_id)
    active = [g["title"] for g in goals if g["status"] == "active"]
    return "\n".join(f"- {g}" for g in active) if active else "None set."


def _repo_context(owner, repo, include_stars=True):
    info = get_repo_info(owner, repo)
    if info is None:
        return None
    readme = get_readme(owner, repo)
    files = get_file_list(owner, repo)
    stars_line = f"Stars: {info['stars']}\n" if include_stars else ""
    return f"""
Repository: {info['name']}
Description: {info['description'] or 'None provided'}
Primary language: {info['language'] or 'Not detected'}
{stars_line}Top-level files: {', '.join(files) if files else 'None found'}

README content:
{readme[:3000] if readme else 'No README found.'}
"""


def evaluate_analysis(context, draft_analysis):
    return _ask(f"""You are a strict quality reviewer. Below is the raw repo data an AI
analyzed, and the analysis it produced. Check the analysis against these criteria:

1. Is every claim actually grounded in the repo data below, or did it invent/assume anything?
2. Is the feedback specific to THIS repo, or could it apply to literally any project (too generic)?
3. Is the resume-readiness score justified by what's actually in the data?

REPO DATA:
{context}

DRAFT ANALYSIS:
{draft_analysis}

If the analysis is accurate, specific, and well-grounded, respond with exactly: APPROVED
If it has problems, respond with: REVISE — followed by a specific, one-paragraph explanation
of what's wrong.
""")


def extract_memory_worthy_info(context, final_analysis):
    raw = _ask(f"""Based on this repo analysis, decide if there's ONE genuinely useful
thing worth saving for later reference — either a note (a fact/lesson worth remembering)
or a goal (something the user should clearly do next based on this analysis).

Only suggest something if it's specific and non-obvious. If nothing stands out, say none.

REPO DATA:
{context}

ANALYSIS:
{final_analysis}

Respond with ONLY valid JSON, no other text, in exactly this format:
{{"type": "note", "title": "short title", "content": "the detail"}}
or
{{"type": "goal", "title": "short actionable goal"}}
or
{{"type": "none"}}
""").strip()

    try:
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {"type": "none"}


def analyze_repo_for_resume(user_id, owner, repo):
    context = _repo_context(owner, repo)
    if context is None:
        return "Couldn't find that repository. Check the owner/repo name and that it's public."

    prompt = f"""You are reviewing a student's GitHub project to help them decide what to
improve before listing it on their resume. Here is the real data pulled from their repo:

{context}

User's stated preferences (respect these in your response):
{_prefs_text(user_id)}

User's active goals (consider these when giving recommendations):
{_goals_text(user_id)}

Give feedback in this exact structure:
1. **Resume-readiness score** (1-10) with a one-line reason
2. **What's already strong** (2-3 bullet points, only if genuinely true — don't invent positives)
3. **What's missing or weak** (specific, tied to what you actually see above)
4. **Concrete next steps** (3-5 specific actions, ordered by impact)

Be honest and specific. Don't give generic advice that would apply to any project.
"""

    draft = _ask(prompt)
    verdict = evaluate_analysis(context, draft)

    if verdict.strip().startswith("APPROVED"):
        final_result = draft
    else:
        final_result = _ask(f"""Your previous analysis had this issue: {verdict}

Here is the original repo data:
{context}

Please provide a corrected analysis, fixing the specific issue raised, using the same
4-part structure (score, strengths, weaknesses, next steps).""")

    memory_note = ""
    try:
        extracted = extract_memory_worthy_info(context, final_result)
        if extracted.get("type") == "note":
            memory.save_note(user_id, extracted["title"], extracted["content"])
            memory_note = f"\n\n---\n🧠 *Auto-saved a note: \"{extracted['title']}\"*"
        elif extracted.get("type") == "goal":
            memory.save_goal(user_id, extracted["title"])
            memory_note = f"\n\n---\n🎯 *Auto-saved a goal: \"{extracted['title']}\"*"
    except Exception:
        pass  # memory-saving must never break the analysis output

    return final_result + memory_note


def draft_resume_bullets(user_id, owner, repo):
    context = _repo_context(owner, repo, include_stars=False)
    if context is None:
        return "Couldn't find that repository. Check the owner/repo name and that it's public."

    return _ask(f"""You are a resume-writing assistant. Based ONLY on the real project data below,
write 3-4 resume bullet points for this project. Follow these rules strictly:

- Start each bullet with a strong action verb (Built, Designed, Implemented, Engineered, etc.)
- Only claim things that are actually supported by the data below — never invent metrics,
  technologies, or outcomes that aren't evidenced
- If there's no evidence of impact/results/metrics, write the bullet around what was built and
  how, not a fabricated impact number
- Keep each bullet to one line, resume-style (no full sentences with "I")

User's preferences to respect: {_prefs_text(user_id)}

PROJECT DATA:
{context}

Return ONLY the bullet points, one per line, starting with "- "
""")


def plan_goal(user_id, goal_title):
    return _ask(f"""You are a planning assistant. Break the following goal into a realistic
4-week plan. Be specific and actionable. Avoid vague advice like "work hard" or "practice more."

GOAL: {goal_title}

User's preferences to respect: {_prefs_text(user_id)}

Format your response as:
**Week 1:** (2-3 concrete tasks)
**Week 2:** (2-3 concrete tasks)
**Week 3:** (2-3 concrete tasks)
**Week 4:** (2-3 concrete tasks)

Keep each task one line, specific enough that the person knows exactly what to do.
""")