"""Data persistence manager using JSON"""

import json
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import uuid

from src.models.data_models import Project, Task, Asset, Shot


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
    """Handles all data persistence operations with JSON"""

    def __init__(self, data_file: str = "data/pipeline_data.json"):
        """Initialize data manager with JSON file path"""
        self.data_file = data_file
        self.data = self._load_or_create()
    
    def _get_data_dir(self):
        """Get data directory, create if needed"""
        data_dir = os.path.dirname(self.data_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def _load_or_create(self) -> Dict:
        """Load data from JSON or create blank structure if file doesn't exist"""
        self._get_data_dir()
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Migrate older files that lack the shots key
                if "shots" not in data:
                    data["shots"] = list(_DEFAULT_SHOTS)
                    self._save_data(data)
                return data
            except (json.JSONDecodeError, IOError):
                print(f"Error reading {self.data_file}, creating new file")
        
        # Create blank data structure
        blank_data = {
            "projects": [],
            "assets": [],
            "shots": list(_DEFAULT_SHOTS),
        }
        self._save_data(blank_data)
        return blank_data
    
    def _save_data(self, data: Dict = None):
        """Save data to JSON file"""
        if data is None:
            data = self.data
        
        self._get_data_dir()
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving to {self.data_file}: {e}")
    
    def save(self):
        """Save current data to file"""
        self._save_data()

    def load_from_file(self, path: str) -> bool:
        """Replace in-memory data with contents of an arbitrary JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.data = data
            self.data_file = path
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {path}: {e}")
            return False

    def save_to_file(self, path: str) -> bool:
        """Write current in-memory data to an arbitrary file path."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving to {path}: {e}")
            return False
    
    # ==================== PROJECT METHODS ====================
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        projects = []
        for proj_data in self.data.get("projects", []):
            projects.append(Project.from_dict(proj_data))
        return projects
    
    def get_project_by_id(self, project_id: str) -> Project:
        """Get a specific project by ID"""
        for proj_data in self.data.get("projects", []):
            if proj_data.get("id") == project_id:
                return Project.from_dict(proj_data)
        return None
    
    def create_project(self, name: str, supervisor_name: str = "", department: str = "Rig",
                      project_type: str = "VFX", needs_daily_review: bool = False,
                      client_delivery: bool = False, high_priority: bool = False,
                      priority: int = 50, timeline_offset: int = 25,
                      completion: int = 0, notes: str = "") -> Project:
        """Create a new project"""
        project_id = f"proj_{uuid.uuid4().hex[:8]}"
        project = Project(
            id=project_id,
            name=name,
            supervisor_name=supervisor_name,
            department=department,
            project_type=project_type,
            needs_daily_review=needs_daily_review,
            client_delivery=client_delivery,
            high_priority=high_priority,
            priority=priority,
            timeline_offset=timeline_offset,
            completion=completion,
            notes=notes,
        )
        self.data["projects"].append(project.to_dict())
        self.save()
        return project
    
    def update_project(self, project: Project):
        """Update an existing project"""
        for i, proj_data in enumerate(self.data.get("projects", [])):
            if proj_data.get("id") == project.id:
                self.data["projects"][i] = project.to_dict()
                self.save()
                return
    
    def delete_project(self, project_id: str):
        """Delete a project by ID"""
        self.data["projects"] = [
            p for p in self.data.get("projects", [])
            if p.get("id") != project_id
        ]
        self.save()
    
    # ==================== TASK METHODS ====================
    
    def get_tasks_for_project(self, project_id: str) -> List[Task]:
        """Get all tasks for a specific project"""
        project = self.get_project_by_id(project_id)
        if project:
            return project.tasks
        return []
    
    def create_task(self, project_id: str, task_name: str) -> Task:
        """Create a new task in a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return None
        
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = Task(id=task_id, name=task_name)
        project.tasks.append(task)
        self.update_project(project)
        return task
    
    def update_task(self, project_id: str, task: Task):
        """Update a task in a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return
        
        for i, t in enumerate(project.tasks):
            if t.id == task.id:
                project.tasks[i] = task
                self.update_project(project)
                return
    
    def delete_task(self, project_id: str, task_id: str):
        """Delete a task from a project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return
        
        project.tasks = [t for t in project.tasks if t.id != task_id]
        self.update_project(project)
    
    # ==================== ASSET METHODS ====================
    
    def get_all_assets(self) -> List[Asset]:
        """Get all assets"""
        assets = []
        for asset_data in self.data.get("assets", []):
            assets.append(Asset.from_dict(asset_data))
        return assets
    
    def get_asset_by_id(self, asset_id: str) -> Asset:
        """Get a specific asset by ID"""
        for asset_data in self.data.get("assets", []):
            if asset_data.get("id") == asset_id:
                return Asset.from_dict(asset_data)
        return None
    
    def create_asset(self, name: str, asset_type: str = "model") -> Asset:
        """Create a new asset"""
        asset_id = f"asset_{uuid.uuid4().hex[:8]}"
        asset = Asset(id=asset_id, name=name, asset_type=asset_type)
        self.data["assets"].append(asset.to_dict())
        self.save()
        return asset
    
    def update_asset(self, asset: Asset):
        """Update an existing asset"""
        for i, asset_data in enumerate(self.data.get("assets", [])):
            if asset_data.get("id") == asset.id:
                self.data["assets"][i] = asset.to_dict()
                self.save()
                return
    
    def delete_asset(self, asset_id: str):
        """Delete an asset by ID"""
        self.data["assets"] = [
            a for a in self.data.get("assets", [])
            if a.get("id") != asset_id
        ]
        self.save()
    
    # ==================== SHOT METHODS ====================

    def get_all_shots(self) -> List[Shot]:
        """Get all shots"""
        return [Shot.from_dict(s) for s in self.data.get("shots", [])]

    def create_shot(self, shot: str, department: str = "FX",
                    status: str = "Pending", due_date: str = "") -> Shot:
        """Create a new shot"""
        shot_id = f"shot_{uuid.uuid4().hex[:8]}"
        new_shot = Shot(id=shot_id, shot=shot, department=department,
                        status=status, due_date=due_date)
        self.data["shots"].append(new_shot.to_dict())
        self.save()
        return new_shot

    def update_shot(self, shot: Shot):
        """Update an existing shot"""
        for i, s in enumerate(self.data.get("shots", [])):
            if s.get("id") == shot.id:
                self.data["shots"][i] = shot.to_dict()
                self.save()
                return

    def delete_shot(self, shot_id: str):
        """Delete a shot by ID"""
        self.data["shots"] = [
            s for s in self.data.get("shots", [])
            if s.get("id") != shot_id
        ]
        self.save()

    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        projects = self.get_all_projects()
        assets = self.get_all_assets()
        
        total_tasks = sum(len(p.tasks) for p in projects)
        pending_tasks = sum(1 for p in projects for t in p.tasks if t.status == "pending")
        completed_tasks = sum(1 for p in projects for t in p.tasks if t.status == "done")
        
        return {
            "total_projects": len(projects),
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": total_tasks - pending_tasks - completed_tasks,
            "total_assets": len(assets)
        }
