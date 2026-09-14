import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

for key in ["GROQ_API_KEY", "PG_HOST", "PG_PORT", "PG_USER", "PG_PASSWORD", "PG_DATABASE"]:
    if key not in os.environ and key in st.secrets:
        os.environ[key] = st.secrets[key]

from groq import Groq
import memory
from rag import query_documents

memory.init_db()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.title("My AI OS")

tab_chat, tab_notes, tab_prefs, tab_goals = st.tabs(["💬 Chat", "📝 Notes", "⚙️ Preferences", "🎯 Goals"])

with tab_prefs:
    st.subheader("Preferences")
    st.caption("These get included whenever the system responds or analyzes something.")

    with st.form("new_pref", clear_on_submit=True):
        pref_key = st.text_input("Setting name (e.g. 'tone', 'focus_area')")
        pref_value = st.text_input("Value (e.g. 'concise and direct', 'backend projects')")
        submitted = st.form_submit_button("Save Preference")
        if submitted and pref_key and pref_value:
            memory.save_preference(pref_key, pref_value)
            st.success("Preference saved!")
            st.rerun()

    st.divider()

    prefs = memory.load_preferences()
    if not prefs:
        st.info("No preferences set yet.")
    for key, value in prefs.items():
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{key}**: {value}")
        if col2.button("Delete", key=f"delpref_{key}"):
            memory.delete_preference(key)
            st.rerun()

with tab_chat:
    A=True
    # ... all your EXISTING chat code goes here: the sidebar GitHub analyzer,
    # the messages loop, and the chat_input block — just indent it one level
    # under this `with tab_chat:` block

with tab_notes:
    st.subheader("Your Notes")

    with st.form("new_note", clear_on_submit=True):
        note_title = st.text_input("Title")
        note_content = st.text_area("Content")
        submitted = st.form_submit_button("Save Note")
        if submitted and note_title and note_content:
            memory.save_note(note_title, note_content)
            st.success("Note saved!")
            st.rerun()

    st.divider()

    notes = memory.load_notes()
    if not notes:
        st.info("No notes yet — add one above.")
    for note in notes:
        with st.expander(f"{note['title']} — {note['timestamp'][:16]}"):
            st.write(note['content'])
            if st.button("Delete", key=f"del_{note['id']}"):
                memory.delete_note(note['id'])
                st.rerun()

with st.sidebar:
    st.subheader("Analyze a GitHub repo")
    repo_owner = st.text_input("Owner (username)")
    repo_name = st.text_input("Repo name")
    if st.button("Analyze"):
        if repo_owner and repo_name:
            with st.spinner("Analyzing repository..."):
                from agent import analyze_repo_for_resume
                result = analyze_repo_for_resume(repo_owner, repo_name)
            st.session_state.messages.append({"role": "assistant", "content": result})
            memory.save_message("assistant", result)
            st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = memory.load_messages()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    memory.save_message("user", user_input)
    with st.chat_message("user"):
        st.write(user_input)

    relevant_chunks = query_documents(user_input)
    context_text = "\n\n".join(relevant_chunks)

    augmented_messages = st.session_state.messages.copy()
    if context_text:
        augmented_messages.insert(0, {
            "role": "system",
            "content": f"Use this context if relevant:\n\n{context_text}"
        })

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=augmented_messages
    )
    reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    memory.save_message("assistant", reply)
    with st.chat_message("assistant"):
        st.write(reply)

with tab_goals:
    st.subheader("Goals")

    with st.form("new_goal", clear_on_submit=True):
        goal_title = st.text_input("New goal")
        submitted = st.form_submit_button("Add Goal")
        if submitted and goal_title:
            memory.save_goal(goal_title)
            st.success("Goal added!")
            st.rerun()

    st.divider()

    goals = memory.load_goals()
    active = [g for g in goals if g["status"] == "active"]
    done = [g for g in goals if g["status"] == "done"]

    st.write(f"**Active ({len(active)})**")
    for g in active:
        col1, col2, col3 = st.columns([4, 1, 1])
        col1.write(g["title"])
        if col2.button("✅ Done", key=f"done_{g['id']}"):
            memory.update_goal_status(g["id"], "done")
            st.rerun()
        if col3.button("🗑️", key=f"delgoal_{g['id']}"):
            memory.delete_goal(g["id"])
            st.rerun()

    if done:
        st.write(f"**Completed ({len(done)})**")
        for g in done:
            st.write(f"~~{g['title']}~~")