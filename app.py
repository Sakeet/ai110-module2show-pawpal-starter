import streamlit as st

from pawpal_system import Owner, Pet, Task, TaskCategory, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner
owner_name = st.text_input("Owner name", value=owner.name)
if owner_name != owner.name:
    owner.name = owner_name

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Add a Pet")
if st.button("Add pet"):
    if pet_name.strip():
        existing_pet = owner.get_pet(pet_name)
        if existing_pet is None:
            owner.add_pet(Pet(name=pet_name, species=species))
            st.success(f"Added {pet_name} to {owner.name}'s pet list.")
        else:
            st.info(f"{pet_name} is already in the list.")
    else:
        st.warning("Please enter a pet name first.")

st.markdown("### Add a Task")
if owner.pets:
    current_pet = owner.pets[-1]
    st.caption(f"Adding task for {current_pet.name}")
else:
    st.caption("Add a pet before creating a task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if not owner.pets:
        owner.add_pet(Pet(name=pet_name or "Pet", species=species))
        current_pet = owner.pets[-1]
    else:
        current_pet = owner.pets[-1]

    priority_map = {
        "low": Priority.LOW,
        "medium": Priority.MEDIUM,
        "high": Priority.HIGH,
    }
    task = Task(
        id=f"{current_pet.name.lower()}-{len(current_pet.tasks) + 1}",
        name=task_title,
        category=TaskCategory.OTHER,
        duration=int(duration),
        priority=priority_map[priority],
    )
    current_pet.add_task(task)
    st.success(f"Added '{task.name}' to {current_pet.name}.")

if owner.pets:
    current_pet = owner.pets[-1]
    st.write(f"### Current tasks for {current_pet.name}")
    if current_pet.get_tasks():
        scheduler = Scheduler(strategy="priority-first")
        pending_tasks = scheduler.filter_tasks(current_pet.get_tasks(), status="pending")
        sorted_tasks = scheduler.sort_by_time(pending_tasks)

        def format_window(task):
            if task.preferred_time_window:
                start, end = task.preferred_time_window
                return f"{start}-{end}"
            return "Flexible"

        task_rows = [
            {
                "Task": task.name,
                "Duration": task.duration,
                "Priority": task.priority.value,
                "Window": format_window(task),
                "Status": task.status,
            }
            for task in sorted_tasks
        ]
        st.caption("Tasks are sorted by preferred time window and filtered to pending items.")
        st.table(task_rows)
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Add a pet and at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(strategy="priority-first")
        all_tasks = owner.get_all_tasks()
        conflict_warnings = scheduler.detect_conflicts(all_tasks)

        if conflict_warnings:
            st.warning("Potential scheduling conflicts detected:")
            for warning in conflict_warnings:
                st.write(f"- {warning}")
            st.caption("A helpful next step is to move one of the overlapping tasks to a different time window.")
        else:
            st.success("No overlapping task windows were found.")

        plans = scheduler.generate_plans_for_owner(owner, available_time_per_pet=120)
        st.success("Schedule generated successfully.")
        for plan in plans:
            st.subheader(f"{plan.pet.name}'s plan")
            st.write(plan.summary())
            st.code(plan.explain())
