import datetime
import streamlit as st
from pawpal_system import Pet, PetCareTask, Constraint, Owner, DailyPlan, generate_week

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state vault — each key is initialized once per session
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

if "active_pet" not in st.session_state:
    st.session_state.active_pet = None

# ---------------------------------------------------------------------------
# Section 1: Owner profile
# ---------------------------------------------------------------------------
st.subheader("1. Owner Profile")

with st.form("owner_form"):
    owner_name  = st.text_input("Your name",  value="Jordan")
    owner_email = st.text_input("Email",       value="jordan@example.com")
    owner_saved = st.form_submit_button("Save Owner")

if owner_saved:
    if st.session_state.owner is None:
        # First time — Owner() constructor handles creation
        st.session_state.owner = Owner(name=owner_name, email=owner_email)
    else:
        # Already exists — update in-place so pets are preserved
        st.session_state.owner.name  = owner_name
        st.session_state.owner.email = owner_email
    st.success(f"Owner saved: {owner_name}")

owner = st.session_state.owner

if owner:
    st.caption(f"Current owner: **{owner.name}** · {owner.email}")

    with st.expander("Block off busy time"):
        col1, col2 = st.columns(2)
        with col1:
            block_start = st.text_input("Start (HH:MM)", value="09:00", key="bs")
        with col2:
            block_end = st.text_input("End   (HH:MM)", value="10:00", key="be")
        if st.button("Add busy block"):
            # owner.add_busy_block() stores the range as "HH:MM-HH:MM"
            owner.add_busy_block(block_start, block_end)
            st.success(f"Blocked {block_start}–{block_end}")

    if owner.busy_blocks:
        st.caption("Busy: " + "  |  ".join(owner.busy_blocks))

    # owner.get_available_slots() computes the free gaps
    free = owner.get_available_slots()
    if free:
        st.caption("Free slots: " + "  |  ".join(free))

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Add a pet
# ---------------------------------------------------------------------------
st.subheader("2. Add a Pet")

if not owner:
    st.info("Save an owner profile first.")
else:
    with st.form("pet_form"):
        col1, col2 = st.columns(2)
        with col1:
            pet_name = st.text_input("Pet name", value="Mochi")
            species  = st.selectbox("Species", ["Dog", "Cat", "Other"])
        with col2:
            breed = st.text_input("Breed", value="Shiba Inu")
            age   = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
        pet_saved = st.form_submit_button("Add Pet")

    if pet_saved:
        new_pet = Pet(name=pet_name, species=species, breed=breed, age=int(age))
        owner.add_pet(new_pet)           # Owner.add_pet() registers the pet
        st.session_state.active_pet = new_pet
        st.success(f"Added {pet_name} the {species}!")

    if owner.pets:
        selected_name = st.selectbox(
            "Active pet", [p.name for p in owner.pets], key="pet_select"
        )
        # Keep active_pet in sync with the selectbox
        st.session_state.active_pet = next(
            p for p in owner.pets if p.name == selected_name
        )

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Add care tasks
# ---------------------------------------------------------------------------
st.subheader("3. Add Care Tasks")

active_pet = st.session_state.active_pet

if not active_pet:
    st.info("Add a pet first.")
else:
    st.caption(f"Adding tasks for **{active_pet.name}**")

    with st.form("task_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task name", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
        with col3:
            priority = st.selectbox("Priority", ["high", "medium", "low"])

        constraint_type = st.selectbox(
            "Constraint type", ["flexible", "fixed", "preferred"]
        )
        fixed_time       = ""
        preferred_window = ""
        is_recurring     = False

        if constraint_type == "fixed":
            fixed_time   = st.text_input("Fixed time (HH:MM)", value="08:00")
            is_recurring = st.checkbox("Recurring daily")
        elif constraint_type == "preferred":
            preferred_window = st.selectbox(
                "Preferred window", ["morning", "afternoon", "evening"]
            )

        task_saved = st.form_submit_button("Add Task")

    if task_saved:
        # Build Constraint only when the type isn't flexible
        constraint = None
        if constraint_type != "flexible":
            constraint = Constraint(
                type=constraint_type,
                fixed_time=fixed_time,
                preferred_window=preferred_window,
                is_recurring=is_recurring,
            )

        new_task = PetCareTask(
            task_name=task_title,
            duration_minutes=int(duration),
            priority=priority,
            constraint=constraint,
        )
        active_pet.add_task(new_task)   # Pet.add_task() appends to pet.tasks
        st.success(f"Task added: {task_title}")

    # Pet.get_tasks() returns the current task list — drives the table below
    tasks = active_pet.get_tasks()
    if tasks:
        st.write(f"**{active_pet.name}'s tasks:**")
        st.table([
            {
                "Task":           t.task_name,
                "Duration (min)": t.duration_minutes,
                "Priority":       t.priority,
                "Constraint":     t.constraint.describe() if t.constraint else "Flexible",
            }
            for t in tasks
        ])
    else:
        st.info("No tasks yet — add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Generate today's schedule
# ---------------------------------------------------------------------------
st.subheader("4. Generate Today's Schedule")

if not owner or not active_pet:
    st.info("Complete owner and pet setup first.")
elif not active_pet.get_tasks():
    st.info("Add at least one task before generating a schedule.")
else:
    col1, col2 = st.columns(2)
    with col1:
        gen_single = st.button("Generate today's schedule")
    with col2:
        gen_week = st.button("Generate 7-day view (recurring)")

    if gen_single:
        today = datetime.date.today().isoformat()
        plan  = DailyPlan(date=today)
        plan.generate(pet=active_pet, owner=owner)
        st.session_state["last_plan"] = plan

    if gen_week:
        today = datetime.date.today().isoformat()
        plans = generate_week(pet=active_pet, owner=owner, start_date=today, days=7)
        st.session_state["last_plan"] = plans[0]
        st.success("7-day recurring plan generated!")
        for p in plans:
            with st.expander(p.date):
                st.text(p.display())

    plan = st.session_state.get("last_plan")
    if plan:
        # --- conflict alerts ---
        if plan.conflicts:
            for msg in plan.conflicts:
                st.warning(f"Scheduling conflict: {msg}")
        else:
            st.success("Schedule generated — no conflicts.")

        # --- filter controls ---
        st.write("**Filter tasks:**")
        fc1, fc2 = st.columns(2)
        with fc1:
            status_filter = st.selectbox(
                "Status", ["All", "Pending", "Completed"], key="sf"
            )
        with fc2:
            priority_filter = st.selectbox(
                "Priority", ["All", "high", "medium", "low"], key="pf"
            )

        completed_arg = None if status_filter == "All" else (status_filter == "Completed")
        priority_arg  = None if priority_filter == "All" else priority_filter

        # get_tasks_sorted() + filter_tasks() drive the filtered table
        filtered = [
            t for t in plan.get_tasks_sorted()
            if t in plan.filter_tasks(completed=completed_arg, priority=priority_arg)
        ]

        if filtered:
            st.table([
                {
                    "Time":           t.scheduled_time,
                    "Task":           t.task_name,
                    "Duration (min)": t.duration_minutes,
                    "Priority":       t.priority,
                    "Done":           "✓" if t.completed else "",
                }
                for t in filtered
            ])
        else:
            st.info("No tasks match the current filter.")

        with st.expander("Full schedule text"):
            st.text(plan.display())
