from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TaskCategory(str, Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"
    OTHER = "other"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MUST_DO = "must_do"


class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ONE_OFF = "one_off"


@dataclass
class Task:
    id: str
    name: str
    category: TaskCategory = TaskCategory.OTHER
    duration: int = 0  # minutes
    priority: Priority = Priority.MEDIUM
    preferred_time_window: Optional[Tuple[int, int]] = None  # (start_minute, end_minute) from midnight
    frequency: Frequency = Frequency.DAILY
    is_time_sensitive: bool = False

    def conflicts_with(self, other_task: "Task") -> bool:
        """Check if this task's time window overlaps with another task's."""
        if not self.preferred_time_window or not other_task.preferred_time_window:
            return False
        
        self_start, self_end = self.preferred_time_window
        other_start, other_end = other_task.preferred_time_window
        
        # Overlap if one doesn't end before the other starts
        return not (self_end <= other_start or other_end <= self_start)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to dict."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "duration": self.duration,
            "priority": self.priority.value,
            "preferred_time_window": self.preferred_time_window,
            "frequency": self.frequency.value,
            "is_time_sensitive": self.is_time_sensitive,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialize task from dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            category=TaskCategory(data.get("category", "other")),
            duration=data.get("duration", 0),
            priority=Priority(data.get("priority", "medium")),
            preferred_time_window=data.get("preferred_time_window"),
            frequency=Frequency(data.get("frequency", "daily")),
            is_time_sensitive=data.get("is_time_sensitive", False),
        )


@dataclass
class Pet:
    name: str
    species: str
    breed: Optional[str] = None
    age: int = 0
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def edit_task(self, task_id: str, **updates: Any) -> None:
        """Edit a task by id with keyword arguments."""
        for task in self.tasks:
            if task.id == task_id:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                return
        raise ValueError(f"Task {task_id} not found")

    def remove_task(self, task_id: str) -> None:
        """Remove a task by id."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Return tasks filtered by category."""
        return [t for t in self.tasks if t.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize pet to dict."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age": self.age,
            "notes": self.notes,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pet":
        """Deserialize pet from dict."""
        tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return cls(
            name=data["name"],
            species=data["species"],
            breed=data.get("breed"),
            age=data.get("age", 0),
            notes=data.get("notes", ""),
            tasks=tasks,
        )


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's pet list."""
        self.pets = [p for p in self.pets if p.name != pet.name]

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Retrieve a pet by name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None


@dataclass
class Scheduler:
    available_time: int = 0
    tasks: List[Task] = field(default_factory=list)
    strategy: str = "priority-first"

    def generate_plan(self, pet: Pet, available_time: int) -> "DailyPlan":
        """Generate a daily plan for a pet given available time in minutes."""
        plan = DailyPlan(pet=pet, date=date.today())
        
        # Get all candidate tasks sorted by priority
        all_tasks = pet.get_tasks()
        priority_order = {Priority.MUST_DO: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        sorted_tasks = sorted(
            all_tasks,
            key=lambda t: (priority_order.get(t.priority, 4), not t.is_time_sensitive, t.duration)
        )
        
        # Greedily fit tasks into available time
        time_used = 0
        included_ids = set()
        for task in sorted_tasks:
            if time_used + task.duration <= available_time:
                plan.scheduled_tasks.append(task)
                included_ids.add(task.id)
                time_used += task.duration
        
        # Order scheduled tasks
        plan.scheduled_tasks.sort(
            key=lambda t: (
                not t.is_time_sensitive,
                priority_order.get(t.priority, 4),
                t.preferred_time_window[0] if t.preferred_time_window else 999,
            )
        )
        
        # Track dropped tasks with reasons
        for task in all_tasks:
            if task.id not in included_ids:
                reason = self.explain_decision(task, included=False)
                plan.dropped_tasks.append({"task": task, "reason": reason})
        
        plan.total_time_used = time_used
        plan.time_remaining = available_time - time_used
        return plan

    def _select_tasks(self, tasks: List[Task], available_time: int) -> List[Task]:
        """Select candidate tasks using a greedy priority-based approach."""
        # Filter and sort: MUST_DO first, then by priority level, then by time-sensitive flag
        priority_order = {Priority.MUST_DO: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        candidates = sorted(
            tasks,
            key=lambda t: (priority_order.get(t.priority, 4), not t.is_time_sensitive, t.duration)
        )
        
        # Greedy: include tasks that fit
        selected = []
        time_used = 0
        for task in candidates:
            if time_used + task.duration <= available_time:
                selected.append(task)
                time_used += task.duration
        
        return selected

    def _order_tasks(self, selected_tasks: List[Task]) -> List[Task]:
        """Order tasks: time-sensitive first, then by priority, then by start time."""
        return sorted(
            selected_tasks,
            key=lambda t: (
                not t.is_time_sensitive,  # time-sensitive tasks first
                {Priority.MUST_DO: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}.get(t.priority, 4),
                t.preferred_time_window[0] if t.preferred_time_window else 999,  # earliest preferred time
            )
        )

    def explain_decision(self, task: Task, included: bool) -> str:
        """Generate a human-readable explanation for including or excluding a task."""
        if included:
            return f"Included '{task.name}' (priority: {task.priority.value}, duration: {task.duration}min)"
        else:
            return f"Dropped '{task.name}' — not enough time remaining"


@dataclass
class DailyPlan:
    pet: Pet
    date: date = field(default_factory=date.today)
    scheduled_tasks: List[Task] = field(default_factory=list)
    dropped_tasks: List[Dict[str, Any]] = field(default_factory=list)  # {"task": Task, "reason": str}
    total_time_used: int = 0
    time_remaining: int = 0

    def summary(self) -> str:
        """Return a human-readable summary of the plan."""
        lines = [
            f"Daily Plan for {self.pet.name} ({self.date})",
            f"Available time: {self.total_time_used + self.time_remaining} minutes",
            f"Scheduled: {len(self.scheduled_tasks)} task(s), {self.total_time_used} minutes",
            f"Dropped: {len(self.dropped_tasks)} task(s)",
            f"Time remaining: {self.time_remaining} minutes",
            "",
            "Scheduled tasks:",
        ]
        for task in self.scheduled_tasks:
            lines.append(f"  • {task.name} ({task.duration}min, {task.priority.value})")
        
        if self.dropped_tasks:
            lines.append("")
            lines.append("Dropped tasks:")
            for item in self.dropped_tasks:
                task = item["task"]
                reason = item["reason"]
                lines.append(f"  • {task.name} ({task.duration}min) — {reason}")
        
        return "\n".join(lines)

    def explain(self) -> str:
        """Return detailed reasoning for all decisions."""
        lines = [f"Explanation for {self.pet.name}'s plan ({self.date}):", ""]
        
        lines.append("Included tasks:")
        if self.scheduled_tasks:
            for task in self.scheduled_tasks:
                lines.append(f"  ✓ {task.name}: priority={task.priority.value}, duration={task.duration}min, time-sensitive={task.is_time_sensitive}")
        else:
            lines.append("  (none)")
        
        lines.append("")
        lines.append("Excluded tasks:")
        if self.dropped_tasks:
            for item in self.dropped_tasks:
                task = item["task"]
                reason = item["reason"]
                lines.append(f"  ✗ {task.name}: {reason}")
        else:
            lines.append("  (none)")
        
        return "\n".join(lines)
