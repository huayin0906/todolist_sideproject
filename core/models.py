from dataclasses import dataclass, field
import uuid


@dataclass
class ScheduleConfig:
    type: str = "none"          # none | daily | interval | weekly | fixed
    reset_time: str = "00:00"   # HH:MM — used by daily / interval / weekly
    interval_days: int = 1      # used by interval
    weekday: int = 0            # 0=Mon … 6=Sun, used by weekly
    deadline: str = ""          # ISO-8601 datetime string, used by fixed


@dataclass
class NotificationConfig:
    enabled: bool = True
    minutes_before: int = 60
    custom_message: str = ""    # empty → use built-in default


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    completed: bool = False
    order: int = 0
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    last_reset: str = ""        # ISO-8601 datetime of last auto-reset


@dataclass
class AppSettings:
    theme: str = "dark"
    timezone_offset: int = 8    # UTC offset in hours
    window_x: int = 100
    window_y: int = 100
    window_width: int = 320
    window_height: int = 500
