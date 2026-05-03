from datetime import datetime, timedelta, timezone

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


def _tz(offset_hours: int) -> timezone:
    return timezone(timedelta(hours=offset_hours))


def _now(offset_hours: int) -> datetime:
    return datetime.now(_tz(offset_hours))


def _parse_hhmm(s: str) -> tuple:
    """Return (hour, minute) from 'HH:MM' string."""
    try:
        h, m = s.split(":")
        return int(h), int(m)
    except Exception:
        return 0, 0


def _next_reset_dt(task, offset_hours: int) -> datetime | None:
    """
    Return the upcoming reset datetime for a task (in aware UTC+offset).
    Returns None for schedule type 'none' or 'fixed'.
    """
    tz = _tz(offset_hours)
    now = datetime.now(tz)
    sched = task.schedule

    if sched.type == "daily":
        h, m = _parse_hhmm(sched.reset_time)
        candidate = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate

    if sched.type == "interval":
        h, m = _parse_hhmm(sched.reset_time)
        if task.last_reset:
            try:
                last = datetime.fromisoformat(task.last_reset)
            except ValueError:
                last = now - timedelta(days=sched.interval_days)
        else:
            last = now - timedelta(days=sched.interval_days)
        candidate = last.replace(hour=h, minute=m, second=0, microsecond=0)
        while candidate <= now:
            candidate += timedelta(days=sched.interval_days)
        return candidate

    if sched.type == "weekly":
        h, m = _parse_hhmm(sched.reset_time)
        days_ahead = (sched.weekday - now.weekday()) % 7
        candidate = (now + timedelta(days=days_ahead)).replace(
            hour=h, minute=m, second=0, microsecond=0
        )
        if candidate <= now:
            candidate += timedelta(weeks=1)
        return candidate

    return None


def _should_reset(task, now: datetime, offset_hours: int) -> bool:
    """True when a scheduled reset is overdue and hasn't been applied yet."""
    sched = task.schedule
    if sched.type in ("none", "fixed"):
        return False

    tz = _tz(offset_hours)
    h, m = _parse_hhmm(sched.reset_time)

    if sched.type == "daily":
        reset_today = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if now < reset_today:
            return False
        if task.last_reset:
            try:
                last = datetime.fromisoformat(task.last_reset).astimezone(tz)
                return last < reset_today
            except ValueError:
                pass
        return True

    if sched.type == "interval":
        if not task.last_reset:
            return False
        try:
            last = datetime.fromisoformat(task.last_reset).astimezone(tz)
        except ValueError:
            return False
        next_reset = last.replace(hour=h, minute=m, second=0, microsecond=0)
        while next_reset <= last:
            next_reset += timedelta(days=sched.interval_days)
        return now >= next_reset

    if sched.type == "weekly":
        days_since = (now.weekday() - sched.weekday) % 7
        reset_this_week = (now - timedelta(days=days_since)).replace(
            hour=h, minute=m, second=0, microsecond=0
        )
        if now < reset_this_week:
            return False
        if task.last_reset:
            try:
                last = datetime.fromisoformat(task.last_reset).astimezone(tz)
                return last < reset_this_week
            except ValueError:
                pass
        return True

    return False


class Scheduler(QObject):
    reset_triggered = pyqtSignal(str)           # task_id
    notification_triggered = pyqtSignal(str, str)  # task_id, message

    def __init__(self, task_manager, settings, parent=None):
        super().__init__(parent)
        self._tm = task_manager
        self._settings = settings
        self._notified: set = set()  # task_ids already notified this cycle

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(30_000)   # check every 30 seconds

    def force_check(self):
        self._tick()

    def _tick(self):
        offset = self._settings.timezone_offset
        now = _now(offset)

        for task in list(self._tm.tasks):
            self._check_reset(task, now, offset)
            self._check_notification(task, now, offset)

    def _check_reset(self, task, now, offset):
        if not _should_reset(task, now, offset):
            return

        # Temporarily update last_reset so _next_reset_dt computes the NEXT
        # window correctly (needed for interval type which uses last_reset).
        task.last_reset = now.isoformat()
        next_dt = _next_reset_dt(task, offset)
        late_until = next_dt.isoformat() if next_dt else ""

        self._tm.reset_and_record(task.id, now.isoformat(), late_until)
        self.reset_triggered.emit(task.id)
        self._notified.discard(task.id)

    def _check_notification(self, task, now, offset):
        if not task.notification.enabled:
            return
        if task.completed:
            return
        if task.id in self._notified:
            return

        target = self._get_target_dt(task, now, offset)
        if target is None:
            return

        minutes_left = (target - now).total_seconds() / 60
        if 0 <= minutes_left <= task.notification.minutes_before:
            msg = self._build_message(task, int(minutes_left), now)
            self.notification_triggered.emit(task.id, msg)
            self._notified.add(task.id)

    def _get_target_dt(self, task, now, offset):
        if task.schedule.type == "fixed" and task.schedule.deadline:
            try:
                dt = datetime.fromisoformat(task.schedule.deadline)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=_tz(offset))
                return dt
            except ValueError:
                return None
        return _next_reset_dt(task, offset)

    def _build_message(self, task, minutes_left: int, now: datetime) -> str:
        if task.notification.custom_message:
            return task.notification.custom_message

        # Count incomplete tasks that share this same reset schedule
        incomplete = sum(
            1 for t in self._tm.tasks
            if not t.completed and t.schedule.type == task.schedule.type
        )
        count_str = str(incomplete) if incomplete > 0 else "some"

        if task.schedule.type == "fixed":
            return (
                f"Task '{task.title}' is due in {minutes_left} minute(s)!"
            )
        return (
            f"You have {count_str} task(s) not done yet! "
            f"Resetting in {minutes_left} minute(s)."
        )
