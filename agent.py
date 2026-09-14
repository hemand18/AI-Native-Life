import os
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from github_tool import get_repo_info, get_readme, get_file_list
from groq import Groq
import memory

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def evaluate_analysis(context, draft_analysis):
    eval_prompt = f"""You are a strict quality reviewer. Below is the raw repo data an AI
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
of what's wrong (e.g. "invented a claim about tests existing when none were found" or
"feedback is generic boilerplate that ignores the actual file list").
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": eval_prompt}]
    )
    return response.choices[0].message.content


def extract_memory_worthy_info(context, final_analysis):
    extract_prompt = f"""Based on this repo analysis, decide if there's ONE genuinely useful
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
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": extract_prompt}]
    )

    raw = response.choices[0].message.content.strip()

    try:
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        return data
    except (json.JSONDecodeError, ValueError):
        return {"type": "none"}


def analyze_repo_for_resume(owner, repo):
    # STEP 1: ACT — call the tool to gather real data
    info = get_repo_info(owner, repo)
    readme = get_readme(owner, repo)
    files = get_file_list(owner, repo)

    if info is None:
        return "Couldn't find that repository. Check the owner/repo name and that it's public."

    # STEP 2: OBSERVE — assemble what we found into context
    context = f"""
Repository: {info['name']}
Description: {info['description'] or 'None provided'}
Primary language: {info['language'] or 'Not detected'}
Stars: {info['stars']}
Top-level files: {', '.join(files) if files else 'None found'}

README content:
{readme[:3000] if readme else 'No README found.'}
"""

    prefs = memory.load_preferences()
    prefs_text = "\n".join(f"- {k}: {v}" for k, v in prefs.items()) if prefs else "None set."

    goals = memory.load_goals()
    active_goals = [g["title"] for g in goals if g["status"] == "active"]
    goals_text = "\n".join(f"- {g}" for g in active_goals) if active_goals else "None set."

    # STEP 3: REASON — ask the LLM to critique it specifically for resume purposes
    prompt = f"""You are reviewing a student's GitHub project to help them decide what to
improve before listing it on their resume. Here is the real data pulled from their repo:

{context}

User's stated preferences (respect these in your response):
{prefs_text}

User's active goals (consider these when giving recommendations):
{goals_text}

Give feedback in this exact structure:
1. **Resume-readiness score** (1-10) with a one-line reason
2. **What's already strong** (2-3 bullet points, only if genuinely true — don't invent positives)
3. **What's missing or weak** (specific, tied to what you actually see above — e.g. missing README, unclear description, no visible results/metrics)
4. **Concrete next steps** (3-5 specific actions, ordered by impact)

Be honest and specific. Don't give generic advice that would apply to any project.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )

    draft = response.choices[0].message.content

    # STEP 4: EVALUATE — self-check before returning to the user
    verdict = evaluate_analysis(context, draft)

    if verdict.strip().startswith("APPROVED"):
        final_result = draft
    else:
        revise_prompt = f"""Your previous analysis had this issue: {verdict}

Here is the original repo data:
{context}

Please provide a corrected analysis, fixing the specific issue raised, using the same
4-part structure (score, strengths, weaknesses, next steps)."""

        revised = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": revise_prompt}]
        )
        final_result = revised.choices[0].message.content

    # STEP 5: AUTO-MEMORY — let the agent decide if something's worth saving
    memory_note = ""
    try:
        extracted = extract_memory_worthy_info(context, final_result)
        if extracted.get("type") == "note":
            memory.save_note(extracted["title"], extracted["content"])
            memory_note = f"\n\n---\n🧠 *Auto-saved a note: \"{extracted['title']}\"*"
        elif extracted.get("type") == "goal":
            memory.save_goal(extracted["title"])
            memory_note = f"\n\n---\n🎯 *Auto-saved a goal: \"{extracted['title']}\"*"
    except Exception:
        pass  # never let memory-saving break the actual analysis output

    return final_result + memory_note