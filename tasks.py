"""
tasks.py — task storage and management for Task AI
Backed by MongoDB (tasks collection).
"""

from datetime import datetime, date

from bson.objectid import ObjectId
import plotly.graph_objects as go

from db import get_db

# Lower number = higher priority (used for sorting)
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

# Keywords used to auto-detect priority from what the user typed
PRIORITY_KEYWORDS = {
    "High": [
        "urgent", "asap", "important", "critical", "exam", "deadline",
        "interview", "submission", "emergency", "due today", "final",
        "presentation", "meeting", "immediately",
    ],
    "Low": [
        "someday", "optional", "later", "whenever", "low priority",
        "maybe", "eventually", "casual", "no rush",
    ],
}


def _tasks():
    return get_db()["tasks"]


def predict_priority(title: str, description: str = "", due_date: str = "") -> str:
    """
    Auto-predict a task's priority from its content and due date.
    1. Keyword match in title/description wins first.
    2. Otherwise, priority is inferred from how soon the due date is.
    3. If neither gives a signal, defaults to "Medium".
    """
    text = f"{title} {description}".lower()

    for word in PRIORITY_KEYWORDS["High"]:
        if word in text:
            return "High"
    for word in PRIORITY_KEYWORDS["Low"]:
        if word in text:
            return "Low"

    if due_date:
        try:
            days_left = (date.fromisoformat(due_date) - date.today()).days
            if days_left <= 1:
                return "High"
            elif days_left <= 5:
                return "Medium"
            else:
                return "Low"
        except ValueError:
            pass

    return "Medium"


def add_task(
    username: str,
    title: str,
    description: str = "",
    due_date: str = "",
    priority: str | None = None,
) -> str:
    """Add a task. If priority isn't given, it's auto-predicted. Returns the priority used."""
    if priority is None:
        priority = predict_priority(title, description, due_date)

    _tasks().insert_one({
        "username": username,
        "title": title,
        "description": description,
        "due_date": due_date,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    })
    return priority


def get_user_tasks(username: str) -> list:
    """Return the user's tasks with Mongo's _id normalized to a string 'id' field."""
    docs = list(_tasks().find({"username": username}).sort("created_at", 1))
    tasks = []
    for d in docs:
        d["id"] = str(d.pop("_id"))
        tasks.append(d)
    return tasks


def toggle_complete(task_id: str) -> None:
    col = _tasks()
    task = col.find_one({"_id": ObjectId(task_id)})
    if not task:
        return
    new_status = not task["completed"]
    col.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {
            "completed": new_status,
            "completed_at": datetime.now().isoformat() if new_status else None,
        }},
    )


def delete_task(task_id: str) -> None:
    _tasks().delete_one({"_id": ObjectId(task_id)})


def task_counts(username: str) -> dict:
    user_tasks = get_user_tasks(username)
    completed = sum(1 for t in user_tasks if t["completed"])
    pending = len(user_tasks) - completed
    return {"total": len(user_tasks), "completed": completed, "pending": pending}


def make_pie_chart(username: str, accent: str, bg: str, text_color: str):
    """Return a Plotly pie chart figure of completed vs pending tasks."""
    counts = task_counts(username)
    labels = ["Completed", "Pending"]
    values = [counts["completed"], counts["pending"]]

    if sum(values) == 0:
        values = [1]
        labels = ["No tasks yet"]

    fig = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=[accent, "#94A3B8"]),
            textinfo="label+percent",
        )]
    )
    fig.update_layout(
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        font=dict(color=text_color, family="Times New Roman"),
        showlegend=True,
        margin=dict(t=10, b=10, l=10, r=10),
        height=350,
    )
    return fig


def suggest_next_task(username: str) -> dict | None:
    """
    Suggest the single most important pending task to do next.
    Ranking: High > Medium > Low priority, then earliest due date,
    then oldest task first. Returns None if nothing is pending.
    """
    pending = [t for t in get_user_tasks(username) if not t["completed"]]
    if not pending:
        return None

    def sort_key(t):
        rank = PRIORITY_ORDER.get(t.get("priority", "Medium"), 1)
        due = t.get("due_date") or "9999-12-31"
        created = t.get("created_at", "")
        return (rank, due, created)

    pending.sort(key=sort_key)
    return pending[0]


def completion_dates(username: str) -> list:
    """List of date() objects on which the user completed at least one task."""
    user_tasks = get_user_tasks(username)
    dates = set()
    for t in user_tasks:
        if t["completed"] and t["completed_at"]:
            d = datetime.fromisoformat(t["completed_at"]).date()
            dates.add(d)
    return sorted(dates)