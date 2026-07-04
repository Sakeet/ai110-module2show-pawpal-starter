import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Pet, Priority, Task, TaskCategory


def test_task_completion_updates_status():
    task = Task(
        id="task-1",
        name="Morning walk",
        category=TaskCategory.WALK,
        duration=20,
        priority=Priority.HIGH,
    )

    assert task.status == "pending"

    task.mark_complete()

    assert task.status == "completed"


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog")
    task = Task(
        id="task-2",
        name="Dinner",
        category=TaskCategory.FEEDING,
        duration=15,
        priority=Priority.MUST_DO,
    )

    assert len(pet.tasks) == 0

    pet.add_task(task)

    assert len(pet.tasks) == 1
