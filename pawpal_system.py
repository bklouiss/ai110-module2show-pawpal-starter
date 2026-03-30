from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        pass


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: str        # "low", "medium", "high"
    category: str        # "activity", "care", "feeding"

    def is_high_priority(self) -> bool:
        pass

    def __repr__(self) -> str:
        pass


class Scheduler:
    def __init__(self, pet: Pet, available_minutes: int) -> None:
        self._pet: Pet = pet
        self.available_minutes: int = available_minutes
        self._tasks: List[Task] = []
        self._plan: List[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def generate_plan(self) -> List[Task]:
        pass

    def explain_plan(self) -> str:
        pass
