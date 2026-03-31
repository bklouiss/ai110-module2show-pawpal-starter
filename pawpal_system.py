from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Priority(Enum):
    """Urgency levels for a task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Category(Enum):
    """Broad type of pet care task."""
    ACTIVITY = "activity"
    CARE = "care"
    FEEDING = "feeding"


@dataclass
class Pet:
    """Represents the pet being cared for."""
    name: str
    species: str
    age: int
    special_needs: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate name is non-blank and age is non-negative."""
        if not self.name.strip():
            raise ValueError("Pet name cannot be empty")
        if self.age < 0:
            raise ValueError("Pet age cannot be negative")

    def __repr__(self) -> str:
        """Return a readable string representation of the pet."""
        needs = f", needs={self.special_needs}" if self.special_needs else ""
        return f"Pet({self.name!r}, {self.species}, age={self.age}{needs})"


@dataclass
class Task:
    """A single pet care task with duration, priority, and category."""
    name: str
    duration_minutes: int
    priority: Priority
    category: Category
    time_of_day: Optional[str] = None  # "morning", "afternoon", "evening" — used for ordering
    completed: bool = False

    def __post_init__(self):
        """Validate name is non-blank and duration is positive."""
        if not self.name.strip():
            raise ValueError("Task name cannot be empty")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task has HIGH priority."""
        return self.priority == Priority.HIGH

    def __repr__(self) -> str:
        """Return a readable string representation of the task."""
        tod = f", {self.time_of_day}" if self.time_of_day else ""
        done = ", done" if self.completed else ""
        return f"Task({self.name!r}, {self.duration_minutes}min, {self.priority.value}{tod}{done})"


@dataclass
class Owner:
    """Represents the pet owner with their time constraints and preferences."""
    name: str
    available_minutes: int
    preferences: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate name, available time, and de-duplicate preferences."""
        if not self.name.strip():
            raise ValueError("Owner name cannot be empty")
        if self.available_minutes <= 0:
            raise ValueError("available_minutes must be greater than 0")
        self.preferences = list(dict.fromkeys(self.preferences))

    def __repr__(self) -> str:
        """Return a readable string representation of the owner."""
        return f"Owner({self.name!r}, {self.available_minutes}min available)"


class Scheduler:
    """Builds and explains a daily care plan for one pet based on tasks and owner constraints."""

    def __init__(self, pet: Pet, owner: Owner) -> None:
        """Initialise the scheduler with a pet and an owner."""
        self._pet: Pet = pet
        self._owner: Owner = owner
        self._tasks: List[Task] = []
        self._plan: List[Task] = []
        self._skipped: List[Task] = []
        self._plan_generated: bool = False

    @property
    def task_count(self) -> int:
        """Return the number of tasks currently registered with this scheduler."""
        return len(self._tasks)

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler, raising ValueError on duplicates."""
        if task in self._tasks:
            raise ValueError(f"Task '{task.name}' has already been added")
        self._tasks.append(task)

    def generate_plan(self) -> List[Task]:
        """Sort and greedily schedule tasks within the owner's available time, respecting pet special needs."""
        if not self._tasks:
            raise ValueError("No tasks added — call add_task() at least once before generating a plan")

        priority_rank = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        time_rank = {"morning": 0, "afternoon": 1, "evening": 2}

        def sort_key(task: Task):
            """Compute sort key, boosting CARE/FEEDING for pets with special needs."""
            rank = priority_rank[task.priority]
            if self._pet.special_needs and task.category in (Category.CARE, Category.FEEDING):
                rank = max(0, rank - 1)
            return (rank, time_rank.get(task.time_of_day, 3))

        sorted_tasks = sorted(self._tasks, key=sort_key)

        self._plan = []
        self._skipped = []
        remaining = self._owner.available_minutes

        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                self._plan.append(task)
                remaining -= task.duration_minutes
            else:
                self._skipped.append(task)

        self._plan_generated = True
        return self._plan

    def explain_plan(self) -> str:
        """Return a formatted schedule string; raises RuntimeError if generate_plan() has not been called."""
        if not self._plan_generated:
            raise RuntimeError("No plan generated yet — call generate_plan() first")

        lines = [
            f"Today's Schedule for {self._pet.name} (owner: {self._owner.name})",
            "=" * 50,
        ]

        if not self._plan:
            lines.append(f"  No tasks fit within {self._owner.available_minutes} available minutes.")
        else:
            total_used = 0
            for i, task in enumerate(self._plan, 1):
                tod = f" [{task.time_of_day}]" if task.time_of_day else ""
                flag = " !" if task.is_high_priority() else ""
                lines.append(
                    f"  {i}. {task.name}{tod} — {task.duration_minutes} min"
                    f"  ({task.category.value}){flag}"
                )
                total_used += task.duration_minutes
            lines.append("-" * 50)
            lines.append(f"  Time used: {total_used} / {self._owner.available_minutes} min")

        if self._skipped:
            lines.append(f"  Skipped (over budget): {[t.name for t in self._skipped]}")

        lines.append("=" * 50)
        return "\n".join(lines)
