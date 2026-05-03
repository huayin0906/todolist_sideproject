from datetime import datetime, timezone

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QSizePolicy,
)

from core.models import HistoryRecord


def _fmt_dt(iso: str) -> str:
    """Format an ISO datetime string to a readable local string."""
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%Y-%m-%d  %H:%M")
    except Exception:
        return iso


def _in_window(record: HistoryRecord) -> bool:
    if not record.late_until:
        return False
    try:
        late_dt = datetime.fromisoformat(record.late_until)
        now = datetime.now(timezone.utc)
        if late_dt.tzinfo is None:
            late_dt = late_dt.replace(tzinfo=timezone.utc)
        return now < late_dt
    except Exception:
        return False


class _RecordRow(QFrame):
    late_submitted = pyqtSignal(str)   # task_id

    def __init__(self, record: HistoryRecord, parent=None):
        super().__init__(parent)
        self.record = record
        self.setObjectName("historyRow")
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)

        # Task title
        title = QLabel(self.record.task_title)
        title.setObjectName("histTitle")
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Reset time
        when = QLabel(_fmt_dt(self.record.reset_at))
        when.setObjectName("histTime")
        when.setFixedWidth(130)

        # Status badge
        if self.record.late_submitted:
            status = QLabel("✓  submitted late")
            status.setObjectName("histStatusLate")
        elif _in_window(self.record):
            status = QPushButton("✗  Submit late")
            status.setObjectName("histStatusMissed")
            status.setCursor(Qt.CursorShape.PointingHandCursor)
            status.clicked.connect(self._on_submit_late)
        else:
            status = QLabel("✗  missed")
            status.setObjectName("histStatusExpired")

        layout.addWidget(title)
        layout.addWidget(when)
        layout.addWidget(status)

    def _on_submit_late(self):
        self.record.late_submitted = True
        self.late_submitted.emit(self.record.task_id)
        # Rebuild the row to show updated state
        old_layout = self.layout()
        while old_layout.count():
            item = old_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._build()


class HistoryDialog(QDialog):
    late_submitted = pyqtSignal(str)   # task_id — relay to main window

    def __init__(self, history: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task History  (last 30 missed)")
        self.setMinimumSize(540, 400)
        self._history = history
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header.setObjectName("histHeader")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 8, 10, 8)
        h_layout.setSpacing(10)
        h_layout.addWidget(QLabel("Task"), 1)
        lbl_when = QLabel("Reset at")
        lbl_when.setFixedWidth(130)
        h_layout.addWidget(lbl_when)
        h_layout.addWidget(QLabel("Status"))
        root.addWidget(header)

        # Scroll area with rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(2)
        container_layout.setContentsMargins(4, 4, 4, 4)

        if not self._history:
            empty = QLabel("No missed tasks recorded yet.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setObjectName("histEmpty")
            container_layout.addWidget(empty)
        else:
            for record in self._history:
                row = _RecordRow(record)
                row.late_submitted.connect(self.late_submitted)
                container_layout.addWidget(row)

        container_layout.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        # Close button
        close_bar = QWidget()
        close_bar.setObjectName("histFooter")
        close_layout = QHBoxLayout(close_bar)
        close_layout.setContentsMargins(10, 8, 10, 8)
        close_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setObjectName("histCloseBtn")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        root.addWidget(close_bar)
