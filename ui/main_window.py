from PyQt6.QtCore import QPoint, QRect, QSize, Qt, pyqtSlot
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QSystemTrayIcon, QMenu, QVBoxLayout, QWidget,
)

from core.models import AppSettings
from core.task_manager import TaskManager
from ui.task_item import TaskItemWidget


def _toast(title: str, message: str, tray_fallback=None) -> None:
    """Show a native Windows toast notification, fall back to tray balloon."""
    try:
        from winotify import Notification
        n = Notification(
            app_id="To-Do List",
            title=title,
            msg=message,
            duration="short",
        )
        n.show()
        return
    except Exception:
        pass
    # fallback: tray balloon
    if tray_fallback is not None:
        try:
            from PyQt6.QtWidgets import QSystemTrayIcon
            tray_fallback.showMessage(title, message,
                                      QSystemTrayIcon.MessageIcon.Information, 5000)
        except Exception:
            pass


_RESIZE = 7          # px margin for resize grab zones
_MIN_W, _MIN_H = 240, 300


def _make_tray_icon() -> QIcon:
    px = QPixmap(32, 32)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#89b4fa"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(3, 3, 26, 26, 5, 5)
    p.setPen(QColor("#ffffff"))
    f = p.font()
    f.setPixelSize(18)
    f.setBold(True)
    p.setFont(f)
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "✓")
    p.end()
    return QIcon(px)


class MainWindow(QWidget):
    def __init__(self, tasks: list, settings: AppSettings, history: list = None):
        super().__init__()
        self.task_manager = TaskManager(tasks, settings, history)
        self.settings = settings

        self._drag_origin: QPoint | None = None
        self._resize_dir: str | None = None
        self._win_origin: QRect | None = None

        self._setup_window()
        self._setup_tray()
        self._build_ui()
        self._apply_theme()
        self._rebuild_list()

    # ── window setup ─────────────────────────────────────────────────────────

    def _setup_window(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        s = self.settings
        self.setGeometry(s.window_x, s.window_y, s.window_width, s.window_height)
        self.setMinimumSize(_MIN_W, _MIN_H)
        self.setMouseTracking(True)

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(_make_tray_icon())
        self.tray.setToolTip("To-Do List")

        menu = QMenu()
        toggle_act = menu.addAction("Show / Hide")
        toggle_act.triggered.connect(self._toggle_visible)
        menu.addSeparator()
        quit_act = menu.addAction("Quit")
        quit_act.triggered.connect(QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_click)
        self.tray.show()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.frame = QWidget(self)
        self.frame.setObjectName("mainFrame")
        self.frame.setMouseTracking(True)

        inner = QVBoxLayout(self.frame)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)

        inner.addWidget(self._build_title_bar())
        inner.addWidget(self._build_task_list(), 1)
        inner.addWidget(self._build_bottom_bar())

        outer.addWidget(self.frame)

    def _build_title_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("titleBar")
        bar.setFixedHeight(38)
        bar.setMouseTracking(True)
        bar.mousePressEvent = self._title_press
        bar.mouseMoveEvent = self._title_move
        bar.mouseReleaseEvent = self._title_release

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 6, 0)
        layout.setSpacing(4)

        lbl = QLabel("To-Do List")
        lbl.setObjectName("titleLabel")

        self.theme_btn = QPushButton("☀" if self.settings.theme == "dark" else "🌙")
        self.theme_btn.setObjectName("iconBtn")
        self.theme_btn.setFixedSize(28, 28)
        self.theme_btn.setToolTip("Toggle theme")
        self.theme_btn.clicked.connect(self._toggle_theme)

        hist_btn = QPushButton("📋")
        hist_btn.setObjectName("iconBtn")
        hist_btn.setFixedSize(28, 28)
        hist_btn.setToolTip("Task history")
        hist_btn.clicked.connect(self._open_history)

        cfg_btn = QPushButton("⚙")
        cfg_btn.setObjectName("iconBtn")
        cfg_btn.setFixedSize(28, 28)
        cfg_btn.setToolTip("Settings")
        cfg_btn.clicked.connect(self._open_settings)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Minimise to tray")
        close_btn.clicked.connect(self._hide_to_tray)

        layout.addWidget(lbl)
        layout.addStretch()
        layout.addWidget(self.theme_btn)
        layout.addWidget(hist_btn)
        layout.addWidget(cfg_btn)
        layout.addWidget(close_btn)
        return bar

    def _build_task_list(self) -> QWidget:
        self.task_list = QListWidget()
        self.task_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.task_list.setSpacing(2)
        self.task_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.task_list.model().rowsMoved.connect(self._on_rows_moved)
        return self.task_list

    def _build_bottom_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("bottomBar")
        bar.setFixedHeight(48)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)

        add_btn = QPushButton("＋  Add Task")
        add_btn.setObjectName("addBtn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_task)

        layout.addWidget(add_btn)
        layout.addStretch()
        return bar

    # ── task list management ──────────────────────────────────────────────────

    def _rebuild_list(self):
        self.task_list.clear()
        for task in self.task_manager.tasks:
            self._append_item(task)

    def _append_item(self, task):
        item = QListWidgetItem(self.task_list)
        item.setData(Qt.ItemDataRole.UserRole, task.id)
        item.setFlags(
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsDragEnabled
        )
        widget = TaskItemWidget(task)
        widget.toggled.connect(self._on_toggle)
        widget.edit_requested.connect(self._on_edit)
        widget.delete_requested.connect(self._on_delete)
        widget.late_submit_requested.connect(self._on_late_submit)
        item.setSizeHint(QSize(0, 46))
        self.task_list.setItemWidget(item, widget)

    def _reattach_widgets(self):
        """Re-attach TaskItemWidget to every item (needed after drag-drop)."""
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            task_id = item.data(Qt.ItemDataRole.UserRole)
            task = self.task_manager.get(task_id)
            if not task:
                continue
            widget = TaskItemWidget(task)
            widget.toggled.connect(self._on_toggle)
            widget.edit_requested.connect(self._on_edit)
            widget.delete_requested.connect(self._on_delete)
            widget.late_submit_requested.connect(self._on_late_submit)
            item.setSizeHint(QSize(0, 46))
            self.task_list.setItemWidget(item, widget)

    # ── slots ─────────────────────────────────────────────────────────────────

    @pyqtSlot()
    def _add_task(self):
        from ui.task_dialog import TaskDialog
        dlg = TaskDialog(tz_offset=self.settings.timezone_offset, parent=self)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec():
            task = dlg.result_task
            self.task_manager.add(task)
            self._append_item(task)

    @pyqtSlot(str)
    def _on_edit(self, task_id: str):
        from ui.task_dialog import TaskDialog
        task = self.task_manager.get(task_id)
        if not task:
            return
        dlg = TaskDialog(task=task, tz_offset=self.settings.timezone_offset, parent=self)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec():
            self.task_manager.update(dlg.result_task)
            # refresh the widget for this item
            for i in range(self.task_list.count()):
                item = self.task_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == task_id:
                    w = self.task_list.itemWidget(item)
                    if isinstance(w, TaskItemWidget):
                        w.refresh(dlg.result_task)
                    break

    @pyqtSlot(str)
    def _on_delete(self, task_id: str):
        self.task_manager.delete(task_id)
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == task_id:
                self.task_list.takeItem(i)
                break

    @pyqtSlot(str, bool)
    def _on_toggle(self, task_id: str, completed: bool):
        self.task_manager.toggle(task_id)

    def _on_rows_moved(self, *_):
        new_order = [
            self.task_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.task_list.count())
        ]
        self.task_manager.reorder(new_order)
        self._reattach_widgets()

    @pyqtSlot(str)
    def _on_late_submit(self, task_id: str):
        self.task_manager.submit_late(task_id)
        task = self.task_manager.get(task_id)
        if not task:
            return
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == task_id:
                w = self.task_list.itemWidget(item)
                if isinstance(w, TaskItemWidget):
                    w.refresh(task)
                break

    def _open_history(self):
        from ui.history_dialog import HistoryDialog
        dlg = HistoryDialog(self.task_manager.history, parent=self)
        dlg.setStyleSheet(self.styleSheet())
        dlg.late_submitted.connect(self._on_late_submit)
        dlg.exec()

    # ── scheduler callbacks ───────────────────────────────────────────────────

    @pyqtSlot(str)
    def on_reset(self, task_id: str):
        """Called by Scheduler when a task resets — refresh its widget."""
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == task_id:
                task = self.task_manager.get(task_id)
                w = self.task_list.itemWidget(item)
                if task and isinstance(w, TaskItemWidget):
                    w.refresh(task)
                break

    @pyqtSlot(str, str)
    def show_notification(self, task_id: str, message: str):
        _toast("To-Do List", message, self.tray)

    # ── theme ─────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        from ui.theme import get_stylesheet
        self.setStyleSheet(get_stylesheet(self.settings.theme))

    def _toggle_theme(self):
        self.settings.theme = "light" if self.settings.theme == "dark" else "dark"
        self.theme_btn.setText("☀" if self.settings.theme == "dark" else "🌙")
        self._apply_theme()
        from core.storage import save_data
        save_data(self.task_manager.tasks, self.settings)

    # ── settings ──────────────────────────────────────────────────────────────

    def _open_settings(self):
        from ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self.settings, parent=self)
        dlg.setStyleSheet(self.styleSheet())
        if dlg.exec():
            self.settings = dlg.settings
            self._apply_theme()
            self.theme_btn.setText("☀" if self.settings.theme == "dark" else "🌙")
            from core.storage import save_data
            save_data(self.task_manager.tasks, self.settings)

    # ── tray / visibility ─────────────────────────────────────────────────────

    def _toggle_visible(self):
        if self.isVisible():
            self._hide_to_tray()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _hide_to_tray(self):
        self._save_geometry()
        self.hide()

    def _on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_visible()

    def closeEvent(self, event):
        event.ignore()
        self._hide_to_tray()

    def _save_geometry(self):
        geo = self.geometry()
        self.settings.window_x = geo.x()
        self.settings.window_y = geo.y()
        self.settings.window_width = geo.width()
        self.settings.window_height = geo.height()
        from core.storage import save_data
        save_data(self.task_manager.tasks, self.settings)

    # ── title-bar drag ────────────────────────────────────────────────────────

    def _title_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint()
            self._win_origin = self.geometry()

    def _title_move(self, event):
        if self._drag_origin and self._win_origin:
            delta = event.globalPosition().toPoint() - self._drag_origin
            self.move(self._win_origin.topLeft() + delta)

    def _title_release(self, event):
        self._drag_origin = None
        self._win_origin = None
        self._save_geometry()

    # ── edge resize ───────────────────────────────────────────────────────────

    def _resize_dir_at(self, pos: QPoint) -> str | None:
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        m = _RESIZE
        top = y < m
        bot = y > h - m
        lft = x < m
        rgt = x > w - m
        if top and lft:
            return "nw"
        if top and rgt:
            return "ne"
        if bot and lft:
            return "sw"
        if bot and rgt:
            return "se"
        if top:
            return "n"
        if bot:
            return "s"
        if lft:
            return "w"
        if rgt:
            return "e"
        return None

    _CURSORS = {
        "n": Qt.CursorShape.SizeVerCursor,
        "s": Qt.CursorShape.SizeVerCursor,
        "e": Qt.CursorShape.SizeHorCursor,
        "w": Qt.CursorShape.SizeHorCursor,
        "nw": Qt.CursorShape.SizeFDiagCursor,
        "se": Qt.CursorShape.SizeFDiagCursor,
        "ne": Qt.CursorShape.SizeBDiagCursor,
        "sw": Qt.CursorShape.SizeBDiagCursor,
    }

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            d = self._resize_dir_at(event.pos())
            if d:
                self._resize_dir = d
                self._drag_origin = event.globalPosition().toPoint()
                self._win_origin = self.geometry()

    def mouseMoveEvent(self, event):
        if self._resize_dir and self._drag_origin and self._win_origin:
            self._do_resize(event.globalPosition().toPoint())
        else:
            d = self._resize_dir_at(event.pos())
            self.setCursor(self._CURSORS.get(d, Qt.CursorShape.ArrowCursor))

    def mouseReleaseEvent(self, event):
        if self._resize_dir:
            self._resize_dir = None
            self._drag_origin = None
            self._win_origin = None
            self._save_geometry()
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _do_resize(self, gpos: QPoint):
        delta = gpos - self._drag_origin
        geo = self._win_origin
        d = self._resize_dir

        x, y = geo.x(), geo.y()
        w, h = geo.width(), geo.height()

        if "e" in d:
            w = max(_MIN_W, w + delta.x())
        if "s" in d:
            h = max(_MIN_H, h + delta.y())
        if "w" in d:
            new_w = max(_MIN_W, w - delta.x())
            x = geo.right() - new_w + 1 if new_w == _MIN_W else geo.x() + delta.x()
            w = new_w
        if "n" in d:
            new_h = max(_MIN_H, h - delta.y())
            y = geo.bottom() - new_h + 1 if new_h == _MIN_H else geo.y() + delta.y()
            h = new_h

        self.setGeometry(x, y, w, h)
