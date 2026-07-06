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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | DailyPlan.get_task_sorted() sorts in chronological order  |
| Filtering | | DailyPlan.filter_task filters by priority or completion status |
| Conflict handling | | When generating a plan, if there is a conflict between, the higher priority task will be scheduled first and the next task will be scheduled at the next avaliable time.|
| Recurring tasks | | Recurring task can be shown daily |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
