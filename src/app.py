"""Main application initialization"""

import sys
from PySide2.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def run():
    """Run the application"""
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
