# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the AI to help implement a persistence layer and a more advanced scheduler mode for PawPal+ so the application could save/load user data and place tasks into actual time slots.

**What did the agent do?**

- Edited `pawpal_system.py` to add `Owner.save_to_file()` and `Owner.load_from_file()`.
- Added `Task.scheduled_start` and `Task.scheduled_end` fields for scheduled time slots.
- Implemented `Scheduler.generate_time_blocked_plan()` to assign tasks into non-overlapping preferred windows.
- Updated `main.py` to save owner data to `data/pawpal_owner.json` and verify that it can be loaded back.
- Updated `README.md` to document persistence, advanced scheduling, and formatted CLI output.

**What did you have to verify or fix manually?**

- Confirmed the persistence JSON format matched nested `Owner`/`Pet`/`Task` serialization.
- Verified `generate_time_blocked_plan()` scheduled only tasks that fit in their preferred windows.
- Ensured the CLI output still ran cleanly and the data file path was correct.

---

## Prompt Comparison (SF11)

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Copilot-style AI assistant | Same assistant with a more specific task prompt |
| **Prompt** | "Add JSON save/load persistence for Owner/Pet/Task and document it." | "Implement a time-blocked scheduling mode that places tasks into non-overlapping preferred windows." |
| **Response summary** | Added a persistence layer and JSON serialization methods. | Added a time-blocked scheduler and updated the demo to use it. |
| **What was useful** | It produced the required save/load API quickly and pointed out serialization edge cases. | It provided a clean plan-generation approach and highlighted the need for task slot metadata. |
| **Problems noticed** | The initial suggestion needed manual verification for file path handling and nested task decoding. | The first version treated all tasks as equal, so I adjusted it to respect priority and window constraints. |
| **Decision** | Used as the base implementation for persistence. | Used as the base implementation for advanced scheduling, with manual refinement. |

**Which approach did you use in your final implementation and why?**

I used the AI-suggested persistence implementation with manual verification to ensure the JSON file structure was correct, and I used the advanced scheduling suggestion after refining the task ordering logic to preserve priority and time-window constraints.
> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
