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
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task title")
        description = st.text_area("Description (optional)")
        due_date = st.date_input("Due date", value=None)
        submitted = st.form_submit_button("Add Task")
        if submitted:
            if not title.strip():
                st.error("Please enter a task title.")
            else:
                task_store.add_task(
                    username,
                    title.strip(),
                    description.strip(),
                    str(due_date) if due_date else "",
                )
                st.success(f"Task '{title}' Added Successfully! 🎉")


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

    for t in user_tasks:
        with st.container():
            st.markdown('<div class="task-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([5, 2, 1])
            with c1:
                status = "✅" if t["completed"] else "🕒"
                st.markdown(f"**{status} {t['title']}**")
                if t["description"]:
                    st.caption(t["description"])
                if t["due_date"]:
                    st.caption(f"Due: {t['due_date']}")
            with c2:
                label = "Mark Pending" if t["completed"] else "Mark Complete"
                if st.button(label, key=f"toggle_{t['id']}"):
                    task_store.toggle_complete(t["id"])
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"delete_{t['id']}"):
                    task_store.delete_task(t["id"])
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page: Rewards
# ---------------------------------------------------------------------------
def render_rewards(username):
    st.header("🏆 Rewards")

    streak = rewards.compute_streak(username)
    st.subheader(f"🔥 Current Streak: {streak} day{'s' if streak != 1 else ''}")
    st.caption("Complete at least one task per day to keep your streak alive!")

    st.markdown("---")
    st.subheader("🎖️ Badges")

    badges = rewards.get_badges_status(username)
    cols = st.columns(3)
    for i, badge in enumerate(badges):
        with cols[i % 3]:
            css_class = "badge-card" if badge["earned"] else "badge-card badge-locked"
            st.markdown(
                f"""
                <div class="{css_class}">
                    <div style="font-size:2.5em;">{badge['emoji']}</div>
                    <b>{badge['label']}</b>
                    <p style="font-size:0.85em;">{badge['desc']}</p>
                    <p style="font-size:0.8em;">{'Earned ✅' if badge['earned'] else 'Locked 🔒'}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Page: Profile
# ---------------------------------------------------------------------------
def render_profile(username):
    st.header("👤 Profile")
    profile = auth.get_user_profile(username)
    st.markdown(f"### {avatar_for(username)} {profile.get('full_name', username)}")
    st.write(f"**Username:** {username}")
    st.write(f"**Gender:** {profile.get('gender', 'N/A').capitalize()}")

    counts = task_store.task_counts(username)
    st.write(f"**Tasks completed:** {counts['completed']}")
    st.write(f"**Current streak:** {rewards.compute_streak(username)} days")

    st.markdown("---")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()


# ---------------------------------------------------------------------------
# Main app flow
# ---------------------------------------------------------------------------
def main():
    palette = apply_theme()

    if not st.session_state.logged_in:
        render_auth_screen(palette)
        return

    username = st.session_state.username
    profile = auth.get_user_profile(username)

    # Welcome popup shown once right after login
    if st.session_state.show_welcome:
        st.toast(f"Welcome back!!!, {profile.get('full_name', username)}! 👋", icon="🎉")
        st.balloons()
        st.session_state.show_welcome = False

    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"## ✅ Task AI")
        st.markdown(f"**{avatar_for(username)} {profile.get('full_name', username)}**")
        st.markdown("---")

        st.session_state.page = st.radio(
            "Navigate",
            ["Overview", "Add Task",  "Rewards", "All Tasks", "Profile"],
            index=["Overview", "Add Task", "Rewards", "All Tasks", "Profile"].index(
                st.session_state.page
            ),
        )

    # Route to selected page
    page = st.session_state.page
    if page == "Overview":
        render_overview(username, palette)
    elif page == "Add Task":
        render_add_task(username)
    elif page == "All Tasks":
        render_all_tasks(username)
    elif page == "Rewards":
        render_rewards(username)
    elif page == "Profile":
        render_profile(username)


if __name__ == "__main__":
    main()