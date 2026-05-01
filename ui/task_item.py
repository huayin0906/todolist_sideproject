from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QCheckBox, QWidget

from core.models import Task

_SCHED_LABELS = {
    "none":     "",
    "daily":    "daily",
    "interval": "interval",
    "weekly":   "weekly",
    "fixed":    "fixed",
}


class TaskItemWidget(QWidget):
    toggled = pyqtSignal(str, bool)       # task_id, completed
    edit_requested = pyqtSignal(str)      # task_id
    delete_requested = pyqtSignal(str)    # task_id

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setObjectName("taskItem")
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        # checkbox
        self.check = QCheckBox()
        self.check.setChecked(self.task.completed)
        self.check.toggled.connect(self._on_toggle)

        # title
        self.label = QLabel(self.task.title)
        self.label.setWordWrap(False)
        self.label.setObjectName("taskLabelDone" if self.task.completed else "taskLabel")

        # schedule badge
        badge_text = _SCHED_LABELS.get(self.task.schedule.type, "")
        self.badge = QLabel(badge_text)
        self.badge.setObjectName("schedBadge")
        self.badge.setVisible(bool(badge_text))

        # edit / delete
        self.edit_btn = QPushButton("✎")
        self.edit_btn.setObjectName("editBtn")
        self.edit_btn.setFixedSize(24, 24)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.task.id))

        self.del_btn = QPushButton("✕")
        self.del_btn.setObjectName("deleteBtn")
        self.del_btn.setFixedSize(24, 24)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.clicked.connect(lambda: self.delete_requested.emit(self.task.id))

        layout.addWidget(self.check)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.badge)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.del_btn)

    def _on_toggle(self, checked: bool):
        self.task.completed = checked
        self.label.setObjectName("taskLabelDone" if checked else "taskLabel")
        # force style refresh
        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)
        self.toggled.emit(self.task.id, checked)

    def refresh(self, task: Task):
        self.task = task
        self.check.blockSignals(True)
        self.check.setChecked(task.completed)
        self.check.blockSignals(False)
        self.label.setText(task.title)
        self.label.setObjectName("taskLabelDone" if task.completed else "taskLabel")
        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)
        badge_text = _SCHED_LABELS.get(task.schedule.type, "")
        self.badge.setText(badge_text)
        self.badge.setVisible(bool(badge_text))

    def sizeHint(self) -> QSize:
        return QSize(0, 44)
