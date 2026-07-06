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

## Features

### Scheduling Engine
- **Priority-aware scheduling** — fixed-time tasks are placed first; remaining tasks are sorted high → medium → low priority before being assigned slots (`DailyPlan.generate`)
- **Three constraint types** — `fixed` (exact time; conflict logged if blocked), `preferred` (morning / afternoon / evening window with fallback to any free slot), `flexible` (placed sequentially from 07:00)
- **Greedy free-slot search** — scans occupied intervals in sorted order and jumps the cursor to the end of each blocking block; returns exact-minute slots, not rounded increments (`DailyPlan._find_next_free`)
- **Owner busy-block exclusion** — owner's unavailable ranges seed the occupied list before any task is scheduled; free gaps are computed with a linear sweep (`Owner.get_available_slots`)

### Conflict Detection
- **Within-plan overlap detection** — half-open interval math (`a_start < b_end AND b_start < a_end`) catches tasks that collide inside a single pet's plan (`DailyPlan.get_overlapping_tasks`)
- **Cross-pet conflict detection** — flattens tasks from multiple pets' plans, skips same-plan pairs (already caught above), and surfaces owner-level time collisions (`detect_conflicts`)

### Recurring Tasks & Multi-day Planning
- **Recurrence system** — marking a task complete returns a copy with `due_date` advanced by 1 day (daily) or 7 days (weekly) via `timedelta` (`PetCareTask.mark_complete`)
- **7-day schedule generation** — day 0 schedules all tasks; days 1–6 replay only recurring tasks on a fresh pet copy to avoid state mutation (`generate_week`)

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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Medication: fixed at 08:00 — Must happen at 08:00 (recurring daily)
Morning Walk: scheduled at 06:00 (morning preference)
Feeding: scheduled at 17:00 (evening preference)

--- Luna (Siamese) ---
Daily Plan — 2026-07-03
================================
  07:30 – 07:40  Feeding [high priority]
  12:00 – 12:20  Grooming [medium priority]
  12:20 – 12:35  Playtime [low priority]

Reasoning:
Feeding: fixed at 07:30 — Must happen at 07:30 (recurring daily)
Grooming: scheduled at 12:00 (afternoon preference)
Playtime: no constraint — placed at 12:20

Owner free slots today:
  07:00-09:00
  10:00-13:00
  14:00-21:00
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
================================================== test session starts ==================================================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/nath/Documents/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 5 items                                                                                                       

tests/test_pawpal.py .....                                                                                        [100%]

=================================================== 5 passed in 0.01s ===================================================

```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | DailyPlan.get_task_sorted() | sorts in chronological order |
| Filtering | DailyPlan.filter_task() | filters by priority or completion status |
| Conflict handling | DailyPlan.get_overlapping_tasks() | When generating a plan, if there is a conflict between, the higher priority task will be scheduled first and the next task will be scheduled at the next avaliable time.|
| Recurring tasks | Pet.get_recurring_task()| Recurring task are scheduled daily at the same time|

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Create an owner profile by entering name and email.
2. Block off time where no task can be done.
3. Add a pet by entering the pets names, species, breed, and age.
4. Select active pet to add tasks.
5. Add a task by entering task information such as name, time duration, priority, and constraint.
6. After all tasks are added, generate an interactive daily schedule that includes filtering task and marking once completed
7. Generate a view of a 7-day schedule.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
