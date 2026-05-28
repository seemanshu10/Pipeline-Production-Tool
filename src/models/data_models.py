"""Data models for VFX Pipeline"""

from dataclasses import dataclass, field, asdict
from typing import List
from datetime import datetime


@dataclass
class Task:
    """Task data model"""
    id: str
    name: str
    status: str = "pending"  # pending, in-progress, done
    priority: str = "medium"  # low, medium, high
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict):
        """Create from dictionary"""
        return Task(
            id=data.get("id"),
            name=data.get("name"),
            status=data.get("status", "pending"),
            priority=data.get("priority", "medium"),
            created_date=data.get("created_date", datetime.now().strftime("%Y-%m-%d"))
        )


@dataclass
class Project:
    """Project data model"""
    id: str
    name: str
    supervisor_name: str = ""
    department: str = "Rig"  # Rig, FX, Animation, Assets
    project_type: str = "VFX"  # Animation, VFX, Gaming
    needs_daily_review: bool = False
    client_delivery: bool = False
    high_priority: bool = False
    priority: int = 50
    timeline_offset: int = 25
    completion: int = 25
    notes: str = ""
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
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
            department=data.get("department", "Rig"),
            project_type=data.get("project_type", "VFX"),
            needs_daily_review=data.get("needs_daily_review", False),
            client_delivery=data.get("client_delivery", False),
            high_priority=data.get("high_priority", False),
            priority=data.get("priority", 50),
            timeline_offset=data.get("timeline_offset", 25),
            completion=data.get("completion", 25),
            notes=data.get("notes", ""),
            created_date=data.get("created_date", datetime.now().strftime("%Y-%m-%d")),
            tasks=tasks
        )


@dataclass
class Asset:
    """Asset data model"""
    id: str
    name: str
    asset_type: str = "model"  # model, texture, animation, etc.
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    
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
            asset_type=data.get("type", "model"),
            created_date=data.get("created_date", datetime.now().strftime("%Y-%m-%d"))
        )
