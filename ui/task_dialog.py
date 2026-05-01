from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDateTimeEdit, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QStackedWidget, QTextEdit, QTimeEdit, QVBoxLayout, QWidget,
)

from core.models import NotificationConfig, ScheduleConfig, Task

_SCHED_TYPES = ["None", "Daily", "Every N days", "Weekly", "Fixed deadline"]
_SCHED_KEYS  = ["none", "daily", "interval", "weekly", "fixed"]
_WEEKDAYS    = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _key_to_index(key: str) -> int:
    try:
        return _SCHED_KEYS.index(key)
    except ValueError:
        return 0


class TaskDialog(QDialog):
    def __init__(self, task: Task | None = None, tz_offset: int = 8, parent=None):
        super().__init__(parent)
        self._tz = tz_offset
        self._editing = task
        self.setWindowTitle("Edit Task" if task else "Add Task")
        self.setMinimumWidth(380)
        self._build()
        if task:
            self._populate(task)

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)

        # title
        form = QFormLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("What do you need to do?")
        form.addRow("Task:", self.title_edit)
        root.addLayout(form)

        # schedule group
        sched_box = QGroupBox("Schedule & Reset")
        sched_layout = QVBoxLayout(sched_box)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.sched_combo = QComboBox()
        self.sched_combo.addItems(_SCHED_TYPES)
        self.sched_combo.currentIndexChanged.connect(self._on_sched_type)
        type_row.addWidget(self.sched_combo, 1)
        sched_layout.addLayout(type_row)

        # stacked pages per schedule type
        self.stack = QStackedWidget()
        self.stack.addWidget(QWidget())                # 0 none
        self.stack.addWidget(self._page_daily())       # 1 daily
        self.stack.addWidget(self._page_interval())    # 2 interval
        self.stack.addWidget(self._page_weekly())      # 3 weekly
        self.stack.addWidget(self._page_fixed())       # 4 fixed
        sched_layout.addWidget(self.stack)
        root.addWidget(sched_box)

        # notification group
        notif_box = QGroupBox("Notification")
        notif_layout = QVBoxLayout(notif_box)

        self.notif_check = QCheckBox("Enable notification")
        self.notif_check.setObjectName("notifCheck")
        self.notif_check.setChecked(True)
        self.notif_check.toggled.connect(self._on_notif_toggle)
        notif_layout.addWidget(self.notif_check)

        notif_form = QFormLayout()
        self.notif_spin = QSpinBox()
        self.notif_spin.setRange(1, 1440)
        self.notif_spin.setValue(60)
        self.notif_spin.setSuffix(" min before")
        notif_form.addRow("Remind:", self.notif_spin)

        self.notif_msg = QTextEdit()
        self.notif_msg.setPlaceholderText(
            'Leave empty for default, or write a custom message.\n'
            'e.g. "Ding dong! Time to take your medicine!"'
        )
        self.notif_msg.setFixedHeight(64)
        notif_form.addRow("Message:", self.notif_msg)
        notif_layout.addLayout(notif_form)

        self._notif_form_widget = notif_form  # keep ref
        root.addWidget(notif_box)

        # buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    # ── schedule pages ────────────────────────────────────────────────────────

    def _time_edit(self, default="00:00") -> QTimeEdit:
        w = QTimeEdit()
        h, m = (int(x) for x in default.split(":"))
        w.setTime(w.time().fromString(f"{h:02d}:{m:02d}", "HH:mm"))
        w.setDisplayFormat("HH:mm")
        return w

    def _page_daily(self) -> QWidget:
        page = QWidget()
        f = QFormLayout(page)
        self.daily_time = self._time_edit("00:00")
        f.addRow("Reset time:", self.daily_time)
        return page

    def _page_interval(self) -> QWidget:
        page = QWidget()
        f = QFormLayout(page)
        self.interval_days = QSpinBox()
        self.interval_days.setRange(1, 365)
        self.interval_days.setValue(1)
        self.interval_days.setSuffix(" day(s)")
        f.addRow("Every:", self.interval_days)
        self.interval_time = self._time_edit("00:00")
        f.addRow("At time:", self.interval_time)
        return page

    def _page_weekly(self) -> QWidget:
        page = QWidget()
        f = QFormLayout(page)
        self.weekly_day = QComboBox()
        self.weekly_day.addItems(_WEEKDAYS)
        f.addRow("Day:", self.weekly_day)
        self.weekly_time = self._time_edit("00:00")
        f.addRow("At time:", self.weekly_time)
        return page

    def _page_fixed(self) -> QWidget:
        page = QWidget()
        f = QFormLayout(page)
        self.fixed_dt = QDateTimeEdit()
        self.fixed_dt.setDisplayFormat("yyyy-MM-dd  HH:mm")
        self.fixed_dt.setCalendarPopup(True)
        # default: 24 h from now
        from datetime import datetime, timedelta, timezone
        tz_dt = datetime.now(timezone(timedelta(hours=self._tz))) + timedelta(hours=24)
        self.fixed_dt.setDateTime(
            QDateTime.fromString(
                tz_dt.strftime("%Y-%m-%d %H:%M"), "yyyy-MM-dd HH:mm"
            )
        )
        f.addRow("Deadline:", self.fixed_dt)
        return page

    # ── slots ─────────────────────────────────────────────────────────────────

    def _on_sched_type(self, index: int):
        self.stack.setCurrentIndex(index)

    def _on_notif_toggle(self, checked: bool):
        self.notif_spin.setEnabled(checked)
        self.notif_msg.setEnabled(checked)

    # ── populate (edit mode) ─────────────────────────────────────────────────

    def _populate(self, task: Task):
        self.title_edit.setText(task.title)

        idx = _key_to_index(task.schedule.type)
        self.sched_combo.setCurrentIndex(idx)
        self.stack.setCurrentIndex(idx)

        s = task.schedule
        if s.type == "daily":
            self._set_time(self.daily_time, s.reset_time)
        elif s.type == "interval":
            self.interval_days.setValue(s.interval_days)
            self._set_time(self.interval_time, s.reset_time)
        elif s.type == "weekly":
            self.weekly_day.setCurrentIndex(s.weekday)
            self._set_time(self.weekly_time, s.reset_time)
        elif s.type == "fixed" and s.deadline:
            try:
                dt = datetime.fromisoformat(s.deadline)
                self.fixed_dt.setDateTime(
                    QDateTime.fromString(dt.strftime("%Y-%m-%d %H:%M"), "yyyy-MM-dd HH:mm")
                )
            except ValueError:
                pass

        n = task.notification
        self.notif_check.setChecked(n.enabled)
        self.notif_spin.setValue(n.minutes_before)
        self.notif_msg.setPlainText(n.custom_message)
        self._on_notif_toggle(n.enabled)

    def _set_time(self, widget: QTimeEdit, hhmm: str):
        from PyQt6.QtCore import QTime
        try:
            h, m = hhmm.split(":")
            widget.setTime(QTime(int(h), int(m)))
        except Exception:
            pass

    # ── accept ────────────────────────────────────────────────────────────────

    def _accept(self):
        title = self.title_edit.text().strip()
        if not title:
            self.title_edit.setFocus()
            return

        idx = self.sched_combo.currentIndex()
        stype = _SCHED_KEYS[idx]

        sched = ScheduleConfig(type=stype)
        if stype == "daily":
            sched.reset_time = self.daily_time.time().toString("HH:mm")
        elif stype == "interval":
            sched.interval_days = self.interval_days.value()
            sched.reset_time = self.interval_time.time().toString("HH:mm")
        elif stype == "weekly":
            sched.weekday = self.weekly_day.currentIndex()
            sched.reset_time = self.weekly_time.time().toString("HH:mm")
        elif stype == "fixed":
            dt_str = self.fixed_dt.dateTime().toString("yyyy-MM-dd HH:mm")
            try:
                sched.deadline = datetime.strptime(dt_str, "%Y-%m-%d %H:%M").isoformat()
            except ValueError:
                sched.deadline = ""

        notif = NotificationConfig(
            enabled=self.notif_check.isChecked(),
            minutes_before=self.notif_spin.value(),
            custom_message=self.notif_msg.toPlainText().strip(),
        )

        if self._editing:
            self._editing.title = title
            self._editing.schedule = sched
            self._editing.notification = notif
            self.result_task = self._editing
        else:
            self.result_task = Task(title=title, schedule=sched, notification=notif)

        self.accept()
