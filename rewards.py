"""
rewards.py — streaks and badges for Task AI
"""

from datetime import date, timedelta
from tasks import get_user_tasks, completion_dates


def compute_streak(username: str) -> int:
    """
    Current consecutive-day streak of completing at least one task per day,
    counting backwards from today (or yesterday, if nothing done today yet).
    """
    dates = set(completion_dates(username))
    if not dates:
        return 0

    today = date.today()
    streak = 0
    cursor = today

    # If nothing completed today, the streak can still be "alive" through yesterday.
    if cursor not in dates:
        cursor -= timedelta(days=1)

    while cursor in dates:
        streak += 1
        cursor -= timedelta(days=1)

    return streak


# Badge definitions: id, label, emoji, description, and a condition function
BADGES = [
    {
        "id": "first_task",
        "label": "First Step",
        "emoji": "🥇",
        "desc": "Complete your first task.",
        "condition": lambda tasks, streak: sum(1 for t in tasks if t["completed"]) >= 1,
    },
    {
        "id": "ten_tasks",
        "label": "Getting Things Done",
        "emoji": "🎯",
        "desc": "Complete 10 tasks.",
        "condition": lambda tasks, streak: sum(1 for t in tasks if t["completed"]) >= 10,
    },
    {
        "id": "fifty_tasks",
        "label": "Task Machine",
        "emoji": "🏆",
        "desc": "Complete 50 tasks.",
        "condition": lambda tasks, streak: sum(1 for t in tasks if t["completed"]) >= 50,
    },
    {
        "id": "streak_3",
        "label": "On a Roll",
        "emoji": "🔥",
        "desc": "Reach a 3-day streak.",
        "condition": lambda tasks, streak: streak >= 3,
    },
    {
        "id": "streak_7",
        "label": "Week Warrior",
        "emoji": "⚡",
        "desc": "Reach a 7-day streak.",
        "condition": lambda tasks, streak: streak >= 7,
    },
    {
        "id": "streak_30",
        "label": "Unstoppable",
        "emoji": "🚀",
        "desc": "Reach a 30-day streak.",
        "condition": lambda tasks, streak: streak >= 30,
    },
]


def get_badges_status(username: str) -> list:
    """Return list of badges with an 'earned' bool attached."""
    tasks = get_user_tasks(username)
    streak = compute_streak(username)
    result = []
    for badge in BADGES:
        earned = badge["condition"](tasks, streak)
        result.append({**badge, "earned": earned})
    return result
