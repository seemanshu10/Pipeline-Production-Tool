"""Main window with tab widget"""

from PySide2.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QWidget,
                               QMenuBar, QMenu, QMessageBox, QFileDialog)
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence

from src.data_manager import DataManager
from src.ui.planner_tab import PlannerTab
from src.ui.assets_tab import AssetsTab
from src.ui.summary_tab import SummaryTab
from src.constants import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Set window properties
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)
        layout.addWidget(self.tabs)
        
        # Create and add tabs
        self.planner_tab = PlannerTab(self.data_manager, self)
        self.assets_tab = AssetsTab(self.data_manager, self)
        self.summary_tab = SummaryTab(self.data_manager, self)
        
        self.tabs.addTab(self.planner_tab, "Planner")
        self.tabs.addTab(self.assets_tab, "Assets")
        self.tabs.addTab(self.summary_tab, "Summary")
        
        # Connect tab changed signal to refresh summary
        self.tabs.currentChanged.connect(self.on_tab_changed)
    
    def on_tab_changed(self, index):
        """Handle tab change event"""
        if index == 1:  # Assets tab
            self.assets_tab.refresh()
        elif index == 2:  # Summary tab
            self.summary_tab.refresh()
    
    def refresh_all(self):
        """Refresh all tabs with latest data"""
        self.planner_tab.refresh()
        self.assets_tab.refresh()
        self.summary_tab.refresh()
    
    def create_menu_bar(self):
        """Create and setup menu bar with File and Help menus"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        new_action = file_menu.addAction("New Project")
        new_action.setShortcut(QKeySequence.New)          # Ctrl+N
        new_action.triggered.connect(self.new_project)

        file_menu.addSeparator()

        open_action = file_menu.addAction("Open Project...")
        open_action.setShortcut(QKeySequence.Open)        # Ctrl+O
        open_action.triggered.connect(self.open_project_file)

        save_action = file_menu.addAction("Save Project...")
        save_action.setShortcut(QKeySequence.Save)        # Ctrl+S
        save_action.triggered.connect(self.save_project_file)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut(QKeySequence.Quit)        # Ctrl+Q
        exit_action.triggered.connect(self.close)

        # Help/About Menu
        help_menu = menubar.addMenu("Help")

        about_action = help_menu.addAction("About")
        about_action.setShortcut(QKeySequence("F1"))
        about_action.triggered.connect(self.show_about)

    def new_project(self):
        """Reset planner form and switch to Planner tab ready for a new entry."""
        self.tabs.setCurrentIndex(0)
        self.planner_tab.projects_list.clearSelection()
        self.planner_tab.clear_project_details()
        self.statusBar().showMessage("Fill in the details and click 'New Project'.", 4000)

    def open_project_file(self):
        """Open a JSON pipeline file and replace the current session data."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Project File", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        ok = self.data_manager.load_from_file(path)
        if ok:
            self.refresh_all()
            self.statusBar().showMessage(f"Loaded: {path}", 5000)
        else:
            QMessageBox.critical(self, "Open Error", f"Could not load file:\n{path}")

    def save_project_file(self):
        """Save the current session data to a user-chosen JSON file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project File", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"
        ok = self.data_manager.save_to_file(path)
        if ok:
            self.statusBar().showMessage(f"Saved: {path}", 5000)
        else:
            QMessageBox.critical(self, "Save Error", f"Could not save file:\n{path}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            f"About {APP_TITLE}",
            f"{APP_TITLE} v1.0\n\n"
            "A modular PySide2 desktop application for managing VFX projects, "
            "tasks, and assets.\n\n"
            "© 2026 VFX Pipeline Team"
        )
