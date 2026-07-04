# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

The CLI entry point in `main.py` prints a simple, readable plan for each pet. A sample run looks like this:

```text
======================================================================
                   🐾 PAWPAL+ - PET CARE SCHEDULER 🐾                   
======================================================================

👤 Owner: Sarah Mitchell
   Timezone: EST
   Availability: weekday evenings and weekends

----------------------------------------------------------------------
🐕 PET 1: Creating Buddy the Dog...
   ✓ Added 5 tasks to Buddy

----------------------------------------------------------------------
🐱 PET 2: Creating Whiskers the Cat...
   ✓ Added 5 tasks to Whiskers

----------------------------------------------------------------------
📅 Generating Today's Schedules...

======================================================================
                          📋 TODAY'S SCHEDULE                          
======================================================================

======================== BUDDY ========================
Species: dog
Time budget: 120 min
Scheduled: 5 task(s) | Used: 110 min | Remaining: 10 min

Scheduled tasks:
  • Breakfast            | 15 min | MUST_DO | [08:00-08:15]
  • Morning Walk         | 30 min | HIGH    | [08:00-08:30]
  • Dinner               | 15 min | MUST_DO | [17:00-17:15]
  • Afternoon Walk       | 30 min | HIGH    | [17:00-17:30]
  • Training Session     | 20 min | MEDIUM  | [18:00-18:20]

====================== WHISKERS ======================
Species: cat
Time budget: 90 min
Scheduled: 5 task(s) | Used: 50 min | Remaining: 40 min

Scheduled tasks:
  • Breakfast            | 10 min | MUST_DO | [08:00-08:10]
  • Medication           |  5 min | MUST_DO | [10:00-10:05]
  • Dinner               | 10 min | MUST_DO | [17:00-17:10]
  • Lunch                | 10 min | MEDIUM  | [13:00-13:10]
  • Play & Enrichment    | 15 min | MEDIUM  | [15:00-15:15]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

The scheduler now includes a few lightweight but practical improvements for pet care planning:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting behavior | `Scheduler.sort_by_time()` | Orders tasks by their preferred start time so the daily plan feels more natural and time-aware. |
| Filtering behavior | `Scheduler.filter_tasks()` | Filters tasks by completion status and/or pet name, which helps owners focus on pending tasks for a specific pet. |
| Conflict detection | `Scheduler.detect_conflicts()` | Checks for overlapping time windows and returns a warning message instead of crashing the app. |
| Recurring task logic | `Task.mark_complete()` | When a daily or weekly task is completed, a new pending task is created for the next occurrence using `timedelta`. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
