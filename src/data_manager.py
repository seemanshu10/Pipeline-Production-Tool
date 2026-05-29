"""Data persistence manager — projects in one file, assets/shots in another"""

import json
import os
from typing import Dict, List
import uuid

from src.models.data_models import Project, Task, Asset, Shot


_PROJECTS_FILE     = "data/Project.json"
_ASSETS_SHOTS_FILE = "data/production.json"

_DEFAULT_SHOTS = [
    {"id": "shot_001", "shot": "SH010", "department": "FX",        "status": "In Progress", "due_date": "2026-06-15"},
    {"id": "shot_002", "shot": "SH020", "department": "Rig",        "status": "Pending",     "due_date": "2026-06-20"},
    {"id": "shot_003", "shot": "SH030", "department": "Animation",  "status": "Done",        "due_date": "2026-05-30"},
    {"id": "shot_004", "shot": "SH040", "department": "Assets",     "status": "Pending",     "due_date": "2026-07-01"},
    {"id": "shot_005", "shot": "SH050", "department": "FX",         "status": "In Progress", "due_date": "2026-06-28"},
    {"id": "shot_006", "shot": "SH060", "department": "Animation",  "status": "Pending",     "due_date": "2026-07-10"},
    {"id": "shot_007", "shot": "SH070", "department": "Rig",        "status": "Done",        "due_date": "2026-05-25"},
]


class DataManager:
    """Handles all data persistence.

    Projects are stored in pipeline_projects.json and exposed via
    open/save dialogs so the user can manage them freely.

    Assets and shots are stored in pipeline_assets_shots.json which is
    managed internally by the app and never exposed to user file dialogs.
    """

    def __init__(self,
                 projects_file: str = _PROJECTS_FILE,
                 assets_shots_file: str = _ASSETS_SHOTS_FILE):
        self.projects_file     = projects_file
        self.assets_shots_file = assets_shots_file

        self._projects_data    = self._load_projects()
        self._static_data      = self._load_static()

    # ──────────────────────────────────────────────────────────────────────
    # Internal load / save helpers
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _ensure_dir(filepath: str):
        d = os.path.dirname(filepath)
        if d:
            os.makedirs(d, exist_ok=True)

    def _load_projects(self) -> Dict:
        self._ensure_dir(self.projects_file)
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print(f"Could not read {self.projects_file}, starting fresh.")
        return {"projects": []}

    def _load_static(self) -> Dict:
        self._ensure_dir(self.assets_shots_file)
        if os.path.exists(self.assets_shots_file):
            try:
                with open(self.assets_shots_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "shots" not in data:
                    data["shots"] = list(_DEFAULT_SHOTS)
                    self._write_json(self.assets_shots_file, data)
                return data
            except (json.JSONDecodeError, IOError):
                print(f"Could not read {self.assets_shots_file}, starting fresh.")
        data = {"assets": [], "shots": list(_DEFAULT_SHOTS)}
        self._write_json(self.assets_shots_file, data)
        return data

    @staticmethod
    def _write_json(filepath: str, data: Dict):
        DataManager._ensure_dir(filepath)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving {filepath}: {e}")

    def _save_projects(self):
        self._write_json(self.projects_file, self._projects_data)

    def _save_static(self):
        self._write_json(self.assets_shots_file, self._static_data)

    # ──────────────────────────────────────────────────────────────────────
    # User-facing file operations (projects only)
    # ──────────────────────────────────────────────────────────────────────

    def load_from_file(self, path: str) -> bool:
        """Replace in-memory projects with contents of a user-chosen JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._projects_data = data
            self.projects_file  = path
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {path}: {e}")
            return False

    def save_to_file(self, path: str) -> bool:
        """Write current projects to a user-chosen JSON file."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._projects_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving {path}: {e}")
            return False

    # ──────────────────────────────────────────────────────────────────────
    # Project methods
    # ──────────────────────────────────────────────────────────────────────

    def get_all_projects(self) -> List[Project]:
        return [Project.from_dict(p) for p in self._projects_data.get("projects", [])]

    def get_project_by_id(self, project_id: str) -> Project:
        for p in self._projects_data.get("projects", []):
            if p.get("id") == project_id:
                return Project.from_dict(p)
        return None

    def create_project(self, name: str, supervisor_name: str = "",
                       department: str = "Rig", project_type: str = "VFX",
                       needs_daily_review: bool = False, client_delivery: bool = False,
                       high_priority: bool = False, priority: int = 50,
                       timeline_offset: int = 25, completion: int = 0,
                       notes: str = "") -> Project:
        project = Project(
            id=f"proj_{uuid.uuid4().hex[:8]}",
            name=name, supervisor_name=supervisor_name, department=department,
            project_type=project_type, needs_daily_review=needs_daily_review,
            client_delivery=client_delivery, high_priority=high_priority,
            priority=priority, timeline_offset=timeline_offset,
            completion=completion, notes=notes,
        )
        self._projects_data.setdefault("projects", []).append(project.to_dict())
        self._save_projects()
        return project

    def update_project(self, project: Project):
        for i, p in enumerate(self._projects_data.get("projects", [])):
            if p.get("id") == project.id:
                self._projects_data["projects"][i] = project.to_dict()
                self._save_projects()
                return

    def delete_project(self, project_id: str):
        self._projects_data["projects"] = [
            p for p in self._projects_data.get("projects", [])
            if p.get("id") != project_id
        ]
        self._save_projects()

    # ──────────────────────────────────────────────────────────────────────
    # Task methods
    # ──────────────────────────────────────────────────────────────────────

    def get_tasks_for_project(self, project_id: str) -> List[Task]:
        project = self.get_project_by_id(project_id)
        return project.tasks if project else []

    def create_task(self, project_id: str, task_name: str) -> Task:
        project = self.get_project_by_id(project_id)
        if not project:
            return None
        task = Task(id=f"task_{uuid.uuid4().hex[:8]}", name=task_name)
        project.tasks.append(task)
        self.update_project(project)
        return task

    def update_task(self, project_id: str, task: Task):
        project = self.get_project_by_id(project_id)
        if not project:
            return
        for i, t in enumerate(project.tasks):
            if t.id == task.id:
                project.tasks[i] = task
                self.update_project(project)
                return

    def delete_task(self, project_id: str, task_id: str):
        project = self.get_project_by_id(project_id)
        if not project:
            return
        project.tasks = [t for t in project.tasks if t.id != task_id]
        self.update_project(project)

    # ──────────────────────────────────────────────────────────────────────
    # Asset methods  (saved to assets/shots file)
    # ──────────────────────────────────────────────────────────────────────

    def get_all_assets(self) -> List[Asset]:
        return [Asset.from_dict(a) for a in self._static_data.get("assets", [])]

    def get_asset_by_id(self, asset_id: str) -> Asset:
        for a in self._static_data.get("assets", []):
            if a.get("id") == asset_id:
                return Asset.from_dict(a)
        return None

    def create_asset(self, name: str, asset_type: str = "model") -> Asset:
        asset = Asset(id=f"asset_{uuid.uuid4().hex[:8]}", name=name, asset_type=asset_type)
        self._static_data.setdefault("assets", []).append(asset.to_dict())
        self._save_static()
        return asset

    def update_asset(self, asset: Asset):
        for i, a in enumerate(self._static_data.get("assets", [])):
            if a.get("id") == asset.id:
                self._static_data["assets"][i] = asset.to_dict()
                self._save_static()
                return

    def delete_asset(self, asset_id: str):
        self._static_data["assets"] = [
            a for a in self._static_data.get("assets", [])
            if a.get("id") != asset_id
        ]
        self._save_static()

    # ──────────────────────────────────────────────────────────────────────
    # Shot methods  (saved to assets/shots file)
    # ──────────────────────────────────────────────────────────────────────

    def get_all_shots(self) -> List[Shot]:
        return [Shot.from_dict(s) for s in self._static_data.get("shots", [])]

    def create_shot(self, shot: str, department: str = "FX",
                    status: str = "Pending", due_date: str = "") -> Shot:
        new_shot = Shot(id=f"shot_{uuid.uuid4().hex[:8]}", shot=shot,
                        department=department, status=status, due_date=due_date)
        self._static_data.setdefault("shots", []).append(new_shot.to_dict())
        self._save_static()
        return new_shot

    def update_shot(self, shot: Shot):
        for i, s in enumerate(self._static_data.get("shots", [])):
            if s.get("id") == shot.id:
                self._static_data["shots"][i] = shot.to_dict()
                self._save_static()
                return

    def delete_shot(self, shot_id: str):
        self._static_data["shots"] = [
            s for s in self._static_data.get("shots", [])
            if s.get("id") != shot_id
        ]
        self._save_static()

    # ──────────────────────────────────────────────────────────────────────
    # Statistics
    # ──────────────────────────────────────────────────────────────────────

    def get_statistics(self) -> Dict:
        projects    = self.get_all_projects()
        assets      = self.get_all_assets()
        total_tasks = sum(len(p.tasks) for p in projects)
        pending     = sum(1 for p in projects for t in p.tasks if t.status == "pending")
        completed   = sum(1 for p in projects for t in p.tasks if t.status == "done")
        return {
            "total_projects":    len(projects),
            "total_tasks":       total_tasks,
            "pending_tasks":     pending,
            "completed_tasks":   completed,
            "in_progress_tasks": total_tasks - pending - completed,
            "total_assets":      len(assets),
        }
