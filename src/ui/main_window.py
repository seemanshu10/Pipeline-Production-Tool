"""Main window with tab widget"""

from PySide2.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QWidget, 
                               QMenuBar, QMenu, QMessageBox)
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence

from src.data_manager import DataManager
from src.ui.planner_tab import PlannerTab
from src.ui.assets_tab import AssetsTab
from src.ui.summary_tab import SummaryTab


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Set window properties
        self.setWindowTitle("VFX Pipeline Production Tool")
        self.setGeometry(100, 100, 900, 700)
        
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
        if index == 2:  # Summary tab
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
        
        # New action
        new_action = file_menu.addAction("New Project")
        new_action.setShortcut(QKeySequence.New)  # Ctrl+N
        new_action.triggered.connect(self.new_project)
        
        # Separator
        file_menu.addSeparator()
        
        # Exit action
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut(QKeySequence.Quit)  # Ctrl+Q
        exit_action.triggered.connect(self.close)
        
        # Help/About Menu
        help_menu = menubar.addMenu("Help")
        
        # About action
        about_action = help_menu.addAction("About")
        about_action.setShortcut(QKeySequence("F1"))
        about_action.triggered.connect(self.show_about)
    
    def new_project(self):
        """Handle new project action"""
        self.statusBar().showMessage("Create new project - Switch to Planner tab")
        self.tabs.setCurrentIndex(0)  # Switch to Planner tab
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About VFX Pipeline Production Tool",
            "VFX Pipeline Production Tool v1.0\n\n"
            "A modular PySide2 desktop application for managing VFX projects, "
            "tasks, and assets.\n\n"
            "© 2026 VFX Pipeline Team"
        )
