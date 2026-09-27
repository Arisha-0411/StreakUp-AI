"""
app.py — DoneRight AI: a Streamlit task-management app
Run with: streamlit run app.py
"""

import importlib

st = importlib.import_module("streamlit")

import auth
import tasks as task_store
import rewards
from theme import apply_theme

st.set_page_config(page_title="StreakUp AI", page_icon="✅", layout="wide")

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = False
if "page" not in st.session_state:
    st.session_state.page = "Overview"

AVATARS = {"male": "🧑", "female": "👩"}


def avatar_for(username: str) -> str:
    profile = auth.get_user_profile(username)
    gender = profile.get("gender", "male")
    return AVATARS.get(gender, "🧑")


# ---------------------------------------------------------------------------
# Auth screens
# ---------------------------------------------------------------------------
def render_auth_screen(palette):
    st.title("✅ StreakUp AI")
    st.caption(" Organize Tasks, Build Streaks, Earn Badges.")

    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")
            if submitted:
                success, message = auth.login(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.show_welcome = True
                    st.rerun()
                else:
                    st.error(message)

    with tab_signup:
        with st.form("signup_form"):
            full_name = st.text_input("Full name")
            new_username = st.text_input("Choose a username")
            new_password = st.text_input("Choose a password", type="password")
            gender = st.selectbox("Gender (for your avatar)", ["male", "female"])
            submitted = st.form_submit_button("Sign Up")
            if submitted:
                success, message = auth.signup(new_username, new_password, full_name, gender)
                if success:
                    st.success(message)
                else:
                    st.error(message)


# ---------------------------------------------------------------------------
# Page: Overview
# ---------------------------------------------------------------------------
def render_overview(username, palette):
    st.header("📊 Overview")
    counts = task_store.task_counts(username)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", counts["total"])
    col2.metric("Completed", counts["completed"])
    col3.metric("Pending", counts["pending"])

    progress = (counts["completed"] / counts["total"]) if counts["total"] else 0
    st.write("**Overall progress**")
    st.progress(progress)

    fig = task_store.make_pie_chart(
        username,
        accent=palette["accent"],
        bg=palette["card_bg"],
        text_color=palette["text"],
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Page: Add Task
# ---------------------------------------------------------------------------
def render_add_task(username):
    st.header("➕ Add a Task")
    st.caption("Priority is predicted automatically from your task's title, description, and due date.")
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task title")
        description = st.text_area("Description (optional)")
        due_date = st.date_input("Due date", value=None)
        submitted = st.form_submit_button("Add Task")
        if submitted:
            if not title.strip():
                st.error("Please enter a task title.")
            else:
                assigned_priority = task_store.add_task(
                    username,
                    title.strip(),
                    description.strip(),
                    str(due_date) if due_date else "",
                )
                st.success(
                    f"Task '{title}' was added successfully! 🎉 "
                    f"Predicted priority: **{assigned_priority}**"
                )

    with st.expander("💡 How is priority decided? (click to see example keywords)"):
        st.markdown(
            """
            The priority is picked automatically based on the words in your **title**
            and **description**, and on how soon your **due date** is.

            **🔴 Words that push priority to High:**
            `urgent`, `asap`, `important`, `critical`, `exam`, `deadline`,
            `interview`, `submission`, `emergency`, `due today`, `final`,
            `presentation`, `meeting`, `immediately`

            **🟢 Words that push priority to Low:**
            `someday`, `optional`, `later`, `whenever`, `low priority`,
            `maybe`, `eventually`, `casual`, `no rush`

            **🟡 No matching words?** Priority falls back to your due date:
            - Due in 1 day or less → **High**
            - Due within 5 days → **Medium**
            - Due later than that, or no due date → **Low**
            - No keywords and no due date at all → defaults to **Medium**
            """
        )


# ---------------------------------------------------------------------------
# Page: All Tasks
# ---------------------------------------------------------------------------
def render_all_tasks(username):
    col_title, col_avatar = st.columns([5, 1])
    with col_title:
        st.header("📋 All Tasks")
    with col_avatar:
        st.markdown(
            f"<div style='text-align:right; font-size:2.5em;'>{avatar_for(username)}</div>",
            unsafe_allow_html=True,
        )

    user_tasks = task_store.get_user_tasks(username)
    if not user_tasks:
        st.info("No tasks yet — add one from the 'Add Task' page!")
        return

    # Suggestion box: which pending task to tackle next
    suggestion = task_store.suggest_next_task(username)
    if suggestion:
        st.info(
            f"🎯 **Suggested next task:** {suggestion['title']} "
            f"({suggestion.get('priority', 'Medium')} priority"
            + (f", due {suggestion['due_date']}" if suggestion.get("due_date") else "")
            + ")"
        )

    PRIORITY_BADGE = {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}

    for t in user_tasks:
        with st.container():
            st.markdown('<div class="task-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([5, 2, 1])
            with c1:
                status = "✅" if t["completed"] else "🕒"
                priority_label = PRIORITY_BADGE.get(t.get("priority", "Medium"), "🟡 Medium")
                st.markdown(f"**{status} {t['title']}**  &nbsp; {priority_label}")
                if t["description"]:
                    st.caption(t["description"])
                if t["due_date"]:
                    st.caption(f"Due: {t['due_date']}")
            with c2:
                pass