from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Constraint:
    type: str                   # "fixed", "preferred", or "flexible"
    fixed_time: str = ""        # e.g. "08:00" for daily medication
    preferred_window: str = ""  # e.g. "morning", "afternoon", "evening"
    is_recurring: bool = False

    def is_time_satisfied(self, time: str) -> bool:
        pass

    def describe(self) -> str:
        pass


@dataclass
class PetCareTask:
    task_name: str
    duration_minutes: int
    priority: str                          # "high", "medium", or "low"
    constraint: Optional[Constraint] = None

    def set_constraint(self, c: Constraint) -> None:
        pass

    def get_duration(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[PetCareTask] = field(default_factory=list)

    def add_task(self, task: PetCareTask) -> None:
        pass

    def get_tasks(self) -> list[PetCareTask]:
        pass


@dataclass
class Owner:
    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)
    busy_blocks: list[str] = field(default_factory=list)  # e.g. ["09:00-10:00"]

    def add_pet(self, pet: Pet) -> None:
        pass

    def add_busy_block(self, start: str, end: str) -> None:
        pass

    def get_available_slots(self) -> list[str]:
        pass


class DailyPlan:
    def __init__(self, date: str) -> None:
        self.date = date
        self.scheduled_tasks: list[PetCareTask] = []
        self.reasoning: str = ""

    def generate(self, pet: Pet, owner: Owner) -> None:
        pass

    def edit_task(self, task: PetCareTask, new_time: str) -> None:
        pass

    def display(self) -> str:
        pass
