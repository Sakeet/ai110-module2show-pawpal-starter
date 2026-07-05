"""Restored tests from the project root file (moved into tests/).

This file was previously at the repository root and caused a pytest
import collision with tests/test_pawpal.py. It was moved to avoid the
issue.
"""

import json
from datetime import date, timedelta
from pawpal_system import (
    Task, Pet, Owner, Scheduler, DailyPlan,
    TaskCategory, Priority, Frequency
)


def test_task_creation_and_serialization():
    """Test Task creation, to_dict, and from_dict."""
    task = Task(
        id="task1",
        name="Morning walk",
        category=TaskCategory.WALK,
        duration=30,
        priority=Priority.HIGH,
        preferred_time_window=(480, 540),  # 8 AM to 9 AM
        frequency=Frequency.DAILY,
        is_time_sensitive=True,
    )
    
    # Test serialization
    task_dict = task.to_dict()
    assert task_dict["name"] == "Morning walk"
    assert task_dict["priority"] == "high"
    assert task_dict["category"] == "walk"
    
    # Test deserialization
    task2 = Task.from_dict(task_dict)
    assert task2.name == task.name
    assert task2.priority == task.priority
    assert task2.preferred_time_window == task.preferred_time_window


def test_conflicts_with():
    """Test time window conflict detection."""
    task1 = Task(
        id="t1",
        name="Walk 1",
        duration=30,
        preferred_time_window=(480, 540),  # 8-9 AM
    )
    
    task2 = Task(
        id="t2",
        name="Walk 2",
        duration=30,
        preferred_time_window=(520, 580),  # 8:40 AM - 9:40 AM (overlaps)
    )
    
    task3 = Task(
        id="t3",
        name="Walk 3",
        duration=30,
        preferred_time_window=(600, 660),  # 10-11 AM (no overlap)
    )
    
    assert task1.conflicts_with(task2), "Should detect overlap"
    assert not task1.conflicts_with(task3), "Should not detect overlap"


def test_pet_management():
    """Test Pet task management."""
    pet = Pet(
        name="Buddy",
        species="dog",
        breed="Golden Retriever",
        age=3,
    )
    
    # Add tasks
    walk = Task(id="w1", name="Morning walk", category=TaskCategory.WALK, duration=30)
    feed = Task(id="f1", name="Breakfast", category=TaskCategory.FEEDING, duration=10)
    
    pet.add_task(walk)
    pet.add_task(feed)
    
    assert len(pet.tasks) == 2
    
    # Get tasks by category
    walk_tasks = pet.get_tasks_by_category(TaskCategory.WALK)
    assert len(walk_tasks) == 1
    
    # Edit task
    pet.edit_task("w1", duration=45)
    assert pet.tasks[0].duration == 45
    
    # Remove task
    pet.remove_task("f1")
    assert len(pet.tasks) == 1


def test_pet_serialization():
    """Test Pet to_dict and from_dict with nested tasks."""
    pet = Pet(
        name="Whiskers",
        species="cat",
        breed="Siamese",
        age=2,
        notes="Picky eater",
    )
    
    task1 = Task(id="t1", name="Lunch", category=TaskCategory.FEEDING, duration=15, priority=Priority.MUST_DO)
    task2 = Task(id="t2", name="Play", category=TaskCategory.ENRICHMENT, duration=20)
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    # Serialize
    pet_dict = pet.to_dict()
    assert pet_dict["name"] == "Whiskers"
    assert len(pet_dict["tasks"]) == 2
    
    # Deserialize
    pet2 = Pet.from_dict(pet_dict)
    assert pet2.name == pet.name
    assert len(pet2.tasks) == 2
    assert pet2.tasks[0].name == "Lunch"


def test_owner_and_multi_pet():
    """Test Owner managing multiple pets and accessing all tasks."""
    owner = Owner(name="Alice", preferences={"timezone": "PST"})
    
    # Create pets with tasks
    dog = Pet(name="Buddy", species="dog")
    dog.add_task(Task(id="d1", name="Walk", category=TaskCategory.WALK, duration=30, priority=Priority.HIGH))
    dog.add_task(Task(id="d2", name="Dinner", category=TaskCategory.FEEDING, duration=15, priority=Priority.MUST_DO))
    
    cat = Pet(name="Whiskers", species="cat")
    cat.add_task(Task(id="c1", name="Lunch", category=TaskCategory.FEEDING, duration=10, priority=Priority.MUST_DO))
    cat.add_task(Task(id="c2", name="Enrichment", category=TaskCategory.ENRICHMENT, duration=20))
    
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    # Test pet retrieval
    assert owner.get_pet("Buddy") == dog
    assert owner.get_pet("Whiskers") == cat
    assert owner.get_pet("NonExistent") is None
    
    # Test getting all tasks
    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 4
    
    # Test getting tasks by category
    walks = owner.get_all_tasks_by_category(TaskCategory.WALK)
    assert len(walks) == 1
    assert walks[0].name == "Walk"
    
    feedings = owner.get_all_tasks_by_category(TaskCategory.FEEDING)
    assert len(feedings) == 2


def test_owner_serialization():
    """Test Owner to_dict and from_dict with all pets and tasks."""
    owner = Owner(name="Bob", preferences={"notifications": "email"})
    
    pet1 = Pet(name="Fido", species="dog")
    pet1.add_task(Task(id="p1t1", name="Walk", category=TaskCategory.WALK, duration=30))
    
    pet2 = Pet(name="Mittens", species="cat")
    pet2.add_task(Task(id="p2t1", name="Feed", category=TaskCategory.FEEDING, duration=10))
    
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    
    # Serialize full hierarchy
    owner_dict = owner.to_dict()
    assert owner_dict["name"] == "Bob"
    assert len(owner_dict["pets"]) == 2
    assert len(owner_dict["pets"][0]["tasks"]) == 1
    
    # Deserialize
    owner2 = Owner.from_dict(owner_dict)
    assert owner2.name == owner.name
    assert len(owner2.pets) == 2
    assert owner2.pets[0].name == "Fido"
    assert len(owner2.pets[0].tasks) == 1


def test_scheduler_greedy_selection():
    """Test the scheduler's greedy task selection."""
    pet = Pet(name="Max", species="cat", age=2)
    
    # Create tasks with different priorities
    must_do = Task(
        id="m1", name="Meds", category=TaskCategory.MEDS,
        duration=10, priority=Priority.MUST_DO, is_time_sensitive=True
    )
    high = Task(
        id="h1", name="Play", category=TaskCategory.ENRICHMENT,
        duration=30, priority=Priority.HIGH
    )
    medium = Task(
        id="m2", name="Groom", category=TaskCategory.GROOMING,
        duration=20, priority=Priority.MEDIUM
    )
    low = Task(
        id="l1", name="Extra playtime", category=TaskCategory.ENRICHMENT,
        duration=20, priority=Priority.LOW
    )
    
    pet.add_task(must_do)
    pet.add_task(high)
    pet.add_task(medium)
    pet.add_task(low)
    
    scheduler = Scheduler()
    plan = scheduler.generate_plan(pet, available_time=60)
    
    # Should include: MUST_DO (10), HIGH (30), MEDIUM (20) = 60 total
    # LOW (20) should be dropped
    assert len(plan.scheduled_tasks) == 3
    assert len(plan.dropped_tasks) == 1
    assert plan.total_time_used == 60
    assert plan.time_remaining == 0
    
    # MUST_DO should come first, then HIGH, then MEDIUM
    assert plan.scheduled_tasks[0].id == "m1"
    assert plan.scheduled_tasks[1].id == "h1"
    assert plan.scheduled_tasks[2].id == "m2"


def test_scheduler_sort_by_time():
    """Test sorting tasks by their preferred time window."""
    scheduler = Scheduler()
    tasks = [
        Task(id="late", name="Late task", preferred_time_window=(900, 960)),
        Task(id="early", name="Early task", preferred_time_window=(480, 540)),
        Task(id="mid", name="Mid task", preferred_time_window=(720, 780)),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.id for task in sorted_tasks] == ["early", "mid", "late"]


def test_scheduler_conflict_detection_flags_duplicate_times():
    """Scheduler should flag tasks with duplicate/overlapping times as conflicts."""
    scheduler = Scheduler()
    task1 = Task(id="t1", name="Vet", preferred_time_window=(600, 660))
    task2 = Task(id="t2", name="Vaccination", preferred_time_window=(600, 660))

    warnings = scheduler.detect_conflicts([task1, task2])

    assert len(warnings) == 1
    assert "Vet" in warnings[0]
    assert "Vaccination" in warnings[0]


def test_sort_by_time_handles_missing_windows():
    """Tasks without preferred windows should sort after tasks with windows."""
    scheduler = Scheduler()
    tasks = [
        Task(id="no-window", name="No window"),
        Task(id="early", name="Early", preferred_time_window=(480, 540)),
        Task(id="also-no-window", name="Also no window"),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.id for task in sorted_tasks] == ["early", "also-no-window", "no-window"]


def test_scheduler_exact_capacity_and_overflow():
    """Scheduler should exactly fill available time and drop overflow tasks."""
    pet = Pet(name="Milo", species="cat")
    pet.add_task(Task(id="t1", name="Feed", duration=30, priority=Priority.MUST_DO))
    pet.add_task(Task(id="t2", name="Play", duration=30, priority=Priority.HIGH))
    pet.add_task(Task(id="t3", name="Brush", duration=30, priority=Priority.MEDIUM))

    scheduler = Scheduler()
    plan = scheduler.generate_plan(pet, available_time=60)

    assert plan.total_time_used == 60
    assert plan.time_remaining == 0
    assert len(plan.scheduled_tasks) == 2
    assert len(plan.dropped_tasks) == 1
    assert plan.dropped_tasks[0]["task"].id == "t3"


def test_scheduler_prefers_time_sensitive_tasks():
    """Time-sensitive tasks should be chosen before non-time-sensitive ones when time is limited."""
    pet = Pet(name="Luna", species="dog")
    pet.add_task(Task(id="a", name="A", duration=30, priority=Priority.MEDIUM, is_time_sensitive=False))
    pet.add_task(Task(id="b", name="B", duration=30, priority=Priority.MEDIUM, is_time_sensitive=True))
    pet.add_task(Task(id="c", name="C", duration=30, priority=Priority.LOW, is_time_sensitive=True))

    scheduler = Scheduler()
    plan = scheduler.generate_plan(pet, available_time=60)

    assert {task.id for task in plan.scheduled_tasks} == {"b", "a"}
    assert plan.scheduled_tasks[0].id == "b"
    assert plan.dropped_tasks[0]["task"].id == "c"


def test_detect_conflicts_treats_adjacent_windows_as_non_overlapping():
    """Tasks that touch end-to-start should not be reported as conflicting."""
    scheduler = Scheduler()
    tasks = [
        Task(id="t1", name="First", preferred_time_window=(480, 540)),
        Task(id="t2", name="Second", preferred_time_window=(540, 600)),
    ]

    warnings = scheduler.detect_conflicts(tasks)

    assert warnings == []


def test_generate_combined_plan_drops_tasks_per_pet():
    """Combined owner plan should assign dropped tasks back to the correct pet."""
    owner = Owner(name="Sam")
    dog = Pet(name="Dog", species="dog")
    cat = Pet(name="Cat", species="cat")

    dog.add_task(Task(id="d1", name="Walk", duration=30, priority=Priority.MUST_DO))
    dog.add_task(Task(id="d2", name="Play", duration=30, priority=Priority.HIGH))
    cat.add_task(Task(id="c1", name="Feed", duration=30, priority=Priority.MUST_DO))
    cat.add_task(Task(id="c2", name="Nap", duration=30, priority=Priority.LOW))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler()
    combined = scheduler.generate_combined_plan(owner, total_available_time=90)

    assert combined["total_time_used"] == 90
    assert combined["time_remaining"] == 0
    assert any(plan.pet.name == "Dog" and len(plan.dropped_tasks) == 0 for plan in combined["pet_plans"])
    assert any(plan.pet.name == "Cat" and len(plan.dropped_tasks) == 1 for plan in combined["pet_plans"])


def test_mark_complete_creates_next_occurrence_for_recurring_tasks():
    """Test that completed daily and weekly tasks create a new pending task for the next occurrence."""
    daily_task = Task(id="daily-1", name="Feed", frequency=Frequency.DAILY, due_date=date.today())
    weekly_task = Task(id="weekly-1", name="Groom", frequency=Frequency.WEEKLY, due_date=date.today())

    next_daily = daily_task.mark_complete()
    next_weekly = weekly_task.mark_complete()

    assert daily_task.status == "completed"
    assert weekly_task.status == "completed"
    assert next_daily is not None
    assert next_weekly is not None
    assert next_daily.status == "pending"
    assert next_weekly.status == "pending"
    assert next_daily.due_date == date.today() + timedelta(days=1)
    assert next_weekly.due_date == date.today() + timedelta(days=7)


def test_scheduler_detect_conflicts_returns_warning_messages():
    """Test conflict detection for overlapping tasks without crashing."""
    scheduler = Scheduler()
    buddy = Pet(name="Buddy", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")

    overlap_a = Task(id="a", name="Morning Walk", preferred_time_window=(480, 540), status="pending")
    overlap_b = Task(id="b", name="Vet Visit", preferred_time_window=(500, 560), status="pending")

    buddy.add_task(overlap_a)
    whiskers.add_task(overlap_b)

    warnings = scheduler.detect_conflicts([overlap_a, overlap_b])

    assert len(warnings) == 1
    assert "Morning Walk" in warnings[0]
    assert "Vet Visit" in warnings[0]


def test_scheduler_filter_tasks():
    """Test filtering tasks by completion status and pet name."""
    scheduler = Scheduler()
    buddy = Pet(name="Buddy", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")

    pending_walk = Task(id="w1", name="Walk", status="pending")
    completed_feed = Task(id="f1", name="Feed", status="completed")
    pending_med = Task(id="m1", name="Medicine", status="pending")

    buddy.add_task(pending_walk)
    buddy.add_task(completed_feed)
    whiskers.add_task(pending_med)

    owner = Owner(name="Alex")
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    filtered_tasks = scheduler.filter_tasks(owner.get_all_tasks(), status="pending", pet_name="Buddy")

    assert [task.id for task in filtered_tasks] == ["w1"]


def test_scheduler_get_all_tasks_for_owner():
    """Test scheduler retrieving all tasks from an owner."""
    owner = Owner(name="Charlie")
    
    dog = Pet(name="Rex", species="dog")
    dog.add_task(Task(id="t1", name="Walk", category=TaskCategory.WALK, duration=30))
    dog.add_task(Task(id="t2", name="Feed", category=TaskCategory.FEEDING, duration=10))
    
    cat = Pet(name="Luna", species="cat")
    cat.add_task(Task(id="t3", name="Groom", category=TaskCategory.GROOMING, duration=20))
    
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    scheduler = Scheduler()
    all_owner_tasks = scheduler.get_all_tasks_for_owner(owner)
    
    assert len(all_owner_tasks) == 3
    task_names = {t.name for t in all_owner_tasks}
    assert task_names == {"Walk", "Feed", "Groom"}


def test_generate_plans_for_owner():
    """Test generating individual plans for each of owner's pets."""
    owner = Owner(name="Diana")
    
    dog = Pet(name="Buddy", species="dog")
    dog.add_task(Task(id="d1", name="Walk", category=TaskCategory.WALK, duration=30, priority=Priority.HIGH))
    dog.add_task(Task(id="d2", name="Feed", category=TaskCategory.FEEDING, duration=15, priority=Priority.MUST_DO))
    
    cat = Pet(name="Whiskers", species="cat")
    cat.add_task(Task(id="c1", name="Groom", category=TaskCategory.GROOMING, duration=20, priority=Priority.MEDIUM))
    
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    scheduler = Scheduler()
    plans = scheduler.generate_plans_for_owner(owner, available_time_per_pet=60)
    
    assert len(plans) == 2
    assert plans[0].pet.name == "Buddy"
    assert plans[1].pet.name == "Whiskers"
    assert len(plans[0].scheduled_tasks) == 2  # Dog gets all tasks (30+15=45 < 60)
    assert len(plans[1].scheduled_tasks) == 1  # Cat gets groom task


def test_daily_plan_serialization():
    """Test DailyPlan serialization and deserialization."""
    pet = Pet(name="Test", species="test")
    task1 = Task(id="t1", name="Task 1", duration=20, priority=Priority.HIGH)
    task2 = Task(id="t2", name="Task 2", duration=30, priority=Priority.LOW)
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    scheduler = Scheduler()
    plan = scheduler.generate_plan(pet, available_time=25)
    
    # Serialize
    plan_dict = plan.to_dict()
    assert plan_dict["pet"]["name"] == "Test"
    assert len(plan_dict["scheduled_tasks"]) > 0
    
    # Deserialize
    plan2 = DailyPlan.from_dict(plan_dict)
    assert plan2.pet.name == plan.pet.name
    assert len(plan2.scheduled_tasks) == len(plan.scheduled_tasks)
    assert plan2.total_time_used == plan.total_time_used


def test_daily_plan_output():
    """Test DailyPlan summary and explanation."""
    pet = Pet(name="Buddy", species="dog", breed="Labrador", age=5)
    
    task1 = Task(id="t1", name="Walk", category=TaskCategory.WALK, duration=30, priority=Priority.HIGH)
    task2 = Task(id="t2", name="Lunch", category=TaskCategory.FEEDING, duration=15, priority=Priority.MUST_DO)
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    scheduler = Scheduler()
    plan = scheduler.generate_plan(pet, available_time=45)
    
    summary = plan.summary()
    assert "Buddy" in summary
    assert "Scheduled: 2 task(s), 45 minutes" in summary
    
    explain = plan.explain()
    assert "Walk" in explain
    assert "Lunch" in explain


if __name__ == "__main__":
    # Allows running this file directly for quick manual checks
    test_task_creation_and_serialization()
    test_conflicts_with()
    test_pet_management()
    test_pet_serialization()
    test_owner_and_multi_pet()
    test_owner_serialization()
    test_scheduler_greedy_selection()
    test_scheduler_get_all_tasks_for_owner()
    test_generate_plans_for_owner()
    test_daily_plan_serialization()
    test_daily_plan_output()
    
    print("\n✅ Restored tests ran successfully (manual run).")
