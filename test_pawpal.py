"""Simple test suite for PawPal system."""

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
    print("✓ Task creation and serialization works")


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
    print("✓ Conflict detection works")


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
    
    print("✓ Pet task management works")


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
    
    print("✓ Scheduler greedy selection works")


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
    
    print("✓ Daily plan output works")


def test_owner_management():
    """Test Owner pet management."""
    owner = Owner(name="Alice", preferences={"timezone": "PST"})
    
    pet1 = Pet(name="Buddy", species="dog")
    pet2 = Pet(name="Whiskers", species="cat")
    
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    
    assert len(owner.pets) == 2
    assert owner.get_pet("Buddy") == pet1
    assert owner.get_pet("Whiskers") == pet2
    assert owner.get_pet("NonExistent") is None
    
    owner.remove_pet(pet1)
    assert len(owner.pets) == 1
    
    print("✓ Owner pet management works")


if __name__ == "__main__":
    test_task_creation_and_serialization()
    test_conflicts_with()
    test_pet_management()
    test_scheduler_greedy_selection()
    test_daily_plan_output()
    test_owner_management()
    
    print("\n✅ All tests passed!")
