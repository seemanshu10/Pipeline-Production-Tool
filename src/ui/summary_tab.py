"""Summary tab - Statistics and overview"""

import json
from datetime import datetime
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QPushButton, QFileDialog, QMessageBox
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont

from src.data_manager import DataManager


class SummaryTab(QWidget):
    """Tab for displaying project statistics and summaries"""
    
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Project Summary & Statistics")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Projects Group
        projects_group = QGroupBox("Projects")
        projects_layout = QGridLayout()
        
        self.total_projects_label = QLabel("0")
        projects_layout.addWidget(QLabel("Total Projects:"), 0, 0)
        projects_layout.addWidget(self.total_projects_label, 0, 1)
        
        projects_group.setLayout(projects_layout)
        layout.addWidget(projects_group)
        
        # Tasks Group
        tasks_group = QGroupBox("Tasks")
        tasks_layout = QGridLayout()
        
        self.total_tasks_label = QLabel("0")
        self.pending_tasks_label = QLabel("0")
        self.in_progress_tasks_label = QLabel("0")
        self.completed_tasks_label = QLabel("0")
        
        tasks_layout.addWidget(QLabel("Total Tasks:"), 0, 0)
        tasks_layout.addWidget(self.total_tasks_label, 0, 1)
        
        tasks_layout.addWidget(QLabel("Pending:"), 1, 0)
        tasks_layout.addWidget(self.pending_tasks_label, 1, 1)
        
        tasks_layout.addWidget(QLabel("In Progress:"), 2, 0)
        tasks_layout.addWidget(self.in_progress_tasks_label, 2, 1)
        
        tasks_layout.addWidget(QLabel("Completed:"), 3, 0)
        tasks_layout.addWidget(self.completed_tasks_label, 3, 1)
        
        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)
        
        # Assets Group
        assets_group = QGroupBox("Assets")
        assets_layout = QGridLayout()
        
        self.total_assets_label = QLabel("0")
        assets_layout.addWidget(QLabel("Total Assets:"), 0, 0)
        assets_layout.addWidget(self.total_assets_label, 0, 1)
        
        assets_group.setLayout(assets_layout)
        layout.addWidget(assets_group)
        
        layout.addStretch()

        # Export group
        export_group = QGroupBox("Export")
        export_layout = QHBoxLayout()

        self.export_btn = QPushButton("Export Summary as JSON")
        self.export_btn.setFixedHeight(36)
        self.export_btn.clicked.connect(self.export_summary)
        export_layout.addWidget(self.export_btn)
        export_layout.addStretch()
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        self.setLayout(layout)

    def refresh(self):
        """Refresh statistics from data manager"""
        stats = self.data_manager.get_statistics()

        self.total_projects_label.setText(str(stats["total_projects"]))
        self.total_tasks_label.setText(str(stats["total_tasks"]))
        self.pending_tasks_label.setText(str(stats["pending_tasks"]))
        self.in_progress_tasks_label.setText(str(stats["in_progress_tasks"]))
        self.completed_tasks_label.setText(str(stats["completed_tasks"]))
        self.total_assets_label.setText(str(stats["total_assets"]))

    def export_summary(self):
        """Export full project summary to a user-chosen JSON file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Summary", "pipeline_summary.json",
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"

        projects = self.data_manager.get_all_projects()
        assets = self.data_manager.get_all_assets()
        stats = self.data_manager.get_statistics()

        summary = {
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "statistics": stats,
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "supervisor": p.supervisor_name,
                    "department": p.department,
                    "project_type": p.project_type,
                    "priority": p.priority,
                    "completion": p.completion,
                    "timeline_offset": p.timeline_offset,
                    "flags": {
                        "needs_daily_review": p.needs_daily_review,
                        "client_delivery": p.client_delivery,
                        "high_priority": p.high_priority,
                    },
                    "notes": p.notes,
                    "created_date": p.created_date,
                    "tasks": [
                        {
                            "id": t.id,
                            "name": t.name,
                            "status": t.status,
                            "priority": t.priority,
                            "created_date": t.created_date,
                        }
                        for t in p.tasks
                    ],
                }
                for p in projects
            ],
            "assets": [
                {
                    "id": a.id,
                    "name": a.name,
                    "type": a.asset_type,
                    "created_date": a.created_date,
                }
                for a in assets
            ],
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            if self.parent_window:
                self.parent_window.statusBar().showMessage(
                    f"Summary exported: {path}", 5000
                )
        except OSError as e:
            QMessageBox.critical(self, "Export Error", f"Could not write file:\n{e}")
