import json
from pathlib import Path

from core.models import AppSettings, NotificationConfig, ScheduleConfig, Task

DATA_DIR = Path.home() / ".todolist"
DATA_FILE = DATA_DIR / "data.json"


def _ensure_dir():
    DATA_DIR.mkdir(exist_ok=True)


# ── serialisation ────────────────────────────────────────────────────────────

def _task_to_dict(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "completed": task.completed,
        "order": task.order,
        "schedule": {
            "type": task.schedule.type,
            "reset_time": task.schedule.reset_time,
            "interval_days": task.schedule.interval_days,
            "weekday": task.schedule.weekday,
            "deadline": task.schedule.deadline,
        },
        "notification": {
            "enabled": task.notification.enabled,
            "minutes_before": task.notification.minutes_before,
            "custom_message": task.notification.custom_message,
        },
        "last_reset": task.last_reset,
    }


def _dict_to_task(d: dict) -> Task:
    s = d.get("schedule", {})
    n = d.get("notification", {})
    return Task(
        id=d.get("id", ""),
        title=d.get("title", ""),
        completed=d.get("completed", False),
        order=d.get("order", 0),
        schedule=ScheduleConfig(
            type=s.get("type", "none"),
            reset_time=s.get("reset_time", "00:00"),
            interval_days=s.get("interval_days", 1),
            weekday=s.get("weekday", 0),
            deadline=s.get("deadline", ""),
        ),
        notification=NotificationConfig(
            enabled=n.get("enabled", True),
            minutes_before=n.get("minutes_before", 60),
            custom_message=n.get("custom_message", ""),
        ),
        last_reset=d.get("last_reset", ""),
    )


# ── public API ───────────────────────────────────────────────────────────────

def save_data(tasks: list, settings: AppSettings) -> None:
    _ensure_dir()
    payload = {
        "settings": {
            "theme": settings.theme,
            "timezone_offset": settings.timezone_offset,
            "window_x": settings.window_x,
            "window_y": settings.window_y,
            "window_width": settings.window_width,
            "window_height": settings.window_height,
        },
        "tasks": [_task_to_dict(t) for t in tasks],
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def load_data() -> tuple:
    if not DATA_FILE.exists():
        return [], AppSettings()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return [], AppSettings()

    raw_s = data.get("settings", {})
    settings = AppSettings(
        theme=raw_s.get("theme", "dark"),
        timezone_offset=raw_s.get("timezone_offset", 8),
        window_x=raw_s.get("window_x", 100),
        window_y=raw_s.get("window_y", 100),
        window_width=raw_s.get("window_width", 320),
        window_height=raw_s.get("window_height", 500),
    )
    tasks = sorted(
        [_dict_to_task(t) for t in data.get("tasks", [])],
        key=lambda t: t.order,
    )
    return tasks, settings
