from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from pathlib import Path
import json
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
    status: str = "pending"
    pet_name: Optional[str] = None
    due_date: Optional[date] = None
    scheduled_start: Optional[int] = None
    scheduled_end: Optional[int] = None

    def conflicts_with(self, other_task: "Task") -> bool:
        """Return True if two tasks overlap in time."""
        if not self.preferred_time_window or not other_task.preferred_time_window:
            return False
        
        self_start, self_end = self.preferred_time_window
        other_start, other_end = other_task.preferred_time_window
        
        # Overlap if one doesn't end before the other starts
        return not (self_end <= other_start or other_end <= self_start)

    def mark_complete(self) -> Optional["Task"]:
        """Mark the task as completed and create the next occurrence for recurring tasks."""
        self.status = "completed"

        if self.frequency == Frequency.DAILY:
            return self._create_next_occurrence(days=1)
        if self.frequency == Frequency.WEEKLY:
            return self._create_next_occurrence(days=7)
        return None

    def _create_next_occurrence(self, days: int) -> "Task":
        """Create a new pending task for the next occurrence."""
        next_occurrence = Task(
            id=f"{self.id}-next",
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            preferred_time_window=self.preferred_time_window,
            frequency=self.frequency,
            is_time_sensitive=self.is_time_sensitive,
            status="pending",
            pet_name=self.pet_name,
            due_date=(self.due_date or date.today()) + timedelta(days=days),
        )
        return next_occurrence

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "duration": self.duration,
            "priority": self.priority.value,
            "preferred_time_window": self.preferred_time_window,
            "frequency": self.frequency.value,
            "is_time_sensitive": self.is_time_sensitive,
            "status": self.status,
            "pet_name": self.pet_name,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "scheduled_start": self.scheduled_start,
            "scheduled_end": self.scheduled_end,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create a task from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            category=TaskCategory(data.get("category", "other")),
            duration=data.get("duration", 0),
            priority=Priority(data.get("priority", "medium")),
            preferred_time_window=data.get("preferred_time_window"),
            frequency=Frequency(data.get("frequency", "daily")),
            is_time_sensitive=data.get("is_time_sensitive", False),
            status=data.get("status", "pending"),
            pet_name=data.get("pet_name"),
            due_date=date.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            scheduled_start=data.get("scheduled_start"),
            scheduled_end=data.get("scheduled_end"),
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
        """Add a task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, task_id: str, **updates: Any) -> None:
        """Update a task by ID using keyword values."""
        for task in self.tasks:
            if task.id == task_id:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                return
        raise ValueError(f"Task {task_id} not found")

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given ID."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Return tasks matching the given category."""
        return [t for t in self.tasks if t.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the pet to a dictionary."""
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
        """Create a pet from a dictionary."""
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
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        self.pets = [p for p in self.pets if p.name != pet.name]

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return the pet with the given name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across this owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_all_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Return tasks of the given category across this owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks_by_category(category))
        return all_tasks

    def to_dict(self) -> Dict[str, Any]:
        """Convert the owner to a dictionary."""
        return {
            "name": self.name,
            "pets": [p.to_dict() for p in self.pets],
            "preferences": self.preferences,
        }

    def save_to_file(self, path: Path | str) -> None:
        """Save the owner and all pets/tasks to a JSON file."""
        path = Path(path)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_file(cls, path: Path | str) -> "Owner":
        """Load the owner and all pets/tasks from a JSON file."""
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Owner":
        """Create an owner from a dictionary."""
        pets = [Pet.from_dict(p) for p in data.get("pets", [])]
        return cls(
            name=data["name"],
            pets=pets,
            preferences=data.get("preferences", {}),
        )


@dataclass
class Scheduler:
    available_time: int = 0
    tasks: List[Task] = field(default_factory=list)
    strategy: str = "priority-first"

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by their preferred start time, then by name as a fallback."""
        return sorted(
            tasks,
            key=lambda task: (
                task.preferred_time_window[0] if task.preferred_time_window else 9999,
                task.preferred_time_window[1] if task.preferred_time_window else 9999,
                task.name,
            ),
        )

    def filter_tasks(self, tasks: List[Task], status: Optional[str] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return tasks that match the requested completion status and/or pet name."""
        filtered_tasks: List[Task] = []
        for task in tasks:
            if status is not None and task.status != status:
                continue
            if pet_name is not None and not self._task_belongs_to_pet(task, pet_name):
                continue
            filtered_tasks.append(task)
        return filtered_tasks

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return warning messages when two tasks overlap in the same time window."""
        warnings: List[str] = []
        for index, task in enumerate(tasks):
            if not task.preferred_time_window:
                continue
            for other in tasks[index + 1 :]:
                if not other.preferred_time_window:
                    continue
                if task.conflicts_with(other):
                    pet_names = ", ".join(filter(None, [task.pet_name, other.pet_name])) or "unknown"
                    warnings.append(
                        f"Warning: '{task.name}' and '{other.name}' overlap for {pet_names} at the same time."
                    )
        return warnings

    def _task_belongs_to_pet(self, task: Task, pet_name: str) -> bool:
        """Return True when the task is associated with the named pet."""
        return task.pet_name == pet_name

    def get_all_tasks_for_owner(self, owner: Owner) -> List[Task]:
        """Return all tasks from an owner's pets."""
        return owner.get_all_tasks()

    def generate_plan(self, pet: Pet, available_time: int) -> "DailyPlan":
        """Create a daily plan for one pet within the available time."""
        plan = DailyPlan(pet=pet, date=date.today())
        
        # Get all candidate tasks sorted by time first, then priority
        all_tasks = pet.get_tasks()
        priority_order = {Priority.MUST_DO: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        sorted_tasks = sorted(
            all_tasks,
            key=lambda t: (
                t.preferred_time_window[0] if t.preferred_time_window else 9999,
                priority_order.get(t.priority, 4),
                not t.is_time_sensitive,
                t.duration,
            ),
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
                t.preferred_time_window[0] if t.preferred_time_window else 9999,
                not t.is_time_sensitive,
                priority_order.get(t.priority, 4),
                t.preferred_time_window[1] if t.preferred_time_window else 9999,
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

    def generate_plans_for_owner(self, owner: Owner, available_time_per_pet: int) -> List[DailyPlan]:
        """Create a daily plan for each pet owned by the user."""
        plans = []
        for pet in owner.pets:
            plan = self.generate_plan(pet, available_time_per_pet)
            plans.append(plan)
        return plans

    def generate_time_blocked_plan(self, pet: Pet, available_time: int) -> "DailyPlan":
        """Generate a plan that assigns tasks to non-overlapping preferred time slots."""
        plan = DailyPlan(pet=pet, date=date.today())
        priority_order = {Priority.MUST_DO: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        candidate_tasks = sorted(
            pet.get_tasks(),
            key=lambda t: (
                t.preferred_time_window[0] if t.preferred_time_window else 9999,
                priority_order.get(t.priority, 4),
                not t.is_time_sensitive,
                t.duration,
            ),
        )

        scheduled: List[Task] = []
        time_used = 0

        for task in candidate_tasks:
            if task.preferred_time_window is None:
                continue

            start_window, end_window = task.preferred_time_window
            candidate_start = start_window
            for existing in scheduled:
                if existing.scheduled_start is None or existing.scheduled_end is None:
                    continue
                if not (candidate_start + task.duration <= existing.scheduled_start or candidate_start >= existing.scheduled_end):
                    candidate_start = existing.scheduled_end

            if candidate_start + task.duration <= end_window and time_used + task.duration <= available_time:
                task.scheduled_start = candidate_start
                task.scheduled_end = candidate_start + task.duration
                plan.scheduled_tasks.append(task)
                scheduled.append(task)
                scheduled.sort(key=lambda t: t.scheduled_start)
                time_used += task.duration

        for task in pet.get_tasks():
            if task not in plan.scheduled_tasks:
                reason = self.explain_decision(task, included=False)
                plan.dropped_tasks.append({"task": task, "reason": reason})

        plan.total_time_used = time_used
        plan.time_remaining = available_time - time_used
        return plan

    def generate_combined_plan(self, owner: Owner, total_available_time: int) -> Dict[str, Any]:
        """Create a combined plan for all pets within a shared time limit."""
        all_tasks_with_pet = []
        for pet in owner.pets:
            for task in pet.get_tasks():
                all_tasks_with_pet.append((pet, task))
        
        # Sort by priority and time-sensitivity
        priority_order = {Priority.MUST_DO: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        all_tasks_with_pet.sort(
            key=lambda x: (priority_order.get(x[1].priority, 4), not x[1].is_time_sensitive, x[1].duration)
        )
        
        # Greedily allocate time
        time_used = 0
        included_task_ids = set()
        pet_to_plan = {pet.name: DailyPlan(pet=pet, date=date.today()) for pet in owner.pets}
        
        for pet, task in all_tasks_with_pet:
            if time_used + task.duration <= total_available_time:
                pet_to_plan[pet.name].scheduled_tasks.append(task)
                included_task_ids.add(task.id)
                time_used += task.duration
        
        # Assign dropped tasks to their respective plans
        for pet, task in all_tasks_with_pet:
            if task.id not in included_task_ids:
                reason = self.explain_decision(task, included=False)
                pet_to_plan[pet.name].dropped_tasks.append({"task": task, "reason": reason})
        
        # Update time totals for each plan
        for pet in owner.pets:
            plan = pet_to_plan[pet.name]
            plan.total_time_used = sum(t.duration for t in plan.scheduled_tasks)
            plan.time_remaining = total_available_time - plan.total_time_used
        
        return {
            "pet_plans": list(pet_to_plan.values()),
            "total_time_used": time_used,
            "total_time_available": total_available_time,
            "time_remaining": total_available_time - time_used,
        }

    def _select_tasks(self, tasks: List[Task], available_time: int) -> List[Task]:
        """Select tasks greedily by priority and urgency."""
        priority_order = {Priority.MUST_DO: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        candidates = sorted(
            tasks,
            key=lambda t: (priority_order.get(t.priority, 4), not t.is_time_sensitive, t.duration)
        )
        
        selected = []
        time_used = 0
        for task in candidates:
            if time_used + task.duration <= available_time:
                selected.append(task)
                time_used += task.duration
        
        return selected

    def _order_tasks(self, selected_tasks: List[Task]) -> List[Task]:
        """Order selected tasks by urgency and time window."""
        return sorted(
            selected_tasks,
            key=lambda t: (
                not t.is_time_sensitive,
                {Priority.MUST_DO: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}.get(t.priority, 4),
                t.preferred_time_window[0] if t.preferred_time_window else 999,
            )
        )

    def explain_decision(self, task: Task, included: bool) -> str:
        """Explain why a task was included or dropped."""
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
        """Return a readable summary of the plan."""
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
        """Return a short explanation of the plan decisions."""
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert the daily plan to a dictionary."""
        return {
            "pet": self.pet.to_dict(),
            "date": self.date.isoformat(),
            "scheduled_tasks": [t.to_dict() for t in self.scheduled_tasks],
            "dropped_tasks": [
                {"task": item["task"].to_dict(), "reason": item["reason"]}
                for item in self.dropped_tasks
            ],
            "total_time_used": self.total_time_used,
            "time_remaining": self.time_remaining,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DailyPlan":
        """Create a daily plan from a dictionary."""
        pet = Pet.from_dict(data["pet"])
        scheduled = [Task.from_dict(t) for t in data.get("scheduled_tasks", [])]
        dropped = [
            {"task": Task.from_dict(item["task"]), "reason": item["reason"]}
            for item in data.get("dropped_tasks", [])
        ]
        
        return cls(
            pet=pet,
            date=date.fromisoformat(data.get("date", date.today().isoformat())),
            scheduled_tasks=scheduled,
            dropped_tasks=dropped,
            total_time_used=data.get("total_time_used", 0),
            time_remaining=data.get("time_remaining", 0),
        )
