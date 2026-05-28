"""Planner tab - Projects and tasks management"""

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QInputDialog, QMessageBox, QSplitter,
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QRadioButton,
    QCheckBox, QButtonGroup, QScrollArea
)
from PySide2.QtCore import Qt

from src.data_manager import DataManager


class PlannerTab(QWidget):
    """Tab for managing projects and tasks"""
    
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        self.current_project_id = None
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QHBoxLayout()
        
        # Left panel - Projects and details
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Projects:"))
        
        self.projects_list = QListWidget()
        self.projects_list.itemSelectionChanged.connect(self.on_project_selected)
        left_layout.addWidget(self.projects_list)
        
        projects_btn_layout = QHBoxLayout()
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.create_project)
        delete_project_btn = QPushButton("Delete Project")
        delete_project_btn.clicked.connect(self.delete_project)
        projects_btn_layout.addWidget(new_project_btn)
        projects_btn_layout.addWidget(delete_project_btn)
        left_layout.addLayout(projects_btn_layout)
        
        # Project Details Group
        details_group = QGroupBox("Project Details")
        details_layout = QFormLayout()
        
        # Project Name
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Enter project name")
        details_layout.addRow("Project Name:", self.project_name_input)
        
        # Supervisor Name
        self.supervisor_name_input = QLineEdit()
        self.supervisor_name_input.setPlaceholderText("Enter supervisor name")
        details_layout.addRow("Supervisor Name:", self.supervisor_name_input)
        
        # Department ComboBox
        self.department_combo = QComboBox()
        self.department_combo.addItems(["Rig", "FX", "Animation", "Assets"])
        details_layout.addRow("Department:", self.department_combo)
        
        details_group.setLayout(details_layout)
        left_layout.addWidget(details_group)
        
        # Project Type Group
        project_type_group = QGroupBox("Project Type")
        project_type_layout = QVBoxLayout()
        
        self.project_type_group = QButtonGroup()
        self.animation_radio = QRadioButton("Animation")
        self.vfx_radio = QRadioButton("VFX")
        self.vfx_radio.setChecked(True)  # Default selection
        self.gaming_radio = QRadioButton("Gaming")
        
        self.project_type_group.addButton(self.animation_radio, 0)
        self.project_type_group.addButton(self.vfx_radio, 1)
        self.project_type_group.addButton(self.gaming_radio, 2)
        
        project_type_layout.addWidget(self.animation_radio)
        project_type_layout.addWidget(self.vfx_radio)
        project_type_layout.addWidget(self.gaming_radio)
        project_type_group.setLayout(project_type_layout)
        left_layout.addWidget(project_type_group)
        
        # Flags Group
        flags_group = QGroupBox("Flags")
        flags_layout = QVBoxLayout()
        
        self.needs_daily_review_checkbox = QCheckBox("Needs daily Review")
        self.client_delivery_checkbox = QCheckBox("Client Delivery")
        self.high_priority_checkbox = QCheckBox("High priority")
        
        flags_layout.addWidget(self.needs_daily_review_checkbox)
        flags_layout.addWidget(self.client_delivery_checkbox)
        flags_layout.addWidget(self.high_priority_checkbox)
        flags_group.setLayout(flags_layout)
        left_layout.addWidget(flags_group)
        
        # Add stretch to push everything to top
        left_layout.addStretch()
        
        # Right panel - Tasks
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Tasks:"))
        
        self.tasks_list = QListWidget()
        right_layout.addWidget(self.tasks_list)
        
        tasks_btn_layout = QHBoxLayout()
        new_task_btn = QPushButton("New Task")
        new_task_btn.clicked.connect(self.create_task)
        delete_task_btn = QPushButton("Delete Task")
        delete_task_btn.clicked.connect(self.delete_task)
        tasks_btn_layout.addWidget(new_task_btn)
        tasks_btn_layout.addWidget(delete_task_btn)
        right_layout.addLayout(tasks_btn_layout)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def refresh(self):
        """Refresh projects and tasks lists"""
        self.refresh_projects()
        if self.current_project_id:
            self.refresh_tasks()
    
    def refresh_projects(self):
        """Refresh projects list from data manager"""
        self.projects_list.clear()
        projects = self.data_manager.get_all_projects()
        
        for project in projects:
            item = QListWidgetItem(project.name)
            item.setData(Qt.UserRole, project.id)
            self.projects_list.addItem(item)
    
    def refresh_tasks(self):
        """Refresh tasks list for current project"""
        self.tasks_list.clear()
        
        if not self.current_project_id:
            return
        
        tasks = self.data_manager.get_tasks_for_project(self.current_project_id)
        
        for task in tasks:
            status_str = f" [{task.status}]"
            item_text = f"{task.name}{status_str}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, task.id)
            self.tasks_list.addItem(item)
    
    def on_project_selected(self):
        """Handle project selection"""
        selected_items = self.projects_list.selectedItems()
        if selected_items:
            self.current_project_id = selected_items[0].data(Qt.UserRole)
            self.refresh_tasks()
            self.load_project_details()
        else:
            self.current_project_id = None
            self.tasks_list.clear()
            self.clear_project_details()
    
    def create_project(self):
        """Create a new project"""
        # Get values from form
        name = self.project_name_input.text().strip()
        supervisor_name = self.supervisor_name_input.text().strip()
        department = self.department_combo.currentText()
        
        # Get project type
        if self.animation_radio.isChecked():
            project_type = "Animation"
        elif self.gaming_radio.isChecked():
            project_type = "Gaming"
        else:
            project_type = "VFX"
        
        # Get flags
        needs_daily_review = self.needs_daily_review_checkbox.isChecked()
        client_delivery = self.client_delivery_checkbox.isChecked()
        high_priority = self.high_priority_checkbox.isChecked()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a project name.")
            return
        
        self.data_manager.create_project(
            name, supervisor_name, department,
            project_type, needs_daily_review, client_delivery, high_priority
        )
        self.refresh_projects()
        self.clear_project_details()
    
    def delete_project(self):
        """Delete selected project"""
        selected_items = self.projects_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a project to delete.")
            return
        
        project_id = selected_items[0].data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this project and all its tasks?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.data_manager.delete_project(project_id)
            self.current_project_id = None
            self.refresh()
    
    def create_task(self):
        """Create a new task in selected project"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Warning", "Please select a project first.")
            return
        
        name, ok = QInputDialog.getText(self, "New Task", "Task name:")
        if ok and name:
            self.data_manager.create_task(self.current_project_id, name)
            self.refresh_tasks()
    
    def delete_task(self):
        """Delete selected task"""
        selected_items = self.tasks_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a task to delete.")
            return
        
        task_id = selected_items[0].data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this task?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.data_manager.delete_task(self.current_project_id, task_id)
            self.refresh_tasks()
    
    def load_project_details(self):
        """Load project details into form fields"""
        if not self.current_project_id:
            return
        
        project = self.data_manager.get_project(self.current_project_id)
        if project:
            self.project_name_input.setText(project.name)
            self.supervisor_name_input.setText(project.supervisor_name)
            self.department_combo.setCurrentText(project.department)
            
            # Load project type
            if project.project_type == "Animation":
                self.animation_radio.setChecked(True)
            elif project.project_type == "Gaming":
                self.gaming_radio.setChecked(True)
            else:
                self.vfx_radio.setChecked(True)
            
            # Load flags
            self.needs_daily_review_checkbox.setChecked(project.needs_daily_review)
            self.client_delivery_checkbox.setChecked(project.client_delivery)
            self.high_priority_checkbox.setChecked(project.high_priority)
    
    def clear_project_details(self):
        """Clear project details form fields"""
        self.project_name_input.clear()
        self.supervisor_name_input.clear()
        self.department_combo.setCurrentIndex(0)
        self.vfx_radio.setChecked(True)  # Default to VFX
        self.needs_daily_review_checkbox.setChecked(False)
        self.client_delivery_checkbox.setChecked(False)
        self.high_priority_checkbox.setChecked(False)
        self.department_combo.setCurrentIndex(0)
