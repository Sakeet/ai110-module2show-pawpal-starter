"""
PawPal+ Main Entry Point
Demonstrates creating an owner with multiple pets and displaying today's schedule.
"""

from pawpal_system import (
    Task, Pet, Owner, Scheduler,
    TaskCategory, Priority, Frequency
)


def main():
    """Create an owner with multiple pets and display today's schedule."""
    
    print("\n" + "=" * 70)
    print("🐾 PAWPAL+ - PET CARE SCHEDULER 🐾".center(70))
    print("=" * 70)
    
    # ============================================================================
    # STEP 1: Create the Owner
    # ============================================================================
    owner = Owner(
        name="Sarah Mitchell",
        preferences={
            "timezone": "EST",
            "notifications": "email",
            "availability": "weekday evenings and weekends"
        }
    )
    print(f"\n👤 Owner: {owner.name}")
    print(f"   Timezone: {owner.preferences.get('timezone')}")
    print(f"   Availability: {owner.preferences.get('availability')}")
    
    # ============================================================================
    # STEP 2: Create Pets with Tasks
    # ============================================================================
    
    # PET 1: Buddy the Dog
    print("\n" + "-" * 70)
    print("🐕 PET 1: Creating Buddy the Dog...")
    buddy = Pet(
        name="Buddy",
        species="dog",
        breed="Golden Retriever",
        age=5,
        notes="High energy, loves outdoor activities. Needs consistent routine."
    )
    
    buddy_tasks = [
        Task(
            id="buddy_t1",
            name="Morning Walk",
            category=TaskCategory.WALK,
            duration=30,
            priority=Priority.HIGH,
            preferred_time_window=(480, 540),  # 8:00 AM - 9:00 AM
            frequency=Frequency.DAILY,
            is_time_sensitive=True,
        ),
        Task(
            id="buddy_t2",
            name="Breakfast",
            category=TaskCategory.FEEDING,
            duration=15,
            priority=Priority.MUST_DO,
            preferred_time_window=(510, 540),  # 8:30 AM - 9:00 AM
            frequency=Frequency.DAILY,
            is_time_sensitive=True,
        ),
        Task(
            id="buddy_t3",
            name="Afternoon Walk",
            category=TaskCategory.WALK,
            duration=30,
            priority=Priority.HIGH,
            preferred_time_window=(1020, 1080),  # 5:00 PM - 6:00 PM
            frequency=Frequency.DAILY,
            is_time_sensitive=False,
        ),
        Task(
            id="buddy_t4",
            name="Dinner",
            category=TaskCategory.FEEDING,
            duration=15,
            priority=Priority.MUST_DO,
            preferred_time_window=(1020, 1050),  # 5:00 PM - 5:30 PM
            frequency=Frequency.DAILY,
            is_time_sensitive=True,
        ),
        Task(
            id="buddy_t5",
            name="Training Session",
            category=TaskCategory.ENRICHMENT,
            duration=20,
            priority=Priority.MEDIUM,
            preferred_time_window=(1080, 1140),  # 6:00 PM - 7:00 PM
            frequency=Frequency.DAILY,
            is_time_sensitive=False,
        ),
    ]
    
    for task in buddy_tasks:
        buddy.add_task(task)
    
    owner.add_pet(buddy)
    print(f"   ✓ Added {len(buddy.tasks)} tasks to {buddy.name}")
    
    # PET 2: Whiskers the Cat
    print("\n" + "-" * 70)
    print("🐱 PET 2: Creating Whiskers the Cat...")
    whiskers = Pet(
        name="Whiskers",
        species="cat",
        breed="Siamese",
        age=3,
        notes="Indoor cat, prefers quiet. Picky eater with dietary restrictions."
    )
    
    whiskers_tasks = [
        Task(
            id="whiskers_t1",
            name="Breakfast",
            category=TaskCategory.FEEDING,
            duration=10,
            priority=Priority.MUST_DO,
            preferred_time_window=(480, 540),  # 8:00 AM - 9:00 AM
            frequency=Frequency.DAILY,
            is_time_sensitive=True,
        ),
        Task(
            id="whiskers_t2",
            name="Medication",
            category=TaskCategory.MEDS,
            duration=5,
            priority=Priority.MUST_DO,
            preferred_time_window=(600, 660),  # 10:00 AM - 11:00 AM
            frequency=Frequency.DAILY,
            is_time_sensitive=True,
        ),
        Task(
            id="whiskers_t3",
            name="Lunch",
            category=TaskCategory.FEEDING,
            duration=10,
            priority=Priority.MEDIUM,
            preferred_time_window=(780, 840),  # 1:00 PM - 2:00 PM
            frequency=Frequency.DAILY,
            is_time_sensitive=False,
        ),
        Task(
            id="whiskers_t4",
            name="Play & Enrichment",
            category=TaskCategory.ENRICHMENT,
            duration=15,
            priority=Priority.MEDIUM,
            preferred_time_window=(900, 960),  # 3:00 PM - 4:00 PM
            frequency=Frequency.DAILY,
            is_time_sensitive=False,
        ),
        Task(
            id="whiskers_t5",
            name="Dinner",
            category=TaskCategory.FEEDING,
            duration=10,
            priority=Priority.MUST_DO,
            preferred_time_window=(1020, 1080),  # 5:00 PM - 6:00 PM
            frequency=Frequency.DAILY,
            is_time_sensitive=True,
        ),
    ]
    
    for task in whiskers_tasks:
        whiskers.add_task(task)
    
    owner.add_pet(whiskers)
    print(f"   ✓ Added {len(whiskers.tasks)} tasks to {whiskers.name}")
    
    # ============================================================================
    # STEP 3: Create Scheduler and Generate Plans
    # ============================================================================
    print("\n" + "-" * 70)
    print("📅 Generating Today's Schedules...")
    scheduler = Scheduler(strategy="priority-first")
    
    # Generate individual plans for each pet
    # Buddy: 2 hours available (120 minutes)
    # Whiskers: 1.5 hours available (90 minutes)
    plans = [
        scheduler.generate_plan(buddy, available_time=120),
        scheduler.generate_plan(whiskers, available_time=90),
    ]
    
    # ============================================================================
    # STEP 4: Display Today's Schedule
    # ============================================================================
    print("\n" + "=" * 70)
    print("📋 TODAY'S SCHEDULE".center(70))
    print("=" * 70)
    
    for plan in plans:
        print(f"\n{plan.summary()}")
        print()
    
    # ============================================================================
    # STEP 5: Display Detailed Explanations
    # ============================================================================
    print("\n" + "=" * 70)
    print("💡 SCHEDULING RATIONALE".center(70))
    print("=" * 70)
    
    for plan in plans:
        print(f"\n{plan.explain()}")
        print()
    
    # ============================================================================
    # STEP 6: Display Owner's Total Task Count
    # ============================================================================
    print("=" * 70)
    print("📊 OWNER SUMMARY".center(70))
    print("=" * 70)
    all_tasks = owner.get_all_tasks()
    print(f"\n{owner.name}'s Pet Care Overview:")
    print(f"  • Total Pets: {len(owner.pets)}")
    print(f"  • Total Tasks: {len(all_tasks)}")
    
    for pet in owner.pets:
        print(f"    - {pet.name} ({pet.species}): {len(pet.tasks)} tasks")
    
    # Task breakdown by category
    print(f"\nTasks by Category:")
    for category in TaskCategory:
        category_tasks = owner.get_all_tasks_by_category(category)
        if category_tasks:
            print(f"  • {category.value.title()}: {len(category_tasks)} task(s)")
    
    print("\n" + "=" * 70)
    print("✅ Schedule Generation Complete!".center(70))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
