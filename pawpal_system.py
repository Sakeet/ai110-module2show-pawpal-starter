from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    id: str
    name: str
    category: str = "OTHER"
    duration: int = 0
    priority: str = "MEDIUM"
    preferred_time_window: Optional[str] = None
    frequency: str = "daily"
    is_time_sensitive: bool = False

    def conflicts_with(self, other_task: "Task") -> bool:
        pass

    def to_dict(self) -> Dict[str, Any]:
        pass

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: Optional[str] = None
    age: int = 0
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, task_id: str, **updates: Any) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass

    def get_tasks_by_category(self, category: str) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        pass


@dataclass
class Scheduler:
    available_time: int = 0
    tasks: List[Task] = field(default_factory=list)
    strategy: str = "priority-first"

    def generate_plan(self, pet: Pet, available_time: int) -> "DailyPlan":
        pass

    def _select_tasks(self, tasks: List[Task], available_time: int) -> List[Task]:
        pass

    def _order_tasks(self, selected_tasks: List[Task]) -> List[Task]:
        pass

    def explain_decision(self, task: Task, included: bool) -> str:
        pass


@dataclass
class DailyPlan:
    pet: Pet
    date: date = field(default_factory=date.today)
    scheduled_tasks: List[Task] = field(default_factory=list)
    dropped_tasks: List[Task] = field(default_factory=list)
    total_time_used: int = 0
    time_remaining: int = 0

    def summary(self) -> str:
        pass

    def explain(self) -> str:
        pass
