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
    is_recurring: bool = False

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
        if self.type == "fixed":
            suffix = " (recurring daily)" if self.is_recurring else ""
            return f"Must happen at {self.fixed_time}{suffix}"
        if self.type == "preferred":
            return f"Preferred in the {self.preferred_window}"
        return "Flexible timing"


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
    completed: bool = False

    def set_constraint(self, c: Constraint) -> None:
        """Attach a constraint to this task."""
        self.constraint = c

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        return self.duration_minutes

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


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
    def __init__(self, date: str) -> None:
        """Initialize an empty plan for the given date (format: 'YYYY-MM-DD')."""
        self.date = date
        self.scheduled_tasks: list[PetCareTask] = []
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
        """Scan forward in 15-minute steps and return the first free start time, or None."""
        cursor = from_min
        while cursor + duration <= latest:
            if self._is_slot_free(cursor, duration, occupied):
                return cursor
            cursor += 15  # advance in 15-minute steps
        return None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, pet: Pet, owner: Owner) -> None:
        """Schedule all pet tasks respecting fixed times, preferred windows, and owner busy blocks."""
        self.scheduled_tasks = []
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
                        reasons.append(
                            f"{task.task_name}: wanted {c.fixed_time} but conflict — "
                            f"moved to {_to_time_str(slot)}"
                        )

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
                        reasons.append(
                            f"{task.task_name}: preferred {c.preferred_window} was full — "
                            f"placed at {_to_time_str(slot)}"
                        )

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

    def display(self) -> str:
        """Return a formatted schedule with reasoning."""
        if not self.scheduled_tasks:
            return f"No plan generated for {self.date}."

        by_time = sorted(
            self.scheduled_tasks,
            key=lambda t: _to_minutes(t.scheduled_time or "23:59"),
        )
        lines = [f"Daily Plan — {self.date}", "=" * 32]
        for task in by_time:
            end = _to_time_str(_to_minutes(task.scheduled_time) + task.duration_minutes)
            lines.append(
                f"  {task.scheduled_time} – {end}  {task.task_name} [{task.priority} priority]"
            )
        lines += ["", "Reasoning:", self.reasoning]
        return "\n".join(lines)
