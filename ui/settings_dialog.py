from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QComboBox,
    QSpinBox, QVBoxLayout, QGroupBox, QCheckBox, QLabel, QPushButton,
)

from core.models import AppSettings


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(300)
        self._settings = settings
        self._build()
        self._populate()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)

        # appearance
        app_box = QGroupBox("Appearance")
        app_form = QFormLayout(app_box)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        app_form.addRow("Theme:", self.theme_combo)
        root.addWidget(app_box)

        # time
        time_box = QGroupBox("Time & Timezone")
        time_form = QFormLayout(time_box)

        self.tz_spin = QSpinBox()
        self.tz_spin.setRange(-12, 14)
        self.tz_spin.setSuffix("  (UTC offset)")
        self.tz_spin.setToolTip(
            "Your UTC offset in hours.\n"
            "e.g. UTC+8 → enter 8"
        )
        time_form.addRow("Timezone:", self.tz_spin)
        root.addWidget(time_box)

        # window
        win_box = QGroupBox("Window")
        win_form = QFormLayout(win_box)
        self.taskbar_check = QCheckBox("Show in taskbar")
        self.taskbar_check.setToolTip(
            "When checked the app appears in the Windows taskbar.\n"
            "Restart required."
        )
        win_form.addRow(self.taskbar_check)
        root.addWidget(win_box)

        # notifications
        notif_box = QGroupBox("Notifications")
        notif_layout = QVBoxLayout(notif_box)
        test_btn = QPushButton("Send test notification")
        test_btn.clicked.connect(self._test_notification)
        notif_layout.addWidget(test_btn)
        root.addWidget(notif_box)

        note = QLabel("Some changes take effect after restart.")
        note.setStyleSheet("color: #888; font-size: 11px;")
        root.addWidget(note)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _populate(self):
        self.theme_combo.setCurrentIndex(0 if self._settings.theme == "dark" else 1)
        self.tz_spin.setValue(self._settings.timezone_offset)
        self.taskbar_check.setChecked(
            getattr(self._settings, "show_in_taskbar", False)
        )

    def _test_notification(self):
        from ui.main_window import _toast
        _toast("To-Do List", "This is a test notification — it's working!")

    def _accept(self):
        self._settings.theme = "dark" if self.theme_combo.currentIndex() == 0 else "light"
        self._settings.timezone_offset = self.tz_spin.value()
        self._settings.show_in_taskbar = self.taskbar_check.isChecked()
        self.accept()

    @property
    def settings(self) -> AppSettings:
        return self._settings
