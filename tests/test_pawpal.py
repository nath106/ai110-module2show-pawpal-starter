import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, PetCareTask, Constraint, Owner, DailyPlan


def test_mark_complete_changes_status():
    task = PetCareTask(task_name="Morning Walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="Dog", breed="Shiba Inu", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(PetCareTask(task_name="Feeding", duration_minutes=10, priority="medium"))
    pet.add_task(PetCareTask(task_name="Playtime", duration_minutes=15, priority="low"))
    assert len(pet.get_tasks()) == 2


def test_get_tasks_sorted_returns_chronological_order():
    plan = DailyPlan(date="2026-07-05")
    t1 = PetCareTask(task_name="Evening Walk", duration_minutes=30, priority="low")
    t1.scheduled_time = "18:00"
    t2 = PetCareTask(task_name="Morning Meds", duration_minutes=10, priority="high")
    t2.scheduled_time = "08:00"
    t3 = PetCareTask(task_name="Afternoon Play", duration_minutes=20, priority="medium")
    t3.scheduled_time = "13:00"
    plan.scheduled_tasks = [t1, t2, t3]  # intentionally out of order

    sorted_times = [t.scheduled_time for t in plan.get_tasks_sorted()]
    assert sorted_times == ["08:00", "13:00", "18:00"]


def test_mark_complete_daily_creates_next_day_task():
    constraint = Constraint(type="fixed", fixed_time="08:00", recurrence="daily")
    task = PetCareTask(
        task_name="Morning Meds", duration_minutes=10, priority="high", constraint=constraint
    )

    next_task = task.mark_complete(today="2026-07-05")

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == "2026-07-06"
    assert next_task.completed is False
    assert next_task.task_name == "Morning Meds"


def test_scheduler_flags_duplicate_fixed_times():
    pet = Pet(name="Mochi", species="Dog", breed="Shiba Inu", age=3)
    owner = Owner(name="Jordan", email="jordan@example.com")

    # Two tasks both fixed at 08:00 — the second must conflict
    pet.add_task(PetCareTask(
        task_name="Morning Meds", duration_minutes=30, priority="high",
        constraint=Constraint(type="fixed", fixed_time="08:00"),
    ))
    pet.add_task(PetCareTask(
        task_name="Feeding", duration_minutes=15, priority="high",
        constraint=Constraint(type="fixed", fixed_time="08:00"),
    ))

    plan = DailyPlan(date="2026-07-05")
    plan.generate(pet=pet, owner=owner)

    assert len(plan.conflicts) > 0
