"""Summary tab - Per-project and studio-wide overview"""

import json
from datetime import datetime
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QPushButton, QFileDialog, QMessageBox,
    QComboBox, QProgressBar, QScrollArea, QFrame, QSizePolicy
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont

from src.data_manager import DataManager


class _CollapsibleSection(QWidget):
    """A titled header button that shows/hides its content area on click."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._title = title
        self._toggle_btn = QPushButton()
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setChecked(True)
        self._toggle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._toggle_btn.setFixedHeight(32)
        self._toggle_btn.clicked.connect(self._on_toggle)
        self._update_label(True)
        layout.addWidget(self._toggle_btn)

        self._body = QWidget()
        body_outer = QVBoxLayout(self._body)
        body_outer.setContentsMargins(0, 4, 0, 4)
        body_outer.setSpacing(6)
        self.body_layout = body_outer          # callers add content here
        layout.addWidget(self._body)

    def _update_label(self, expanded: bool):
        arrow = "▼" if expanded else "▶"
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self._toggle_btn.setFont(font)
        self._toggle_btn.setText(f"  {arrow}   {self._title}")
        self._toggle_btn.setStyleSheet(
            "QPushButton { text-align: left; padding-left: 6px; }"
        )

    def _on_toggle(self, checked: bool):
        self._body.setVisible(checked)
        self._update_label(checked)


class SummaryTab(QWidget):
    """Tab for displaying per-project and studio-wide summaries"""

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        self.init_ui()
        self.refresh()

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setSpacing(10)

        # ── PROJECT SUMMARY (collapsible) ─────────────────────────────────
        proj_section = _CollapsibleSection("Project Summary")
        cl = proj_section.body_layout

        # Project selector row
        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Select Project:"))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(220)
        self.project_combo.currentIndexChanged.connect(self._on_project_selected)
        selector_row.addWidget(self.project_combo)
        selector_row.addStretch()
        cl.addLayout(selector_row)

        # Details + Progress
        proj_top_row = QHBoxLayout()

        details_group = QGroupBox("Details")
        details_grid = QGridLayout()
        details_grid.setColumnStretch(1, 1)
        self._proj_name_val       = QLabel("—")
        self._proj_supervisor_val = QLabel("—")
        self._proj_dept_val       = QLabel("—")
        self._proj_type_val       = QLabel("—")
        self._proj_created_val    = QLabel("—")
        for row, (lbl, val) in enumerate([
            ("Name:",       self._proj_name_val),
            ("Supervisor:", self._proj_supervisor_val),
            ("Department:", self._proj_dept_val),
            ("Type:",       self._proj_type_val),
            ("Created:",    self._proj_created_val),
        ]):
            details_grid.addWidget(QLabel(lbl), row, 0, Qt.AlignTop)
            details_grid.addWidget(val,         row, 1)
        details_group.setLayout(details_grid)
        proj_top_row.addWidget(details_group)

        progress_group = QGroupBox("Progress")
        progress_grid = QGridLayout()
        self._proj_priority_bar   = QProgressBar()
        self._proj_completion_bar = QProgressBar()
        self._proj_timeline_bar   = QProgressBar()
        for bar in (self._proj_priority_bar, self._proj_completion_bar, self._proj_timeline_bar):
            bar.setMinimum(0)
            bar.setMaximum(100)
        for row, (lbl, bar) in enumerate([
            ("Priority:",        self._proj_priority_bar),
            ("Completion:",      self._proj_completion_bar),
            ("Timeline Offset:", self._proj_timeline_bar),
        ]):
            progress_grid.addWidget(QLabel(lbl), row, 0)
            progress_grid.addWidget(bar,         row, 1)
        progress_group.setLayout(progress_grid)
        proj_top_row.addWidget(progress_group)
        cl.addLayout(proj_top_row)

        # Tasks + Flags
        proj_mid_row = QHBoxLayout()

        tasks_group = QGroupBox("Tasks")
        tasks_grid = QGridLayout()
        self._proj_tasks_total_val   = QLabel("0")
        self._proj_tasks_pending_val = QLabel("0")
        self._proj_tasks_inprog_val  = QLabel("0")
        self._proj_tasks_done_val    = QLabel("0")
        for row, (lbl, val) in enumerate([
            ("Total:",       self._proj_tasks_total_val),
            ("Pending:",     self._proj_tasks_pending_val),
            ("In Progress:", self._proj_tasks_inprog_val),
            ("Done:",        self._proj_tasks_done_val),
        ]):
            tasks_grid.addWidget(QLabel(lbl), row, 0)
            tasks_grid.addWidget(val,         row, 1)
        tasks_group.setLayout(tasks_grid)
        proj_mid_row.addWidget(tasks_group)

        flags_group = QGroupBox("Flags")
        flags_layout = QVBoxLayout()
        self._proj_flag_daily  = QLabel()
        self._proj_flag_client = QLabel()
        self._proj_flag_hipri  = QLabel()
        for lbl in (self._proj_flag_daily, self._proj_flag_client, self._proj_flag_hipri):
            flags_layout.addWidget(lbl)
        flags_layout.addStretch()
        flags_group.setLayout(flags_layout)
        proj_mid_row.addWidget(flags_group)
        cl.addLayout(proj_mid_row)

        # Export project button
        self._export_proj_btn = QPushButton("Export Project Summary as JSON")
        self._export_proj_btn.setFixedHeight(32)
        self._export_proj_btn.setEnabled(False)
        self._export_proj_btn.clicked.connect(self._export_project_summary)
        cl.addWidget(self._export_proj_btn)

        inner_layout.addWidget(proj_section)

        # ── DIVIDER ───────────────────────────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        inner_layout.addWidget(divider)

        # ── STUDIO SUMMARY (collapsible) ──────────────────────────────────
        studio_section = _CollapsibleSection("Studio Summary")
        sl = studio_section.body_layout

        studio_top_row = QHBoxLayout()

        overall_group = QGroupBox("Overall")
        overall_grid = QGridLayout()
        self._st_projects = QLabel("0")
        self._st_tasks    = QLabel("0")
        self._st_pending  = QLabel("0")
        self._st_inprog   = QLabel("0")
        self._st_done     = QLabel("0")
        self._st_assets   = QLabel("0")
        for row, (lbl, val) in enumerate([
            ("Total Projects:", self._st_projects),
            ("Total Tasks:",    self._st_tasks),
            ("  Pending:",      self._st_pending),
            ("  In Progress:",  self._st_inprog),
            ("  Done:",         self._st_done),
            ("Total Assets:",   self._st_assets),
        ]):
            overall_grid.addWidget(QLabel(lbl), row, 0)
            overall_grid.addWidget(val,         row, 1)
        overall_group.setLayout(overall_grid)
        studio_top_row.addWidget(overall_group)

        type_group = QGroupBox("Projects by Type")
        type_grid = QGridLayout()
        self._st_type_vfx  = QLabel("0")
        self._st_type_anim = QLabel("0")
        self._st_type_game = QLabel("0")
        for row, (lbl, val) in enumerate([
            ("VFX:",       self._st_type_vfx),
            ("Animation:", self._st_type_anim),
            ("Gaming:",    self._st_type_game),
        ]):
            type_grid.addWidget(QLabel(lbl), row, 0)
            type_grid.addWidget(val,         row, 1)
        type_group.setLayout(type_grid)
        studio_top_row.addWidget(type_group)

        dept_group = QGroupBox("Projects by Department")
        dept_grid = QGridLayout()
        self._st_dept_rig   = QLabel("0")
        self._st_dept_fx    = QLabel("0")
        self._st_dept_anim  = QLabel("0")
        self._st_dept_asset = QLabel("0")
        for row, (lbl, val) in enumerate([
            ("Rig:",       self._st_dept_rig),
            ("FX:",        self._st_dept_fx),
            ("Animation:", self._st_dept_anim),
            ("Assets:",    self._st_dept_asset),
        ]):
            dept_grid.addWidget(QLabel(lbl), row, 0)
            dept_grid.addWidget(val,         row, 1)
        dept_group.setLayout(dept_grid)
        studio_top_row.addWidget(dept_group)
        sl.addLayout(studio_top_row)

        studio_bot_row = QHBoxLayout()

        studio_flags_group = QGroupBox("Studio Flags")
        studio_flags_grid = QGridLayout()
        self._st_flag_hipri  = QLabel("0")
        self._st_flag_client = QLabel("0")
        self._st_flag_daily  = QLabel("0")
        for row, (lbl, val) in enumerate([
            ("High Priority:",      self._st_flag_hipri),
            ("Client Delivery:",    self._st_flag_client),
            ("Needs Daily Review:", self._st_flag_daily),
        ]):
            studio_flags_grid.addWidget(QLabel(lbl), row, 0)
            studio_flags_grid.addWidget(val,         row, 1)
        studio_flags_group.setLayout(studio_flags_grid)
        studio_bot_row.addWidget(studio_flags_group)

        completion_group = QGroupBox("Studio Completion")
        completion_layout = QVBoxLayout()
        self._st_completion_bar = QProgressBar()
        self._st_completion_bar.setMinimum(0)
        self._st_completion_bar.setMaximum(100)
        completion_layout.addWidget(self._st_completion_bar)
        completion_group.setLayout(completion_layout)
        studio_bot_row.addWidget(completion_group)
        sl.addLayout(studio_bot_row)

        # Export studio button
        self._export_studio_btn = QPushButton("Export Studio Summary as JSON")
        self._export_studio_btn.setFixedHeight(32)
        self._export_studio_btn.clicked.connect(self._export_studio_summary)
        sl.addWidget(self._export_studio_btn)

        inner_layout.addWidget(studio_section)
        inner_layout.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll)
        self.setLayout(root)

    # ──────────────────────────────────────────────────────────────────────
    # Refresh
    # ──────────────────────────────────────────────────────────────────────

    def refresh(self):
        self._refresh_studio()
        self._refresh_project_combo()

    def _refresh_studio(self):
        projects = self.data_manager.get_all_projects()
        stats    = self.data_manager.get_statistics()

        self._st_projects.setText(str(stats["total_projects"]))
        self._st_tasks.setText(str(stats["total_tasks"]))
        self._st_pending.setText(str(stats["pending_tasks"]))
        self._st_inprog.setText(str(stats["in_progress_tasks"]))
        self._st_done.setText(str(stats["completed_tasks"]))
        self._st_assets.setText(str(stats["total_assets"]))

        self._st_type_vfx.setText(str(sum(1 for p in projects if p.project_type == "VFX")))
        self._st_type_anim.setText(str(sum(1 for p in projects if p.project_type == "Animation")))
        self._st_type_game.setText(str(sum(1 for p in projects if p.project_type == "Gaming")))

        self._st_dept_rig.setText(str(sum(1 for p in projects if p.department == "Rig")))
        self._st_dept_fx.setText(str(sum(1 for p in projects if p.department == "FX")))
        self._st_dept_anim.setText(str(sum(1 for p in projects if p.department == "Animation")))
        self._st_dept_asset.setText(str(sum(1 for p in projects if p.department == "Assets")))

        self._st_flag_hipri.setText(str(sum(1 for p in projects if p.high_priority)))
        self._st_flag_client.setText(str(sum(1 for p in projects if p.client_delivery)))
        self._st_flag_daily.setText(str(sum(1 for p in projects if p.needs_daily_review)))

        total_tasks = stats["total_tasks"]
        done_tasks  = stats["completed_tasks"]
        pct = int((done_tasks / total_tasks) * 100) if total_tasks else 0
        self._st_completion_bar.setValue(pct)
        self._st_completion_bar.setFormat(
            f"%p%  ({done_tasks}/{total_tasks} tasks done)" if total_tasks else "No tasks"
        )

    def _refresh_project_combo(self):
        current_id = self.project_combo.currentData()
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.addItem("— select a project —", None)
        for p in self.data_manager.get_all_projects():
            self.project_combo.addItem(p.name, p.id)
        idx = self.project_combo.findData(current_id)
        self.project_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.project_combo.blockSignals(False)
        self._on_project_selected(self.project_combo.currentIndex())

    def _on_project_selected(self, index):
        project_id = self.project_combo.itemData(index)
        if not project_id:
            self._clear_project_panel()
            self._export_proj_btn.setEnabled(False)
            return

        p = self.data_manager.get_project_by_id(project_id)
        if not p:
            self._clear_project_panel()
            self._export_proj_btn.setEnabled(False)
            return

        self._proj_name_val.setText(p.name)
        self._proj_supervisor_val.setText(p.supervisor_name or "—")
        self._proj_dept_val.setText(p.department)
        self._proj_type_val.setText(p.project_type)
        self._proj_created_val.setText(p.created_date)

        self._proj_priority_bar.setValue(p.priority)
        self._proj_priority_bar.setFormat(f"{p.priority}/100")
        self._proj_timeline_bar.setValue(p.timeline_offset)
        self._proj_timeline_bar.setFormat(f"{p.timeline_offset}/100")

        total   = len(p.tasks)
        done    = sum(1 for t in p.tasks if t.status == "done")
        inprog  = sum(1 for t in p.tasks if t.status == "in-progress")
        pending = sum(1 for t in p.tasks if t.status == "pending")
        pct = int((done / total) * 100) if total else 0
        self._proj_completion_bar.setValue(pct)
        self._proj_completion_bar.setFormat(f"%p%  ({done}/{total})" if total else "No tasks")

        self._proj_tasks_total_val.setText(str(total))
        self._proj_tasks_pending_val.setText(str(pending))
        self._proj_tasks_inprog_val.setText(str(inprog))
        self._proj_tasks_done_val.setText(str(done))

        self._proj_flag_daily.setText("✔  Needs Daily Review" if p.needs_daily_review else "✘  Needs Daily Review")
        self._proj_flag_client.setText("✔  Client Delivery"   if p.client_delivery    else "✘  Client Delivery")
        self._proj_flag_hipri.setText("✔  High Priority"      if p.high_priority       else "✘  High Priority")

        self._export_proj_btn.setEnabled(True)

    def _clear_project_panel(self):
        for lbl in (self._proj_name_val, self._proj_supervisor_val, self._proj_dept_val,
                    self._proj_type_val, self._proj_created_val,
                    self._proj_tasks_total_val, self._proj_tasks_pending_val,
                    self._proj_tasks_inprog_val, self._proj_tasks_done_val):
            lbl.setText("—")
        for bar in (self._proj_priority_bar, self._proj_completion_bar, self._proj_timeline_bar):
            bar.setValue(0)
            bar.setFormat("")
        self._proj_flag_daily.setText("")
        self._proj_flag_client.setText("")
        self._proj_flag_hipri.setText("")

    # ──────────────────────────────────────────────────────────────────────
    # Export
    # ──────────────────────────────────────────────────────────────────────

    def _export_project_summary(self):
        project_id = self.project_combo.currentData()
        if not project_id:
            return
        p = self.data_manager.get_project_by_id(project_id)
        if not p:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Project Summary",
            f"{p.name.replace(' ', '_')}_summary.json",
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"

        total   = len(p.tasks)
        done    = sum(1 for t in p.tasks if t.status == "done")
        inprog  = sum(1 for t in p.tasks if t.status == "in-progress")
        pending = total - done - inprog

        data = {
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project": {
                "id": p.id, "name": p.name, "supervisor": p.supervisor_name,
                "department": p.department, "project_type": p.project_type,
                "created_date": p.created_date, "priority": p.priority,
                "timeline_offset": p.timeline_offset,
                "completion_pct": int((done / total) * 100) if total else 0,
                "flags": {
                    "high_priority": p.high_priority,
                    "client_delivery": p.client_delivery,
                    "needs_daily_review": p.needs_daily_review,
                },
                "notes": p.notes,
                "tasks": {
                    "total": total, "pending": pending,
                    "in_progress": inprog, "done": done,
                    "items": [
                        {"id": t.id, "name": t.name, "status": t.status,
                         "priority": t.priority, "created_date": t.created_date}
                        for t in p.tasks
                    ],
                },
            },
        }
        self._write_json(path, data)

    def _export_studio_summary(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Studio Summary", "studio_summary.json",
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"

        projects = self.data_manager.get_all_projects()
        assets   = self.data_manager.get_all_assets()
        stats    = self.data_manager.get_statistics()

        data = {
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "statistics": stats,
            "breakdown": {
                "by_type": {
                    "VFX":       sum(1 for p in projects if p.project_type == "VFX"),
                    "Animation": sum(1 for p in projects if p.project_type == "Animation"),
                    "Gaming":    sum(1 for p in projects if p.project_type == "Gaming"),
                },
                "by_department": {
                    "Rig":       sum(1 for p in projects if p.department == "Rig"),
                    "FX":        sum(1 for p in projects if p.department == "FX"),
                    "Animation": sum(1 for p in projects if p.department == "Animation"),
                    "Assets":    sum(1 for p in projects if p.department == "Assets"),
                },
                "flags": {
                    "high_priority":      sum(1 for p in projects if p.high_priority),
                    "client_delivery":    sum(1 for p in projects if p.client_delivery),
                    "needs_daily_review": sum(1 for p in projects if p.needs_daily_review),
                },
            },
            "projects": [
                {
                    "id": p.id, "name": p.name, "supervisor": p.supervisor_name,
                    "department": p.department, "project_type": p.project_type,
                    "priority": p.priority, "created_date": p.created_date,
                    "task_count": len(p.tasks),
                    "tasks_done": sum(1 for t in p.tasks if t.status == "done"),
                }
                for p in projects
            ],
            "assets": [
                {"id": a.id, "name": a.name, "type": a.asset_type, "created_date": a.created_date}
                for a in assets
            ],
        }
        self._write_json(path, data)

    def _write_json(self, path: str, data: dict):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            if self.parent_window:
                self.parent_window.statusBar().showMessage(f"Exported: {path}", 5000)
        except OSError as e:
            QMessageBox.critical(self, "Export Error", f"Could not write file:\n{e}")
