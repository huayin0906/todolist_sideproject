import sys
import os

# Ensure the project root is on the path so 'core' and 'ui' are importable
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.storage import load_data
from core.scheduler import Scheduler
from ui.main_window import MainWindow


def main():
    # Crisp rendering on high-DPI screens
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("To-Do List")

    tasks, settings = load_data()

    window = MainWindow(tasks, settings)
    window.show()

    scheduler = Scheduler(window.task_manager, settings)
    scheduler.reset_triggered.connect(window.on_reset)
    scheduler.notification_triggered.connect(window.show_notification)
    scheduler.force_check()     # check immediately on startup

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
