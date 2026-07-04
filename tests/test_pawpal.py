import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, PetCareTask


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
