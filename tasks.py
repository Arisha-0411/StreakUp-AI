"""
tasks.py — task storage and management for Task AI
Stores tasks in a local JSON file (data/tasks.json).
"""

import json
import os
import uuid
from datetime import datetime, date

import plotly.graph_objects as go

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")

os.makedirs(DATA_DIR, exist_ok=True)


def load_tasks() -> list:
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_tasks(tasks: list) -> None:
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(username: str, title: str, description: str = "", due_date: str = "") -> None:
    tasks = load_tasks()
    tasks.append({
        "id": str(uuid.uuid4()),
        "username": username,
        "title": title,
        "description": description,
        "due_date": due_date,
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    })
    save_tasks(tasks)


def get_user_tasks(username: str) -> list:
    return [t for t in load_tasks() if t["username"] == username]


def toggle_complete(task_id: str) -> None:
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = not t["completed"]
            t["completed_at"] = datetime.now().isoformat() if t["completed"] else None
    save_tasks(tasks)


def delete_task(task_id: str) -> None:
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)


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


def completion_dates(username: str) -> list:
    """List of date() objects on which the user completed at least one task."""
    user_tasks = get_user_tasks(username)
    dates = set()
    for t in user_tasks:
        if t["completed"] and t["completed_at"]:
            d = datetime.fromisoformat(t["completed_at"]).date()
            dates.add(d)
    return sorted(dates)
