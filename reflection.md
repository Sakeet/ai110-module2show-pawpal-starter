# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design for PawPal+ centers on five classes, split between two roles: data-holding classes (Owner, Pet, Task) that represent the real-world entities in the domain, and process/output classes (Scheduler, DailyPlan) that handle the actual "planning" logic and its result. This split was intentional from the start — I wanted the objects that store information to be separate from the object that makes decisions, so the scheduling algorithm could be built, tested, and changed without touching the data model.
Classes and responsibilities:

Owner — Represents the pet owner using the app. Holds basic identifying info and a collection of Pet objects. Its responsibility is administrative: managing which pets belong to this user. It contains no scheduling logic.

Pet — Represents a single animal and owns that animal's list of Task objects. Responsible for pet-specific context (species, age, care notes) and for basic task-list management (add/edit/remove). It does not decide what gets scheduled — only what tasks exist.

Task — Represents one unit of care (a walk, feeding, meds, etc.). Designed as a largely passive data object holding duration, priority, category, and time-sensitivity. It knows facts about itself but has no awareness of other tasks or of the overall schedule.

Scheduler — The core decision-making class. Takes a pet's tasks plus a time constraint (available minutes) and is responsible for selecting which tasks fit, ordering them sensibly, and generating the reasoning behind each inclusion/exclusion. This is where all the "smart" logic lives.

DailyPlan — The output object produced by Scheduler. Holds the finalized scheduled tasks, dropped tasks (with reasons), and time totals, plus simple formatting methods (summary(), explain()) so the Streamlit UI can display results without knowing how they were derived.

Initial relationships:
Owner 1───* Pet 1───* Task
                        │
                        ▼
                   Scheduler ──generates──> DailyPlan
Owner owns many Pets; each Pet owns many Tasks; Scheduler consumes a Pet's tasks (plus a time constraint) and produces a DailyPlan, which the UI layer then renders.
Guiding principle behind this initial cut: single responsibility per class — each class answers exactly one question (who owns what pets, what tasks does this pet have, what are this task's properties, what should today's plan be, what does that plan look like) — which keeps the scheduling algorithm isolated in Scheduler and easy to unit test independently of the UI or data model.
(This is the starting design — I'd expect it to evolve once I stress-test the scheduling algorithm itself, e.g., whether Task needs a conflicts_with() method, or whether Scheduler needs a strategy attribute to support multiple prioritization approaches.)

**b. Design changes**

Yes, the design evolved significantly during implementation. Here are the key changes and why I made them:

1. **Introduced Enums for Type Safety**
   - *Change:* Added `TaskCategory`, `Priority`, and `Frequency` enums to replace string-based values for category (e.g., "WALK" → `TaskCategory.WALK`).
   - *Why:* String-based magic values are error-prone (typos, inconsistency) and hard to validate. Enums provide type safety, IDE autocompletion, and ensure only valid values are used. This also makes the scheduler's priority sorting logic clearer and less fragile.

2. **Structured Time Windows for Conflict Detection**
   - *Change:* Replaced `Task.preferred_time_window: Optional[str]` (e.g., "morning") with `Optional[Tuple[int, int]]` representing `(start_minute, end_minute)` from midnight (e.g., `(480, 540)` = 8 AM to 9 AM).
   - *Why:* The original string-based time window was too vague to implement meaningful conflict detection. With structured times, `Task.conflicts_with()` can reliably detect overlaps. This unblocks future features like time-slot-aware scheduling and alerts for overlapping tasks.

3. **Dropped Tasks Now Track Reasons**
   - *Change:* Changed `DailyPlan.dropped_tasks: List[Task]` to `List[Dict[str, Any]]` where each dict holds `{"task": Task, "reason": str}`.
   - *Why:* Simply dropping a task without explanation is a poor UX. Storing the reason (e.g., "not enough time remaining") makes the app transparent to users and supports future features like "why was this left out?" explanations in the UI.

4. **Full Serialization Support**
   - *Change:* Implemented `Task.to_dict()` / `Task.from_dict()` and `Pet.to_dict()` / `Pet.from_dict()` with proper handling of enum values and nested objects.
   - *Why:* The original stubs made it impossible to persist data to Streamlit session state or files. Real serialization is required for the app to remember user data across sessions. This also revealed edge cases (e.g., enums must serialize as `.value` strings, not enum objects).

5. **Greedy Scheduler Algorithm in Generate Plan**
   - *Change:* Implemented `Scheduler.generate_plan()` and helper methods (`_select_tasks`, `_order_tasks`) with a clear, greedy priority-based algorithm: sort all tasks by priority (MUST_DO first) and time-sensitivity, greedily pack them into available time, then order scheduled tasks by time-sensitivity and priority.
   - *Why:* The initial stubs gave no guidance on algorithm. A greedy approach is simple, fast (O(n log n) sort + O(n) packing), and produces reasonable results for Module 2 scope. It also clarified that `generate_plan()` should internally call the helper methods, not require the caller to orchestrate them.

6. **Computed Plan Summary and Explanation**
   - *Change:* Implemented `DailyPlan.summary()` and `explain()` to produce formatted, human-readable output (e.g., task names, durations, dropped reasons) without the UI layer needing to know the internal structure.
   - *Why:* The UML left these as stubs, but clear output formatting is essential for Streamlit display. Moving formatting logic into `DailyPlan` keeps the UI layer simple and testable independently.

**Impact:**
These changes transformed the skeleton from a collection of empty stubs into a working, tested system with clear data flow. The result is more robust (enums, structured times), more transparent (reasons for dropped tasks), and more complete (serialization, working scheduler). The design is now ready for UI integration and handles the happy path reliably.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- One tradeoff my scheduler makes is that it checks for exact time-window overlap when detecting conflicts, rather than modeling every task's full duration across the day.
- This is reasonable for this project because the scheduler is meant to be lightweight and easy to understand for a pet-care app. Exact overlap checks are fast, simple to explain, and good enough to spot obvious scheduling conflicts without making the logic too complex.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
