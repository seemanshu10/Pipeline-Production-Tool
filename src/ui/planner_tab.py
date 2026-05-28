"""Planner tab - Projects and tasks management"""

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QInputDialog, QMessageBox, QSplitter,
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QRadioButton,
    QCheckBox, QButtonGroup, QScrollArea, QSlider, QScrollBar, QProgressBar,
    QTextEdit, QGridLayout
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
        self._pre_completion_statuses: dict = {}  # task_id -> status before slider hit 100
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QHBoxLayout()
        
        # Left panel - Details, Project Type, Flags, Priority/Timeline
        left_layout = QVBoxLayout()

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
        flags_group = QGroupBox("Project Flags")
        flags_layout = QVBoxLayout()
        
        self.needs_daily_review_checkbox = QCheckBox("Needs daily Review")
        self.client_delivery_checkbox = QCheckBox("Client Delivery")
        self.high_priority_checkbox = QCheckBox("High priority")
        
        flags_layout.addWidget(self.needs_daily_review_checkbox)
        flags_layout.addWidget(self.client_delivery_checkbox)
        flags_layout.addWidget(self.high_priority_checkbox)
        flags_group.setLayout(flags_layout)
        left_layout.addWidget(flags_group)
        
        # Priority and Timeline Group (new)
        priority_group = QGroupBox("Priority and Timeline")
        priority_layout = QVBoxLayout()

        # Priority slider (0-100)
        priority_row = QHBoxLayout()
        self.priority_slider = QSlider(Qt.Horizontal)
        self.priority_slider.setMinimum(0)
        self.priority_slider.setMaximum(100)
        self.priority_slider.setValue(50)
        self.priority_value_label = QLabel("50")
        self.priority_slider.valueChanged.connect(lambda v: self.priority_value_label.setText(str(v)))
        self.priority_slider.sliderReleased.connect(self._auto_save_priority)
        priority_row.addWidget(QLabel("Priority:"))
        priority_row.addWidget(self.priority_slider)
        priority_row.addWidget(self.priority_value_label)
        priority_layout.addLayout(priority_row)

        # Timeline offset scrollbar (0-100)
        timeline_row = QHBoxLayout()
        self.timeline_scroll = QScrollBar(Qt.Horizontal)
        self.timeline_scroll.setMinimum(0)
        self.timeline_scroll.setMaximum(100)
        self.timeline_scroll.setValue(25)
        self.timeline_value_label = QLabel("25")
        self.timeline_scroll.valueChanged.connect(lambda v: self.timeline_value_label.setText(str(v)))
        self.timeline_scroll.sliderReleased.connect(self._auto_save_timeline)
        timeline_row.addWidget(QLabel("Timeline Offset:"))
        timeline_row.addWidget(self.timeline_scroll)
        timeline_row.addWidget(self.timeline_value_label)
        priority_layout.addLayout(timeline_row)

        # Completion slider + progress bar (0-100)
        completion_row = QHBoxLayout()
        self.completion_slider = QSlider(Qt.Horizontal)
        self.completion_slider.setMinimum(0)
        self.completion_slider.setMaximum(100)
        self.completion_slider.setValue(25)
        self.completion_progress = QProgressBar()
        self.completion_progress.setMinimum(0)
        self.completion_progress.setMaximum(100)
        self.completion_progress.setValue(25)
        self.completion_value_label = QLabel("25")
        self.completion_slider.valueChanged.connect(
            lambda v: [self.completion_progress.setValue(v), self.completion_value_label.setText(str(v))]
        )
        self.completion_slider.sliderReleased.connect(self._on_completion_released)
        completion_row.addWidget(QLabel("Completion:"))
        completion_row.addWidget(self.completion_slider)
        completion_row.addWidget(self.completion_progress)
        completion_row.addWidget(self.completion_value_label)
        priority_layout.addLayout(completion_row)

        priority_group.setLayout(priority_layout)
        left_layout.addWidget(priority_group)

        # Actions group — 2×2 grid
        actions_group = QGroupBox("Actions")
        actions_grid = QGridLayout()

        add_task_btn = QPushButton("Add Task")
        add_task_btn.clicked.connect(self.create_task)
        remove_task_btn = QPushButton("Remove Task")
        remove_task_btn.clicked.connect(self.delete_task)
        mark_done_btn = QPushButton("Mark Done")
        mark_done_btn.clicked.connect(self.mark_task_done)
        clear_notes_btn = QPushButton("Clear Notes")
        clear_notes_btn.clicked.connect(self.clear_notes)

        actions_grid.addWidget(add_task_btn,    0, 0)
        actions_grid.addWidget(remove_task_btn, 0, 1)
        actions_grid.addWidget(mark_done_btn,   1, 0)
        actions_grid.addWidget(clear_notes_btn, 1, 1)

        actions_group.setLayout(actions_grid)
        left_layout.addWidget(actions_group)

        # Save Changes button
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_project_details)
        self.save_btn.setEnabled(False)
        left_layout.addWidget(self.save_btn)

        # Add stretch to push everything to top
        left_layout.addStretch()
        
        # Right panel - Projects and Tasks
        right_layout = QVBoxLayout()
        # Project Notes
        notes_group = QGroupBox("Project Notes")
        notes_layout = QVBoxLayout()
        self.project_notes = QTextEdit()
        self.project_notes.setPlaceholderText("Enter project notes here...")
        notes_layout.addWidget(self.project_notes)
        notes_group.setLayout(notes_layout)
        right_layout.addWidget(notes_group)
        right_layout.addWidget(QLabel("Projects:"))

        self.projects_list = QListWidget()
        self.projects_list.itemSelectionChanged.connect(self.on_project_selected)
        right_layout.addWidget(self.projects_list)

        projects_btn_layout = QHBoxLayout()
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.create_project)
        delete_project_btn = QPushButton("Delete Project")
        delete_project_btn.clicked.connect(self.delete_project)
        projects_btn_layout.addWidget(new_project_btn)
        projects_btn_layout.addWidget(delete_project_btn)
        right_layout.addLayout(projects_btn_layout)

        # Separator to tasks
        right_layout.addWidget(QLabel("Tasks:"))

        self.tasks_list = QListWidget()
        right_layout.addWidget(self.tasks_list)

        
        
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

        project = self.data_manager.get_project_by_id(self.current_project_id)
        if not project:
            return

        for task in project.tasks:
            item_text = (
                f"{project.name}  |  {project.department}  |  "
                f"{task.name}  |  {task.status}"
            )
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
            self._set_status(f"Project '{selected_items[0].text()}' selected.")
        else:
            self.current_project_id = None
            self.tasks_list.clear()
            self.clear_project_details()
            self._set_status("No project selected.")
    
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
            project_type, needs_daily_review, client_delivery, high_priority,
            priority=self.priority_slider.value(),
            timeline_offset=self.timeline_scroll.value(),
            completion=self.completion_slider.value()
        )
        self.refresh_projects()
        self.clear_project_details()
        self._set_status(f"Project '{name}' created.")
    
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
            project_name = selected_items[0].text()
            self.data_manager.delete_project(project_id)
            self.current_project_id = None
            self.refresh()
            self._set_status(f"Project '{project_name}' deleted.")
    
    def create_task(self):
        """Create a new task in selected project"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Warning", "Please select a project first.")
            return
        
        name, ok = QInputDialog.getText(self, "New Task", "Task name:")
        if ok and name:
            self.data_manager.create_task(self.current_project_id, name)
            self.refresh_tasks()
            self._set_status(f"Task '{name}' created.")
    
    def delete_task(self):
        """Delete selected task"""
        selected_items = self.tasks_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a task to delete.")
            return
        
        task_id = selected_items[0].data(Qt.UserRole)
        task_name = selected_items[0].text().split("  |  ")[2]

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this task?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.data_manager.delete_task(self.current_project_id, task_id)
            self.refresh_tasks()
            self._set_status(f"Task '{task_name}' deleted.")
    
    def load_project_details(self):
        """Load project details into form fields"""
        if not self.current_project_id:
            return
        project = self.data_manager.get_project_by_id(self.current_project_id)
        if project:
            # Snapshot task statuses so the completion slider can restore them
            self._pre_completion_statuses = {t.id: t.status for t in project.tasks}
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

            # Load priority/timeline/completion — block signals to avoid spurious auto-saves on load
            for _w in (self.priority_slider, self.timeline_scroll, self.completion_slider):
                _w.blockSignals(True)
            self.priority_slider.setValue(project.priority)
            self.timeline_scroll.setValue(project.timeline_offset)
            self.completion_slider.setValue(project.completion)
            for _w in (self.priority_slider, self.timeline_scroll, self.completion_slider):
                _w.blockSignals(False)
            self.project_notes.setPlainText(project.notes)
            self.save_btn.setEnabled(True)
    
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
        self.priority_slider.setValue(50)
        self.timeline_scroll.setValue(25)
        self.completion_slider.setValue(25)
        self.project_notes.clear()
        self.save_btn.setEnabled(False)

    def save_project_details(self):
        """Persist current form values to the selected project"""
        if not self.current_project_id:
            return

        project = self.data_manager.get_project_by_id(self.current_project_id)
        if not project:
            return

        name = self.project_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Project name cannot be empty.")
            return

        project.name = name
        project.supervisor_name = self.supervisor_name_input.text().strip()
        project.department = self.department_combo.currentText()

        if self.animation_radio.isChecked():
            project.project_type = "Animation"
        elif self.gaming_radio.isChecked():
            project.project_type = "Gaming"
        else:
            project.project_type = "VFX"

        project.needs_daily_review = self.needs_daily_review_checkbox.isChecked()
        project.client_delivery = self.client_delivery_checkbox.isChecked()
        project.high_priority = self.high_priority_checkbox.isChecked()
        project.priority = self.priority_slider.value()
        project.timeline_offset = self.timeline_scroll.value()
        project.completion = self.completion_slider.value()
        project.notes = self.project_notes.toPlainText()

        self.data_manager.update_project(project)
        self.refresh_projects()

        self._set_status(f"Project '{name}' saved.")

    def mark_task_done(self):
        """Mark the selected task as done"""
        if not self.current_project_id:
            QMessageBox.warning(self, "Warning", "Please select a project first.")
            return

        selected_items = self.tasks_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a task to mark as done.")
            return

        task_id = selected_items[0].data(Qt.UserRole)
        project = self.data_manager.get_project_by_id(self.current_project_id)
        if not project:
            return

        for task in project.tasks:
            if task.id == task_id:
                task.status = "done"
                self._pre_completion_statuses[task_id] = "done"
                self.data_manager.update_task(self.current_project_id, task)
                self.refresh_tasks()
                self._set_status(f"Task '{task.name}' marked as done.")
                break

    def clear_notes(self):
        """Clear the project notes text field"""
        self.project_notes.clear()
        self._set_status("Notes cleared.")

    def _auto_save_priority(self):
        if not self.current_project_id:
            return
        project = self.data_manager.get_project_by_id(self.current_project_id)
        if project:
            project.priority = self.priority_slider.value()
            self.data_manager.update_project(project)
            self._set_status(f"Priority set to {project.priority}.")

    def _auto_save_timeline(self):
        if not self.current_project_id:
            return
        project = self.data_manager.get_project_by_id(self.current_project_id)
        if project:
            project.timeline_offset = self.timeline_scroll.value()
            self.data_manager.update_project(project)
            self._set_status(f"Timeline offset set to {project.timeline_offset}.")

    def _on_completion_released(self):
        if not self.current_project_id:
            return
        project = self.data_manager.get_project_by_id(self.current_project_id)
        if not project:
            return
        project.completion = self.completion_slider.value()
        if project.completion == 100:
            for task in project.tasks:
                task.status = "done"
            self.data_manager.update_project(project)
            self.refresh_tasks()
            self._set_status("All tasks marked as done — project 100% complete.")
        else:
            if self._pre_completion_statuses:
                for task in project.tasks:
                    if task.id in self._pre_completion_statuses:
                        task.status = self._pre_completion_statuses[task.id]
            self.data_manager.update_project(project)
            self.refresh_tasks()
            self._set_status(f"Completion set to {project.completion}%.")

    def _set_status(self, message: str, timeout: int = 3000):
        if self.parent_window:
            self.parent_window.statusBar().showMessage(message, timeout)
