import copy
import datetime
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def _to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' to minutes since midnight."""
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)


def _to_time_str(minutes: int) -> str:
    """Convert minutes since midnight to 'HH:MM'."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


WINDOWS = {
    "morning":   ("06:00", "12:00"),
    "afternoon": ("12:00", "17:00"),
    "evening":   ("17:00", "21:00"),
}

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


# ---------------------------------------------------------------------------
# Constraint
# ---------------------------------------------------------------------------

@dataclass
class Constraint:
    type: str                   # "fixed", "preferred", or "flexible"
    fixed_time: str = ""        # e.g. "08:00" for daily medication
    preferred_window: str = ""  # e.g. "morning", "afternoon", "evening"
    is_recurring: bool = False  # legacy flag; prefer recurrence= below
    recurrence: str = ""        # "daily", "weekly", or "" (one-off)

    def is_time_satisfied(self, time: str) -> bool:
        """Return True if the given time satisfies this constraint."""
        if self.type == "fixed":
            return time == self.fixed_time
        if self.type == "preferred":
            window = WINDOWS.get(self.preferred_window)
            if window:
                return _to_minutes(window[0]) <= _to_minutes(time) < _to_minutes(window[1])
        return True  # flexible: any time is acceptable

    def describe(self) -> str:
        """Return a human-readable description of the constraint."""
        recur_suffix = f" (repeats {self.recurrence})" if self.recurrence else (
            " (recurring daily)" if self.is_recurring else ""
        )
        if self.type == "fixed":
            return f"Must happen at {self.fixed_time}{recur_suffix}"
        if self.type == "preferred":
            return f"Preferred in the {self.preferred_window}{recur_suffix}"
        return f"Flexible timing{recur_suffix}"


# ---------------------------------------------------------------------------
# PetCareTask
# ---------------------------------------------------------------------------

@dataclass
class PetCareTask:
    task_name: str
    duration_minutes: int
    priority: str                          # "high", "medium", or "low"
    constraint: Optional[Constraint] = None
    scheduled_time: Optional[str] = None  # set by DailyPlan.generate()
    due_date: Optional[str] = None        # "YYYY-MM-DD"; set on recurring tasks
    completed: bool = False

    def set_constraint(self, c: Constraint) -> None:
        """Attach a constraint to this task."""
        self.constraint = c

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        return self.duration_minutes

    def mark_complete(self, today: str = "") -> Optional["PetCareTask"]:
        """Mark this task done and return the next occurrence, or None if not recurring.

        Uses timedelta to compute the next due_date:
          daily  → today + 1 day
          weekly → today + 7 days
        """
        self.completed = True

        recurrence = self.constraint.recurrence if self.constraint else ""
        if not recurrence:
            return None

        delta_days = {"daily": 1, "weekly": 7}.get(recurrence)
        if delta_days is None:
            return None

        base = datetime.date.fromisoformat(today) if today else datetime.date.today()
        next_due = (base + datetime.timedelta(days=delta_days)).isoformat()

        next_task = copy.copy(self)
        next_task.completed = False
        next_task.scheduled_time = None
        next_task.due_date = next_due
        return next_task


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[PetCareTask] = field(default_factory=list)

    def add_task(self, task: PetCareTask) -> None:
        """Append a care task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list[PetCareTask]:
        """Return a shallow copy of the pet's task list."""
        return list(self.tasks)

    def get_recurring_tasks(self) -> list[PetCareTask]:
        """Return tasks that have any recurrence (is_recurring flag or recurrence field)."""
        return [
            t for t in self.tasks
            if t.constraint and (t.constraint.is_recurring or t.constraint.recurrence)
        ]

    def remove_task(self, task_name: str) -> bool:
        """Remove the first task matching task_name. Returns True if a task was removed."""
        original = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.task_name != task_name]
        return len(self.tasks) < original


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)
    busy_blocks: list[str] = field(default_factory=list)  # e.g. ["09:00-10:00"]

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def add_busy_block(self, start: str, end: str) -> None:
        """Record a time range when the owner is unavailable (format: 'HH:MM')."""
        self.busy_blocks.append(f"{start}-{end}")

    def get_pet(self, name: str) -> Optional["Pet"]:
        """Return the pet with the given name, or None."""
        return next((p for p in self.pets if p.name == name), None)

    def get_available_slots(self) -> list[str]:
        """Return free time ranges across a standard day (07:00–21:00)."""
        day_start = _to_minutes("07:00")
        day_end   = _to_minutes("21:00")

        occupied = []
        for block in self.busy_blocks:
            s, e = block.split("-")
            occupied.append((_to_minutes(s), _to_minutes(e)))
        occupied.sort()

        free = []
        cursor = day_start
        for (s, e) in occupied:
            if cursor < s:
                free.append(f"{_to_time_str(cursor)}-{_to_time_str(s)}")
            cursor = max(cursor, e)
        if cursor < day_end:
            free.append(f"{_to_time_str(cursor)}-{_to_time_str(day_end)}")
        return free


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------

class DailyPlan:
    def __init__(self, date: str, pet_name: str = "") -> None:
        """Initialize an empty plan for the given date (format: 'YYYY-MM-DD')."""
        self.date = date
        self.pet_name = pet_name
        self.scheduled_tasks: list[PetCareTask] = []
        self.conflicts: list[str] = []
        self.reasoning: str = ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_slot_free(self, start: int, duration: int, occupied: list[tuple[int, int]]) -> bool:
        """Return True if the given start/duration range overlaps no occupied block."""
        end = start + duration
        return all(start >= be or end <= bs for bs, be in occupied)

    def _find_next_free(
        self,
        from_min: int,
        duration: int,
        occupied: list[tuple[int, int]],
        latest: int = _to_minutes("21:00"),
    ) -> Optional[int]:
        """Return the first start time >= from_min where a block of `duration` minutes fits, or None.

        Sorts `occupied` and jumps cursor to the end of each blocking interval,
        so the returned time may be any minute (not constrained to 15-min increments).
        Returns None if no gap fits before `latest`.
        """
        sorted_occ = sorted(occupied)
        cursor = from_min
        while cursor + duration <= latest:
            blocking = next(
                (e for s, e in sorted_occ if s < cursor + duration and e > cursor),
                None,
            )
            if blocking is None:
                return cursor
            cursor = blocking
        return None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, pet: Pet, owner: Owner) -> None:
        """Schedule all of pet's tasks and populate scheduled_tasks, reasoning, and conflicts.

        Tasks are processed fixed-time first, then in priority order. Owner busy blocks
        seed the occupied intervals. Fixed tasks go to their exact time if free, or the
        nearest available slot with a conflict logged. Preferred tasks fill their window
        or fall back to any free slot. Flexible tasks fill sequentially from 07:00.
        """
        self.scheduled_tasks = []
        self.conflicts = []
        reasons: list[str] = []

        # Fixed-time tasks first, then sort remaining by priority
        tasks = sorted(
            pet.get_tasks(),
            key=lambda t: (
                0 if t.constraint and t.constraint.type == "fixed" else 1,
                PRIORITY_ORDER.get(t.priority, 99),
            ),
        )

        # Seed occupied slots with owner's busy blocks
        occupied: list[tuple[int, int]] = []
        for block in owner.busy_blocks:
            s, e = block.split("-")
            occupied.append((_to_minutes(s), _to_minutes(e)))

        cursor = _to_minutes("07:00")  # rolling pointer for flexible tasks

        for task in tasks:
            c = task.constraint
            slot: Optional[int] = None

            if c and c.type == "fixed" and c.fixed_time:
                preferred = _to_minutes(c.fixed_time)
                if self._is_slot_free(preferred, task.duration_minutes, occupied):
                    slot = preferred
                    reasons.append(
                        f"{task.task_name}: fixed at {c.fixed_time} — {c.describe()}"
                    )
                else:
                    # Conflict: find nearest free slot and flag it
                    slot = self._find_next_free(preferred, task.duration_minutes, occupied)
                    if slot is None:
                        slot = self._find_next_free(_to_minutes("07:00"), task.duration_minutes, occupied)
                    if slot is not None:
                        msg = (
                            f"{task.task_name}: wanted {c.fixed_time} but conflict — "
                            f"moved to {_to_time_str(slot)}"
                        )
                        reasons.append(msg)
                        self.conflicts.append(msg)

            elif c and c.type == "preferred" and c.preferred_window in WINDOWS:
                win_start, win_end = WINDOWS[c.preferred_window]
                slot = self._find_next_free(
                    _to_minutes(win_start), task.duration_minutes, occupied, _to_minutes(win_end)
                )
                if slot is not None:
                    reasons.append(
                        f"{task.task_name}: scheduled at {_to_time_str(slot)} "
                        f"({c.preferred_window} preference)"
                    )
                else:
                    # Preferred window full — fall back to any free slot
                    slot = self._find_next_free(cursor, task.duration_minutes, occupied)
                    if slot is not None:
                        msg = (
                            f"{task.task_name}: preferred {c.preferred_window} was full — "
                            f"placed at {_to_time_str(slot)}"
                        )
                        reasons.append(msg)
                        self.conflicts.append(msg)

            else:
                # Flexible: place at the next open slot after the rolling cursor
                slot = self._find_next_free(cursor, task.duration_minutes, occupied)
                if slot is not None:
                    reasons.append(
                        f"{task.task_name}: no constraint — placed at {_to_time_str(slot)}"
                    )

            if slot is not None:
                task.scheduled_time = _to_time_str(slot)
                occupied.append((slot, slot + task.duration_minutes))
                cursor = max(cursor, slot + task.duration_minutes)
                self.scheduled_tasks.append(task)

        self.reasoning = "\n".join(reasons)

    def edit_task(self, task: PetCareTask, new_time: str) -> None:
        """Move a scheduled task to a new start time."""
        if task in self.scheduled_tasks:
            task.scheduled_time = new_time

    def get_overlapping_tasks(self) -> list[str]:
        """Return warning strings for any tasks in this plan whose time ranges overlap.

        Uses half-open interval math: two tasks [a_start, a_end) and [b_start, b_end)
        overlap when a_start < b_end AND b_start < a_end.
        Never raises — callers receive warnings, not exceptions.
        """
        warnings: list[str] = []
        tasks = [t for t in self.scheduled_tasks if t.scheduled_time]
        for i, a in enumerate(tasks):
            a_start = _to_minutes(a.scheduled_time)
            a_end   = a_start + a.duration_minutes
            for b in tasks[i + 1:]:
                b_start = _to_minutes(b.scheduled_time)
                b_end   = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"WARNING: '{a.task_name}' "
                        f"({a.scheduled_time}–{_to_time_str(a_end)}) overlaps "
                        f"'{b.task_name}' ({b.scheduled_time}–{_to_time_str(b_end)})"
                    )
        return warnings

    def get_tasks_sorted(self) -> list[PetCareTask]:
        """Return scheduled tasks in chronological order."""
        return sorted(
            self.scheduled_tasks,
            key=lambda t: _to_minutes(t.scheduled_time or "23:59"),
        )

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
    ) -> list[PetCareTask]:
        """Return scheduled tasks matching the given filters (None = no filter)."""
        result = self.scheduled_tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if priority is not None:
            result = [t for t in result if t.priority == priority]
        return result

    def display(self) -> str:
        """Return a formatted schedule string with tasks in chronological order via get_tasks_sorted(),
        followed by scheduling reasoning and any conflicts."""
        if not self.scheduled_tasks:
            return f"No plan generated for {self.date}."

        lines = [f"Daily Plan — {self.date}", "=" * 32]
        for task in self.get_tasks_sorted():
            end = _to_time_str(_to_minutes(task.scheduled_time) + task.duration_minutes)
            lines.append(
                f"  {task.scheduled_time} – {end}  {task.task_name} [{task.priority} priority]"
            )
        lines += ["", "Reasoning:", self.reasoning]
        if self.conflicts:
            lines += ["", "Conflicts:", *[f"  ! {c}" for c in self.conflicts]]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Multi-day scheduling
# ---------------------------------------------------------------------------

def generate_week(pet: Pet, owner: Owner, start_date: str, days: int = 7) -> list[DailyPlan]:
    """Return one DailyPlan per day, replaying recurring tasks on days after the first."""
    plans: list[DailyPlan] = []
    base = datetime.date.fromisoformat(start_date)
    for i in range(days):
        date_str = (base + datetime.timedelta(days=i)).isoformat()
        plan = DailyPlan(date=date_str, pet_name=pet.name)
        if i == 0:
            plan.generate(pet=pet, owner=owner)
        else:
            # Only recurring tasks repeat on subsequent days
            day_pet = Pet(name=pet.name, species=pet.species, breed=pet.breed, age=pet.age)
            for task in pet.get_recurring_tasks():
                fresh = copy.copy(task)
                fresh.scheduled_time = None
                fresh.completed = False
                day_pet.add_task(fresh)
            plan.generate(pet=day_pet, owner=owner)
        plans.append(plan)
    return plans


def detect_conflicts(plans: list[DailyPlan]) -> list[str]:
    """Return warning strings for tasks that overlap across any of the given plans.

    Each plan should have pet_name set so warnings identify which pet owns each task.
    Same-plan pairs are skipped (identified by list position) to avoid duplicating
    warnings already surfaced by DailyPlan.get_overlapping_tasks(). Passing the same
    DailyPlan object at two different positions will treat them as separate plans.
    Never raises — callers receive warnings, not exceptions.
    """
    warnings: list[str] = []

    # Build a flat list of (plan_index, label, task) preserving which plan each task came from
    labeled: list[tuple[int, str, PetCareTask]] = [
        (idx, plan.pet_name or plan.date, task)
        for idx, plan in enumerate(plans)
        for task in plan.scheduled_tasks
        if task.scheduled_time
    ]

    # Check every cross-plan pair — same plan_index means same plan, skip to avoid
    # double-reporting tasks already caught by get_overlapping_tasks()
    for i, (idx_a, label_a, a) in enumerate(labeled):
        a_start = _to_minutes(a.scheduled_time)
        a_end   = a_start + a.duration_minutes
        for idx_b, label_b, b in labeled[i + 1:]:
            if idx_a == idx_b:
                continue  # same plan — skip
            b_start = _to_minutes(b.scheduled_time)
            b_end   = b_start + b.duration_minutes
            if a_start < b_end and b_start < a_end:
                warnings.append(
                    f"WARNING: [{label_a}] '{a.task_name}' "
                    f"({a.scheduled_time}–{_to_time_str(a_end)}) overlaps "
                    f"[{label_b}] '{b.task_name}' "
                    f"({b.scheduled_time}–{_to_time_str(b_end)})"
                )
    return warnings
