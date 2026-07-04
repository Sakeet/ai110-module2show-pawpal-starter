"""
Demo script showing the complete PawPal system in action.
This demonstrates how Task, Pet, Owner, and Scheduler work together
to create a multi-pet care planning application.
"""

from pawpal_system import (
    Task, Pet, Owner, Scheduler,
    TaskCategory, Priority, Frequency
)


def demo_single_pet_planning():
    """Demo 1: Plan tasks for a single pet."""
    print("=" * 60)
    print("DEMO 1: Single Pet Daily Planning")
    print("=" * 60)
    
    # Create a pet with tasks
    buddy = Pet(
        name="Buddy",
        species="dog",
        breed="Golden Retriever",
        age=3,
        notes="Loves outdoor activities"
    )
    
    # Add various care tasks
    tasks = [
        Task(
            id="t1",
            name="Morning walk",
            category=TaskCategory.WALK,
            duration=30,
            priority=Priority.HIGH,
            preferred_time_window=(480, 540),  # 8-9 AM
            is_time_sensitive=True,
        ),
        Task(
            id="t2",
            name="Breakfast",
            category=TaskCategory.FEEDING,
            duration=15,
            priority=Priority.MUST_DO,
            preferred_time_window=(480, 510),  # 8-8:30 AM
            is_time_sensitive=True,
        ),
        Task(
            id="t3",
            name="Playtime",
            category=TaskCategory.ENRICHMENT,
            duration=20,
            priority=Priority.MEDIUM,
        ),
        Task(
            id="t4",
            name="Afternoon walk",
            category=TaskCategory.WALK,
            duration=30,
            priority=Priority.HIGH,
        ),
        Task(
            id="t5",
            name="Dinner",
            category=TaskCategory.FEEDING,
            duration=15,
            priority=Priority.MUST_DO,
        ),
    ]
    
    for task in tasks:
        buddy.add_task(task)
    
    # Generate plan with limited time
    scheduler = Scheduler()
    plan = scheduler.generate_plan(buddy, available_time=90)
    
    print(f"\n{plan.summary()}\n")
    print(f"{plan.explain()}\n")


def demo_multi_pet_management():
    """Demo 2: Manage multiple pets and generate individual plans."""
    print("=" * 60)
    print("DEMO 2: Multi-Pet Management")
    print("=" * 60)
    
    # Create an owner with multiple pets
    owner = Owner(
        name="Sarah",
        preferences={"timezone": "EST", "notifications": "sms"}
    )
    
    # Pet 1: Dog
    dog = Pet(
        name="Buddy",
        species="dog",
        breed="Labrador",
        age=5,
        notes="Needs daily exercise"
    )
    dog.add_task(Task(id="d1", name="Walk", category=TaskCategory.WALK, duration=30, priority=Priority.HIGH))
    dog.add_task(Task(id="d2", name="Dinner", category=TaskCategory.FEEDING, duration=15, priority=Priority.MUST_DO))
    
    # Pet 2: Cat
    cat = Pet(
        name="Whiskers",
        species="cat",
        breed="Siamese",
        age=3,
        notes="Indoor cat, picky eater"
    )
    cat.add_task(Task(id="c1", name="Lunch", category=TaskCategory.FEEDING, duration=10, priority=Priority.MUST_DO))
    cat.add_task(Task(id="c2", name="Enrichment", category=TaskCategory.ENRICHMENT, duration=15, priority=Priority.MEDIUM))
    
    # Pet 3: Rabbit
    rabbit = Pet(
        name="Hoppy",
        species="rabbit",
        breed="Holland Lop",
        age=2,
        notes="Shy, prefers quiet"
    )
    rabbit.add_task(Task(id="r1", name="Hay refill", category=TaskCategory.FEEDING, duration=5, priority=Priority.MUST_DO))
    rabbit.add_task(Task(id="r2", name="Cage cleaning", category=TaskCategory.GROOMING, duration=20, priority=Priority.MEDIUM))
    
    # Add pets to owner
    owner.add_pet(dog)
    owner.add_pet(cat)
    owner.add_pet(rabbit)
    
    print(f"\nOwner: {owner.name}")
    print(f"Pets: {', '.join([p.name for p in owner.pets])}")
    print(f"Total tasks across all pets: {len(owner.get_all_tasks())}\n")
    
    # Generate plans for each pet
    scheduler = Scheduler()
    plans = scheduler.generate_plans_for_owner(owner, available_time_per_pet=60)
    
    for i, plan in enumerate(plans, 1):
        print(f"\n--- Plan {i}: {plan.pet.name} ---")
        print(plan.summary())


def demo_serialization():
    """Demo 3: Serialize and deserialize a complete owner setup."""
    print("\n" + "=" * 60)
    print("DEMO 3: Full Serialization (Save/Load)")
    print("=" * 60)
    
    # Create a complete setup
    owner = Owner(name="Mike", preferences={"morning_person": True})
    
    pet = Pet(name="Rex", species="dog", breed="German Shepherd", age=4)
    pet.add_task(Task(id="t1", name="Walk", category=TaskCategory.WALK, duration=45, priority=Priority.HIGH))
    pet.add_task(Task(id="t2", name="Training", category=TaskCategory.ENRICHMENT, duration=30, priority=Priority.HIGH))
    pet.add_task(Task(id="t3", name="Meal", category=TaskCategory.FEEDING, duration=10, priority=Priority.MUST_DO))
    
    owner.add_pet(pet)
    
    # Serialize
    owner_dict = owner.to_dict()
    print(f"\nSerialized owner to dict with {len(owner_dict['pets'])} pet(s)")
    print(f"Pet '{owner_dict['pets'][0]['name']}' has {len(owner_dict['pets'][0]['tasks'])} tasks")
    
    # Generate and serialize a plan
    scheduler = Scheduler()
    plan = scheduler.generate_plan(pet, available_time=90)
    plan_dict = plan.to_dict()
    print(f"\nSerialized plan: {len(plan_dict['scheduled_tasks'])} scheduled, {len(plan_dict['dropped_tasks'])} dropped")
    
    # Deserialize back
    from pawpal_system import DailyPlan
    loaded_owner = Owner.from_dict(owner_dict)
    loaded_plan = DailyPlan.from_dict(plan_dict)
    
    print(f"\nDeserialized owner: {loaded_owner.name} with {len(loaded_owner.pets)} pet(s)")
    print(f"Deserialized plan for: {loaded_plan.pet.name} on {loaded_plan.date}")
    print(f"  Scheduled tasks: {len(loaded_plan.scheduled_tasks)}")
    print(f"  Time used: {loaded_plan.total_time_used} / {loaded_plan.total_time_used + loaded_plan.time_remaining} minutes")


def demo_conflict_detection():
    """Demo 4: Detect task scheduling conflicts."""
    print("\n" + "=" * 60)
    print("DEMO 4: Time Window Conflict Detection")
    print("=" * 60)
    
    # Create tasks with overlapping time windows
    task1 = Task(
        id="t1",
        name="Morning jog",
        category=TaskCategory.WALK,
        duration=30,
        priority=Priority.HIGH,
        preferred_time_window=(480, 510),  # 8-8:30 AM
    )
    
    task2 = Task(
        id="t2",
        name="Breakfast",
        category=TaskCategory.FEEDING,
        duration=15,
        priority=Priority.MUST_DO,
        preferred_time_window=(500, 520),  # 8:20-8:40 AM (overlaps with jog)
    )
    
    task3 = Task(
        id="t3",
        name="Medication",
        category=TaskCategory.MEDS,
        duration=5,
        priority=Priority.MUST_DO,
        preferred_time_window=(530, 535),  # 8:50-8:55 AM (no overlap)
    )
    
    print(f"\nTask 1 (8:00-8:30): Morning jog")
    print(f"Task 2 (8:20-8:40): Breakfast")
    print(f"Task 3 (8:50-8:55): Medication")
    
    print(f"\nConflict check:")
    print(f"  Jog conflicts with Breakfast? {task1.conflicts_with(task2)} (Expected: True)")
    print(f"  Jog conflicts with Medication? {task1.conflicts_with(task3)} (Expected: False)")
    print(f"  Breakfast conflicts with Medication? {task2.conflicts_with(task3)} (Expected: False)")


if __name__ == "__main__":
    demo_single_pet_planning()
    demo_multi_pet_management()
    demo_serialization()
    demo_conflict_detection()
    
    print("\n" + "=" * 60)
    print("Demo complete! ✅")
    print("=" * 60)
