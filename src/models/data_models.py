"""Data models for VFX Pipeline"""

from dataclasses import dataclass, field, asdict
from typing import List
from datetime import datetime

from src.constants import (
    DATE_FORMAT,
    DEFAULT_DEPARTMENT, DEFAULT_PROJECT_TYPE,
    DEFAULT_TASK_STATUS, DEFAULT_TASK_PRIORITY,
    DEFAULT_ASSET_TYPE,
    DEFAULT_SHOT_DEPARTMENT, DEFAULT_SHOT_STATUS,
    DEFAULT_PRIORITY, DEFAULT_TIMELINE_OFFSET, DEFAULT_COMPLETION,
)


@dataclass
class Task:
    """Task data model"""
    id: str
    name: str
    status: str = DEFAULT_TASK_STATUS
    priority: str = DEFAULT_TASK_PRIORITY
    created_date: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))

    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        """Create from dictionary"""
        return Task(
            id=data.get("id"),
            name=data.get("name"),
            status=data.get("status", DEFAULT_TASK_STATUS),
            priority=data.get("priority", DEFAULT_TASK_PRIORITY),
            created_date=data.get("created_date", datetime.now().strftime(DATE_FORMAT))
        )


@dataclass
class Project:
    """Project data model"""
    id: str
    name: str
    supervisor_name: str = ""
    department: str = DEFAULT_DEPARTMENT
    project_type: str = DEFAULT_PROJECT_TYPE
    needs_daily_review: bool = False
    client_delivery: bool = False
    high_priority: bool = False
    priority: int = DEFAULT_PRIORITY
    timeline_offset: int = DEFAULT_TIMELINE_OFFSET
    completion: int = DEFAULT_COMPLETION
    notes: str = ""
    created_date: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))
    tasks: List[Task] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "supervisor_name": self.supervisor_name,
            "department": self.department,
            "project_type": self.project_type,
            "needs_daily_review": self.needs_daily_review,
            "client_delivery": self.client_delivery,
            "high_priority": self.high_priority,
            "priority": self.priority,
            "timeline_offset": self.timeline_offset,
            "completion": self.completion,
            "notes": self.notes,
            "created_date": self.created_date,
            "tasks": [task.to_dict() for task in self.tasks]
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Create from dictionary"""
        tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        return Project(
            id=data.get("id"),
            name=data.get("name"),
            supervisor_name=data.get("supervisor_name", ""),
            department=data.get("department", DEFAULT_DEPARTMENT),
            project_type=data.get("project_type", DEFAULT_PROJECT_TYPE),
            needs_daily_review=data.get("needs_daily_review", False),
            client_delivery=data.get("client_delivery", False),
            high_priority=data.get("high_priority", False),
            priority=data.get("priority", DEFAULT_PRIORITY),
            timeline_offset=data.get("timeline_offset", DEFAULT_TIMELINE_OFFSET),
            completion=data.get("completion", DEFAULT_COMPLETION),
            notes=data.get("notes", ""),
            created_date=data.get("created_date", datetime.now().strftime(DATE_FORMAT)),
            tasks=tasks
        )


@dataclass
class Asset:
    """Asset data model"""
    id: str
    name: str
    asset_type: str = DEFAULT_ASSET_TYPE
    created_date: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.asset_type,
            "created_date": self.created_date
        }

    @staticmethod
    def from_dict(data: dict):
        """Create from dictionary"""
        return Asset(
            id=data.get("id"),
            name=data.get("name"),
            asset_type=data.get("type", DEFAULT_ASSET_TYPE),
            created_date=data.get("created_date", datetime.now().strftime(DATE_FORMAT))
        )


@dataclass
class Shot:
    """Shot tracking data model"""
    id: str
    shot: str
    department: str = DEFAULT_SHOT_DEPARTMENT
    status: str = DEFAULT_SHOT_STATUS
    due_date: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "shot": self.shot,
            "department": self.department,
            "status": self.status,
            "due_date": self.due_date,
        }

    @staticmethod
    def from_dict(data: dict):
        return Shot(
            id=data.get("id", ""),
            shot=data.get("shot", ""),
            department=data.get("department", DEFAULT_SHOT_DEPARTMENT),
            status=data.get("status", DEFAULT_SHOT_STATUS),
            due_date=data.get("due_date", ""),
        )
