"""Main application initialization"""

import sys
from pathlib import Path
from PySide2.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def _load_stylesheet() -> str:
    qss_path = Path(__file__).parent.parent / "resources" / "style.qss"
    try:
        return qss_path.read_text(encoding="utf-8")
    except OSError:
        return ""


def run():
    """Run the application"""
    app = QApplication(sys.argv)
    app.setStyleSheet(_load_stylesheet())

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
