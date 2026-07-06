from pawpal_system import Owner, Pet, PetCareTask, Constraint, DailyPlan, generate_week, detect_conflicts
from pawpal_system import _to_minutes, _to_time_str

DIVIDER = "=" * 44

# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
owner = Owner(name="Alex Rivera", email="alex@example.com")
owner.add_busy_block("09:00", "10:00")  # morning meeting
owner.add_busy_block("13:00", "14:00")  # lunch break

# ---------------------------------------------------------------------------
# Pet 1 — Mochi the dog
# Tasks added out of order: evening → flexible/weekly → fixed-daily → preferred-morning
# ---------------------------------------------------------------------------
mochi = Pet(name="Mochi", species="Dog", breed="Shiba Inu", age=3)

feeding_mochi = PetCareTask(
    task_name="Feeding",
    duration_minutes=10,
    priority="medium",
    constraint=Constraint(type="preferred", preferred_window="evening", recurrence="daily"),
    due_date="2026-07-05",
)

bath = PetCareTask(
    task_name="Bath Time",
    duration_minutes=20,
    priority="low",
    constraint=Constraint(type="preferred", preferred_window="afternoon", recurrence="weekly"),
    due_date="2026-07-05",
)

medication = PetCareTask(
    task_name="Medication",
    duration_minutes=5,
    priority="high",
    constraint=Constraint(type="fixed", fixed_time="08:00", recurrence="daily"),
    due_date="2026-07-05",
)

morning_walk = PetCareTask(
    task_name="Morning Walk",
    duration_minutes=30,
    priority="high",
    constraint=Constraint(type="preferred", preferred_window="morning"),
)

# Added evening-first, then weekly, then fixed-daily, then preferred-morning
mochi.add_task(feeding_mochi)
mochi.add_task(bath)
mochi.add_task(medication)
mochi.add_task(morning_walk)

# ---------------------------------------------------------------------------
# Pet 2 — Luna the cat
# Tasks added out of order: flexible → afternoon → fixed-daily
# ---------------------------------------------------------------------------
luna = Pet(name="Luna", species="Cat", breed="Siamese", age=5)

playtime = PetCareTask(
    task_name="Playtime",
    duration_minutes=15,
    priority="low",
    constraint=Constraint(type="flexible"),
)

grooming = PetCareTask(
    task_name="Grooming",
    duration_minutes=20,
    priority="medium",
    constraint=Constraint(type="preferred", preferred_window="afternoon", recurrence="weekly"),
    due_date="2026-07-05",
)

feeding_luna = PetCareTask(
    task_name="Feeding",
    duration_minutes=10,
    priority="high",
    constraint=Constraint(type="fixed", fixed_time="07:30", recurrence="daily"),
    due_date="2026-07-05",
)

# Added flexible first, then weekly afternoon, then fixed-daily — opposite of schedule order
luna.add_task(playtime)
luna.add_task(grooming)
luna.add_task(feeding_luna)

owner.add_pet(mochi)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# Generate schedules and demonstrate sorting + filtering
# ---------------------------------------------------------------------------
print(DIVIDER)
print("         PawPal+ — Today's Schedule")
print(DIVIDER)

TODAY = "2026-07-05"

for pet in owner.pets:
    plan = DailyPlan(date=TODAY)
    plan.generate(pet=pet, owner=owner)

    print(f"\n{'─' * 44}")
    print(f"  {pet.name} ({pet.breed})")
    print(f"{'─' * 44}")

    if plan.conflicts:
        print("  [!] Conflicts detected:")
        for c in plan.conflicts:
            print(f"      {c}")
    else:
        print("  [✓] No scheduling conflicts")

    print("\n  Tasks sorted chronologically (get_tasks_sorted):")
    for t in plan.get_tasks_sorted():
        end = _to_time_str(_to_minutes(t.scheduled_time) + t.duration_minutes)
        done = "✓" if t.completed else " "
        due  = f"  due {t.due_date}" if t.due_date else ""
        print(f"    [{done}] {t.scheduled_time}–{end}  {t.task_name:<16} [{t.priority}]{due}")

    high = plan.filter_tasks(priority="high")
    print(f"\n  High-priority tasks ({len(high)}):")
    for t in high:
        print(f"    · {t.task_name} @ {t.scheduled_time}")

    pending = plan.filter_tasks(completed=False)
    print(f"\n  Pending tasks ({len(pending)} of {len(plan.scheduled_tasks)}):")
    for t in pending:
        print(f"    · {t.task_name}")

    low = plan.filter_tasks(priority="low")
    print(f"\n  Low-priority tasks ({len(low)}):")
    for t in low:
        print(f"    · {t.task_name} @ {t.scheduled_time}")

# ---------------------------------------------------------------------------
# Demonstrate mark_complete() auto-spawning the next occurrence
# ---------------------------------------------------------------------------
print(f"\n{DIVIDER}")
print("  mark_complete() — next-occurrence demo")
print(DIVIDER)

demo_tasks = [
    ("Mochi", medication),     # daily
    ("Mochi", bath),           # weekly
    ("Mochi", morning_walk),   # no recurrence — should return None
    ("Luna",  feeding_luna),   # daily
]

for pet_name, task in demo_tasks:
    next_task = task.mark_complete(today=TODAY)
    recur_label = task.constraint.recurrence or "one-off"
    status = f"✓ completed  [{recur_label}]"
    print(f"\n  {pet_name} / {task.task_name}")
    print(f"    {status}")
    if next_task:
        delta = {"daily": 1, "weekly": 7}[task.constraint.recurrence]
        print(f"    → next occurrence due: {next_task.due_date}  (timedelta +{delta}d)")
        print(f"      completed={next_task.completed}  scheduled_time={next_task.scheduled_time!r}")
    else:
        print("    → no next occurrence (not recurring)")

# ---------------------------------------------------------------------------
# 7-day recurring view for Mochi
# ---------------------------------------------------------------------------
print(f"\n{DIVIDER}")
print("  7-Day Recurring View — Mochi")
print(DIVIDER)

week = generate_week(pet=mochi, owner=owner, start_date=TODAY, days=7)
for day_plan in week:
    tasks_str = ", ".join(t.task_name for t in day_plan.get_tasks_sorted())
    marker = "(all tasks)     " if day_plan.date == TODAY else "(recurring only)"
    print(f"  {day_plan.date}  {marker}: {tasks_str or 'none'}")

# ---------------------------------------------------------------------------
# Owner availability
# ---------------------------------------------------------------------------
print(f"\n{DIVIDER}")
print("  Owner free slots today")
print(DIVIDER)
for slot in owner.get_available_slots():
    print(f"  {slot}")

# ---------------------------------------------------------------------------
# Conflict detection — within a single pet's plan
#
# generate() prevents overlaps on its own, but edit_task() bypasses it.
# We manually move Mochi's Feeding onto 08:00 (same slot as Medication) to
# simulate a bad manual reschedule, then call get_overlapping_tasks().
# ---------------------------------------------------------------------------
print(f"\n{DIVIDER}")
print("  Conflict Detection — Within-Plan (same pet)")
print(DIVIDER)

mochi_plan = DailyPlan(date=TODAY, pet_name="Mochi")
mochi_plan.generate(pet=mochi, owner=owner)

print("  Mochi's schedule before manual edit:")
for t in mochi_plan.get_tasks_sorted():
    end = _to_time_str(_to_minutes(t.scheduled_time) + t.duration_minutes)
    print(f"    {t.scheduled_time}–{end}  {t.task_name}")

# Force a collision: move Feeding to 08:00 — same as Medication
mochi_plan.edit_task(feeding_mochi, "08:00")
print("\n  After edit_task(feeding_mochi, '08:00'):")
for t in mochi_plan.get_tasks_sorted():
    end = _to_time_str(_to_minutes(t.scheduled_time) + t.duration_minutes)
    print(f"    {t.scheduled_time}–{end}  {t.task_name}")

within_warnings = mochi_plan.get_overlapping_tasks()
print(f"\n  get_overlapping_tasks() found {len(within_warnings)} issue(s):")
if within_warnings:
    for w in within_warnings:
        print(f"    ⚠  {w}")
else:
    print("    (none)")

# ---------------------------------------------------------------------------
# Conflict detection — across two different pets' plans
#
# Luna's Feeding is fixed at 07:30 (10 min).
# We add a Vet Check-in for Mochi also at 07:30 (20 min).
# Each pet's generate() runs independently and has no knowledge of the other,
# so both tasks land at 07:30 — detect_conflicts() catches it.
# ---------------------------------------------------------------------------
print(f"\n{DIVIDER}")
print("  Conflict Detection — Cross-Pet (different pets, same owner)")
print(DIVIDER)

vet_checkin = PetCareTask(
    task_name="Vet Check-in",
    duration_minutes=20,
    priority="high",
    constraint=Constraint(type="fixed", fixed_time="07:30"),
)
mochi.add_task(vet_checkin)

mochi_plan2 = DailyPlan(date=TODAY, pet_name="Mochi")
luna_plan   = DailyPlan(date=TODAY, pet_name="Luna")
mochi_plan2.generate(pet=mochi, owner=owner)
luna_plan.generate(pet=luna,   owner=owner)

print("  Mochi's schedule:")
for t in mochi_plan2.get_tasks_sorted():
    end = _to_time_str(_to_minutes(t.scheduled_time) + t.duration_minutes)
    print(f"    {t.scheduled_time}–{end}  {t.task_name}")

print("  Luna's schedule:")
for t in luna_plan.get_tasks_sorted():
    end = _to_time_str(_to_minutes(t.scheduled_time) + t.duration_minutes)
    print(f"    {t.scheduled_time}–{end}  {t.task_name}")

cross_warnings = detect_conflicts([mochi_plan2, luna_plan])
print(f"\n  detect_conflicts() found {len(cross_warnings)} issue(s):")
if cross_warnings:
    for w in cross_warnings:
        print(f"    ⚠  {w}")
else:
    print("    (none)")
