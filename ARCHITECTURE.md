# PawPal+ System Architecture

## Overview

PawPal+ is a multi-pet care planning system that helps owners organize and schedule tasks across their pets. The system is built around five core classes with a clear separation of concerns: **data classes** (Owner, Pet, Task) store information, and **process classes** (Scheduler, DailyPlan) handle decision-making and output.

## Core Classes

### 1. **Task** — The Atomic Unit of Care
Represents a single care activity (walk, feeding, medication, grooming, enrichment).

**Key Attributes:**
- `id` (unique identifier)
- `name` (descriptive label)
- `category` (enum: WALK, FEEDING, MEDS, ENRICHMENT, GROOMING, OTHER)
- `duration` (minutes)
- `priority` (enum: MUST_DO, HIGH, MEDIUM, LOW)
- `preferred_time_window` (optional tuple: (start_minute, end_minute) from midnight)
- `frequency` (enum: DAILY, WEEKLY, ONE_OFF)
- `is_time_sensitive` (bool — whether time window matters)

**Key Methods:**
- `conflicts_with(other_task)` → bool: Check if time windows overlap
- `to_dict()` / `from_dict()`: Serialization for persistence

---

### 2. **Pet** — Owns Tasks
Represents an individual animal and manages its list of care tasks.

**Key Attributes:**
- `name` (pet's name)
- `species` (dog, cat, rabbit, etc.)
- `breed`, `age`, `notes` (metadata)
- `tasks` (list of Task objects)

**Key Methods:**
- `add_task(task)`, `remove_task(task_id)`, `edit_task(task_id, **updates)`
- `get_tasks()` → all tasks for this pet
- `get_tasks_by_category(category)` → filtered tasks
- `to_dict()` / `from_dict()`: Full serialization with nested tasks

---

### 3. **Owner** — Manages Pets
Represents the app user who owns one or more pets.

**Key Attributes:**
- `name` (owner's name)
- `pets` (list of Pet objects)
- `preferences` (dict of owner preferences, e.g., timezone, notification style)

**Key Methods:**
- `add_pet(pet)`, `remove_pet(pet)`, `get_pet(pet_name)`
- **`get_all_tasks()`** → retrieves all tasks from all owned pets (flattened list)
- **`get_all_tasks_by_category(category)`** → cross-pet task filtering
- `to_dict()` / `from_dict()`: Full serialization (entire hierarchy)

---

### 4. **Scheduler** — The Planning Engine
The core decision-making class. Retrieves tasks and generates daily plans.

**Key Attributes:**
- `available_time` (total minutes available for planning)
- `tasks` (cached task list, optional)
- `strategy` (string flag for future algorithm variations)

**Key Methods:**

#### Core Planning Methods:
- **`generate_plan(pet, available_time)`** → DailyPlan
  - For a single pet, produces a schedule within available time
  - Uses greedy priority-based selection + ordering

- **`generate_plans_for_owner(owner, available_time_per_pet)`** → List[DailyPlan]
  - Generates individual plans for each pet in the owner's collection
  - Each pet gets its own time budget
  - Returns plans in the same order as owner.pets

- **`generate_combined_plan(owner, total_available_time)`** → Dict
  - Allocates a single time budget across all pets
  - Prioritizes tasks globally (not per-pet)
  - Useful when planning one block of pet care time

#### Task Retrieval:
- **`get_all_tasks_for_owner(owner)`** → List[Task]
  - Calls `owner.get_all_tasks()` internally
  - Returns flattened list of all tasks across all owner's pets
  - This is the primary pattern for multi-pet scheduling

#### Helper Methods:
- `_select_tasks(tasks, available_time)` → List[Task]
  - Greedy selection: MUST_DO priority first, then HIGH, MEDIUM, LOW
  - Time-sensitive tasks sorted before non-time-sensitive
  - Packs tasks into available time

- `_order_tasks(selected_tasks)` → List[Task]
  - Sorts scheduled tasks for optimal execution
  - Time-sensitive first, then by priority, then by earliest start time

- `explain_decision(task, included: bool)` → str
  - Generates human-readable reasoning for each task decision

---

### 5. **DailyPlan** — The Output Object
Represents the finalized schedule for one pet on one day.

**Key Attributes:**
- `pet` (which pet this plan is for)
- `date` (plan date)
- `scheduled_tasks` (list of Task objects that made the cut)
- `dropped_tasks` (list of dicts: `{"task": Task, "reason": str}`)
- `total_time_used` (minutes allocated)
- `time_remaining` (unused minutes)

**Key Methods:**
- `summary()` → str: Human-readable plan overview
- `explain()` → str: Detailed reasoning trail for each task
- `to_dict()` / `from_dict()`: Full serialization with nested objects

---

## How the Scheduler Retrieves All Tasks from an Owner

The pattern is simple and clean:

```python
# In Scheduler class:
def get_all_tasks_for_owner(self, owner: Owner) -> List[Task]:
    """Retrieve all tasks from all of an owner's pets."""
    return owner.get_all_tasks()

# Which calls in Owner class:
def get_all_tasks(self) -> List[Task]:
    """Retrieve all tasks across all pets owned by this owner."""
    all_tasks = []
    for pet in self.pets:
        all_tasks.extend(pet.get_tasks())
    return all_tasks
```

**Key Insight:** The Scheduler doesn't bypass the Owner's structure; instead, it asks the Owner for all tasks. This maintains separation of concerns: the Owner knows how to collect its pets' tasks, and the Scheduler consumes that interface.

---

## Planning Workflows

### Workflow 1: Single-Pet Planning
```python
scheduler = Scheduler()
plan = scheduler.generate_plan(pet, available_time=90)
print(plan.summary())
```
Result: One DailyPlan for one pet.

---

### Workflow 2: Multi-Pet Individual Plans
```python
scheduler = Scheduler()
plans = scheduler.generate_plans_for_owner(owner, available_time_per_pet=60)
for plan in plans:
    print(f"{plan.pet.name}: {len(plan.scheduled_tasks)} tasks")
```
Result: List of DailyPlans, one per pet, each with its own time budget.

---

### Workflow 3: Multi-Pet Combined Plan
```python
scheduler = Scheduler()
result = scheduler.generate_combined_plan(owner, total_available_time=180)
for plan in result["pet_plans"]:
    print(f"{plan.pet.name}: {plan.total_time_used} min used")
```
Result: Single time budget shared across all pets, tasks prioritized globally.

---

## Scheduling Algorithm

**Strategy: Greedy Priority-First**

1. **Collect** all candidate tasks from the pet(s)
2. **Sort** by:
   - Priority (MUST_DO → HIGH → MEDIUM → LOW)
   - Time-sensitivity (time-sensitive first)
   - Duration (shorter tasks first, tiebreaker)
3. **Pack** greedily: iterate through sorted list, include each task if it fits in remaining time
4. **Order** scheduled tasks by:
   - Time-sensitivity (urgent tasks earlier)
   - Priority
   - Preferred start time (earliest preferred time first)
5. **Track** dropped tasks with reasons for transparency

**Complexity:** O(n log n) due to sorting; O(n) packing. Suitable for ~100s of tasks.

**Why This Works:** 
- MUST_DO tasks (meds, critical feedings) always fit first
- HIGH-priority tasks (walks, training) slot next
- Non-critical tasks fill remaining time or are dropped
- Owners see *why* tasks were dropped → better UX

---

## Data Persistence

All classes support full serialization:

```python
# Serialize entire owner hierarchy
owner_dict = owner.to_dict()

# Later: reconstruct
owner_restored = Owner.from_dict(owner_dict)

# Serialize a plan (for saving to session state or file)
plan_dict = plan.to_dict()
plan_restored = DailyPlan.from_dict(plan_dict)
```

Serialization handles:
- Enums (converted to `.value` strings during serialization)
- Nested objects (tasks within pets, pets within owners)
- Date objects (ISO format strings)
- Dropped task reasons (preserved in dicts)

---

## Testing

The project includes a comprehensive test suite (`test_pawpal.py`) covering:
- Task creation, serialization, conflict detection
- Pet task management and serialization
- Owner multi-pet management and serialization
- Scheduler greedy selection and multi-pet planning
- DailyPlan output formatting and serialization

Run tests:
```bash
python test_pawpal.py
```

Run demo:
```bash
python demo.py
```

---

## Design Principles

1. **Single Responsibility:** Each class answers one question (who owns pets, what are a pet's tasks, what should today's schedule be, what does the plan look like?)
2. **Data/Process Separation:** Data classes (Owner, Pet, Task) are passive; process classes (Scheduler, DailyPlan) contain logic
3. **Transparency:** Dropped tasks include reasons; scheduling decisions are explainable
4. **Flexibility:** Strategy attribute in Scheduler supports future algorithm variations without changing the core structure
5. **Testability:** Clean interfaces allow unit testing each component independently

---

## Next Steps (Future Enhancements)

- Time-window-aware scheduling (ensure no overlapping tasks)
- Multi-day planning (weekly schedule)
- Owner preferences integration (preferred times, buffer time between tasks)
- Recurrence handling (weekly/monthly tasks)
- Conflict resolution (suggest alternatives when tasks don't fit)
- Data persistence (JSON/database storage)
- Streamlit UI integration
