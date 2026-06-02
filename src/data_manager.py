"""Data persistence manager — projects in one file, assets/shots in another"""

import json
import os
from typing import Dict, List
import uuid

from src.models.data_models import Project, Task, Asset, Shot
from src.constants import PROJECTS_FILE, ASSETS_SHOTS_FILE, DEFAULT_SHOTS

# Resolve data paths relative to this file (src/) so they work regardless of CWD
_SRC_DIR = os.path.dirname(__file__)
_DEFAULT_PROJECTS_FILE     = os.path.join(_SRC_DIR, PROJECTS_FILE)
_DEFAULT_ASSETS_SHOTS_FILE = os.path.join(_SRC_DIR, ASSETS_SHOTS_FILE)


class DataManager:
    """Handles all data persistence.

    Projects are stored in Project.json and exposed via open/save dialogs.
    Assets and shots are stored in production.json, managed internally.
    """

    def __init__(self,
                 projects_file: str = _DEFAULT_PROJECTS_FILE,
                 assets_shots_file: str = _DEFAULT_ASSETS_SHOTS_FILE):
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

    def _load_json(self, filepath: str) -> dict | None:
        """Read a JSON file and return its contents, or None on any failure."""
        self._ensure_dir(filepath)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print(f"Could not read {filepath}, starting fresh.")
        return None

    def _load_projects(self) -> Dict:
        return self._load_json(self.projects_file) or {"projects": []}

    def _load_static(self) -> Dict:
        data = self._load_json(self.assets_shots_file)
        if data is None:
            data = {"assets": [], "shots": list(DEFAULT_SHOTS)}
            self._write_json(self.assets_shots_file, data)
        elif "shots" not in data:
            data["shots"] = list(DEFAULT_SHOTS)
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
            id=f"proj_{uuid.uuid4().hex[:4]}",
            name=name, supervisor_name=supervisor_name, department=department,
            project_type=project_type, needs_daily_review=needs_daily_review,
            client_delivery=client_delivery, high_priority=high_priority,
            priority=priority, timeline_offset=timeline_offset,
            completion=completion, notes=notes,
        )
        self._projects_data.setdefault("projects", []).append(project.to_dict())
        self._write_json(self.projects_file, self._projects_data)
        return project

    def update_project(self, project: Project):
        for i, p in enumerate(self._projects_data.get("projects", [])):
            if p.get("id") == project.id:
                self._projects_data["projects"][i] = project.to_dict()
                self._write_json(self.projects_file, self._projects_data)
                return

    def delete_project(self, project_id: str):
        self._projects_data["projects"] = [
            p for p in self._projects_data.get("projects", [])
            if p.get("id") != project_id
        ]
        self._write_json(self.projects_file, self._projects_data)

    # ──────────────────────────────────────────────────────────────────────
    # Task methods
    # ──────────────────────────────────────────────────────────────────────

    def create_task(self, project_id: str, task_name: str) -> Task:
        project = self.get_project_by_id(project_id)
        if not project:
            return None
        task = Task(id=f"task_{uuid.uuid4().hex[:4]}", name=task_name)
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
    # Asset methods
    # ──────────────────────────────────────────────────────────────────────

    def get_all_assets(self) -> List[Asset]:
        return [Asset.from_dict(a) for a in self._static_data.get("assets", [])]

    def create_asset(self, name: str, asset_type: str = "model") -> Asset:
        asset = Asset(id=f"asset_{uuid.uuid4().hex[:4]}", name=name, asset_type=asset_type)
        self._static_data.setdefault("assets", []).append(asset.to_dict())
        self._write_json(self.assets_shots_file, self._static_data)
        return asset

    def update_asset(self, asset: Asset):
        for i, a in enumerate(self._static_data.get("assets", [])):
            if a.get("id") == asset.id:
                self._static_data["assets"][i] = asset.to_dict()
                self._write_json(self.assets_shots_file, self._static_data)
                return

    def delete_asset(self, asset_id: str):
        self._static_data["assets"] = [
            a for a in self._static_data.get("assets", [])
            if a.get("id") != asset_id
        ]
        self._write_json(self.assets_shots_file, self._static_data)

    # ──────────────────────────────────────────────────────────────────────
    # Shot methods
    # ──────────────────────────────────────────────────────────────────────

    def get_all_shots(self) -> List[Shot]:
        return [Shot.from_dict(s) for s in self._static_data.get("shots", [])]

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
