# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design for PawPal+ centers on five classes, split between two roles: data-holding classes (Owner, Pet, Task) that represent real-world entities, and process/output classes (Scheduler, DailyPlan) that handle planning logic and formatted results. I intentionally kept the object model separate from scheduling decisions so the algorithm could evolve independently of the pet/task storage model.

Classes and responsibilities:

- **Owner** — Represents the pet owner and manages the list of Pet objects. It is administrative only and contains no scheduling logic.
- **Pet** — Represents a single pet and owns its list of Task objects. It is responsible for task management, not for choosing which tasks are scheduled.
- **Task** — Represents one care action with duration, priority, category, time sensitivity, and optional preferred time windows. It is mostly a passive data object and only knows how to identify conflicts with another task.
- **Scheduler** — The core decision engine. It selects which tasks fit within available time, orders them sensibly, and generates the reasoning behind each inclusion or exclusion.
- **DailyPlan** — The output model produced by Scheduler. It stores scheduled and dropped tasks, time totals, and provides human-readable display methods (`summary()` and `explain()`).

Initial relationships:

Owner 1───* Pet 1───* Task
                        │
                        ▼
                   Scheduler ──generates──> DailyPlan

This design enforces single responsibility: each class has one clear role, which made the scheduler easier to test and allowed the UI to remain thin.

**b. Design changes**

Yes, the design evolved as implementation exposed real requirements. Key changes included:

1. **Introduced Enums for Type Safety**
   - *Change:* Added `TaskCategory`, `Priority`, and `Frequency` enums instead of using strings.
   - *Why:* Enums reduce bugs from typo-prone strings, improve IDE support, and make priority sorting explicit.

2. **Structured Time Windows for Conflict Detection**
   - *Change:* Represented `preferred_time_window` as `Optional[Tuple[int, int]]` instead of vague text labels.
   - *Why:* Numeric time windows enabled precise conflict checking and laid the foundation for a schedule that can reason about overlapping tasks.

3. **Dropped Tasks Now Track Reasons**
   - *Change:* Changed `DailyPlan.dropped_tasks` to store both the task and a reason string.
   - *Why:* This made the scheduler’s decisions transparent and supported user-facing explanations in the UI.

4. **Full Serialization Support**
   - *Change:* Implemented `to_dict()` and `from_dict()` for `Task`, `Pet`, and `DailyPlan` objects.
   - *Why:* Serialization is needed for stable Streamlit session management, and it revealed implementation details like converting enums to `.value` strings.

5. **Greedy Scheduler Algorithm**
   - *Change:* Built `Scheduler.generate_plan()` with a greedy selection algorithm that prioritizes MUST_DO and HIGH tasks and fits them into the available time.
   - *Why:* This approach is simple, predictable, and sufficient for a pet-care planning app. It also avoids over-engineering while still supporting the required behaviors.

6. **Plan Formatting in DailyPlan**
   - *Change:* Added `DailyPlan.summary()` and `DailyPlan.explain()` to keep presentation logic out of the UI.
   - *Why:* This keeps the UI focused on presentation, while the model itself exposes readable output for both tests and the Streamlit front end.

**Impact**

These changes turned a conceptual skeleton into a working system. The design is now more robust, easier to reason about, and better suited for the UI. The scheduler is isolated, the data model is stable, and the plan output is clear.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers the following constraints:

- **Available time** per pet: the main capacity limit for each daily plan.
- **Task priority**: MUST_DO tasks are chosen before HIGH, MEDIUM, and LOW.
- **Time sensitivity**: time-sensitive tasks are preferred when deciding which tasks to include.
- **Preferred time windows**: used for ordering tasks and for conflict detection.

I decided these constraints mattered most because they reflect real pet-care decisions: owners want to prioritize must-do care, avoid overlapping appointments, and fit the most important tasks into the time they truly have.

**b. Tradeoffs**

One tradeoff in the implementation is that the scheduler detects conflicts by comparing preferred time windows, but it does not build a full minute-by-minute timeline. That keeps the algorithm simple and easy to explain, which is a good fit for this project size. The consequence is that the scheduler is strong at spotting obvious overlaps and ordering tasks, but it is not yet a full calendar engine.

Another tradeoff is the greedy plan selection. It quickly chooses tasks by priority and urgency, which is sufficient for the module requirements, but it does not guarantee a globally optimal solution for every possible mix of durations and priorities.

## 3. AI Collaboration

**a. How you used AI**

I used the AI assistant primarily for:

- **Design brainstorming**: confirming the separation between data model classes and scheduling logic.
- **Code refinement**: transforming stub methods into working implementations and making the plan output more readable.
- **Testing guidance**: generating edge-case test ideas around sorting, recurrence, and conflict detection.
- **Documentation updates**: drafting the README walkthrough and the reflection narrative.

The most helpful prompts were those that asked the AI to explain tradeoffs in plain language, compare alternative scheduler designs, and suggest focused tests for specific behaviors.

**b. Judgment and verification**

One moment I did not accept an AI suggestion as-is was when it proposed storing the preferred time window as a text label like "morning" and then using string matching to detect conflicts. I rejected that because it would have made overlap detection too imprecise and fragile. Instead, I kept the design clean by using numeric minute ranges for time windows and writing an explicit `conflicts_with()` method.

I verified suggestions by reading the resulting code, running the test suite, and ensuring the scheduler behavior matched the intended use cases. If a proposed approach felt too complex or too vague, I simplified it and only kept the parts that supported the actual features.

## 4. Testing and Verification

**a. What you tested**

I tested the following behaviors:

- task sorting by preferred time window,
- recurring task generation for daily and weekly tasks,
- conflict detection for overlapping time windows,
- plan generation under a fixed time budget,
- task filtering by status and pet.

These tests were important because they cover the main scheduler qualities the app promises: sensible ordering, recurring care, clear warnings for conflicts, and a plan that fits available time.

**b. Confidence**

I am fairly confident the scheduler works correctly for the core use cases. The path from tasks to plan is covered by tests, and the logic is simple enough to reason about.

If I had more time, I would add edge-case tests for:

- tasks with identical time windows and different priorities,
- combined plans across multiple pets sharing a single time budget,
- tasks with no preferred time window,
- tasks whose duration exactly fills the remaining time,
- repeated completion of recurring tasks over multiple days.

## 5. Reflection

**a. What went well**

I am most satisfied with the clean separation between data model and scheduling logic. That separation made it easy to test the scheduler independently and to connect the same logic to both the CLI sample output and the Streamlit UI.

**b. What you would improve**

If I had another iteration, I would improve the time-window model by making it first-class and adding a true timeline builder. That would let the scheduler place tasks into specific slots rather than only sorting and filtering by windows.

**c. Key takeaway**

The most important thing I learned is that being the lead architect means using AI as a collaborator, not as an autopilot. The AI can propose ideas quickly, but the best result comes from validating those ideas, keeping the design minimal, and rejecting anything that adds complexity without supporting the core product goals.