from pawpal_system import Owner, Pet, PetCareTask, Constraint, DailyPlan

# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
owner = Owner(name="Alex Rivera", email="alex@example.com")
owner.add_busy_block("09:00", "10:00")  # morning meeting
owner.add_busy_block("13:00", "14:00")  # lunch break

# ---------------------------------------------------------------------------
# Pet 1 — Mochi the dog
# ---------------------------------------------------------------------------
mochi = Pet(name="Mochi", species="Dog", breed="Shiba Inu", age=3)

morning_walk = PetCareTask(
    task_name="Morning Walk",
    duration_minutes=30,
    priority="high",
    constraint=Constraint(type="preferred", preferred_window="morning"),
)

medication = PetCareTask(
    task_name="Medication",
    duration_minutes=5,
    priority="high",
    constraint=Constraint(type="fixed", fixed_time="08:00", is_recurring=True),
)

feeding_mochi = PetCareTask(
    task_name="Feeding",
    duration_minutes=10,
    priority="medium",
    constraint=Constraint(type="preferred", preferred_window="evening"),
)

mochi.add_task(morning_walk)
mochi.add_task(medication)
mochi.add_task(feeding_mochi)

# ---------------------------------------------------------------------------
# Pet 2 — Luna the cat
# ---------------------------------------------------------------------------
luna = Pet(name="Luna", species="Cat", breed="Siamese", age=5)

grooming = PetCareTask(
    task_name="Grooming",
    duration_minutes=20,
    priority="medium",
    constraint=Constraint(type="preferred", preferred_window="afternoon"),
)

playtime = PetCareTask(
    task_name="Playtime",
    duration_minutes=15,
    priority="low",
    constraint=Constraint(type="flexible"),
)

feeding_luna = PetCareTask(
    task_name="Feeding",
    duration_minutes=10,
    priority="high",
    constraint=Constraint(type="fixed", fixed_time="07:30", is_recurring=True),
)

luna.add_task(grooming)
luna.add_task(playtime)
luna.add_task(feeding_luna)

# ---------------------------------------------------------------------------
# Register pets with owner
# ---------------------------------------------------------------------------
owner.add_pet(mochi)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# Generate and print Today's Schedule
# ---------------------------------------------------------------------------
print("=" * 40)
print("        PawPal+ — Today's Schedule")
print("=" * 40)

for pet in owner.pets:
    plan = DailyPlan(date="2026-07-03")
    plan.generate(pet=pet, owner=owner)
    print(f"\n--- {pet.name} ({pet.breed}) ---")
    print(plan.display())

print("\nOwner free slots today:")
for slot in owner.get_available_slots():
    print(f"  {slot}")
