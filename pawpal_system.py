import re
from dataclasses import dataclass, field
from datetime import date, timedelta
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


class Recurrence(Enum):
    """How often a task repeats."""
    NONE   = "none"
    DAILY  = "daily"
    WEEKLY = "weekly"


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
    time_of_day: Optional[str] = None        # "morning", "afternoon", "evening" — label-based ordering
    start_time: Optional[str] = None         # "HH:MM" — precise time, takes priority over time_of_day in sort
    recurrence: Recurrence = Recurrence.NONE # how often the task repeats
    due_date: Optional[date] = None          # date this occurrence is due; None means unscheduled
    completed: bool = False

    def __post_init__(self):
        """Validate name, duration, and start_time format."""
        if not self.name.strip():
            raise ValueError("Task name cannot be empty")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        if self.start_time is not None:
            if not re.match(r"^\d{2}:\d{2}$", self.start_time):
                raise ValueError(f"start_time must be in HH:MM format, got {self.start_time!r}")
            h, m = map(int, self.start_time.split(":"))
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError(f"start_time {self.start_time!r} is not a valid time")

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed and return the next occurrence, or None for one-off tasks."""
        self.completed = True
        if self.recurrence == Recurrence.NONE:
            return None
        _delta = {Recurrence.DAILY: timedelta(days=1), Recurrence.WEEKLY: timedelta(weeks=1)}
        next_due = (self.due_date or date.today()) + _delta[self.recurrence]
        return Task(
            name=self.name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            time_of_day=self.time_of_day,
            start_time=self.start_time,
            recurrence=self.recurrence,
            due_date=next_due,
        )

    def is_high_priority(self) -> bool:
        """Return True if this task has HIGH priority."""
        return self.priority == Priority.HIGH

    def __repr__(self) -> str:
        """Return a readable string representation of the task."""
        tod  = f", {self.time_of_day}" if self.time_of_day else ""
        done = ", done" if self.completed else ""
        rec  = f", {self.recurrence.value}" if self.recurrence != Recurrence.NONE else ""
        due  = f", due {self.due_date}" if self.due_date else ""
        return f"Task({self.name!r}, {self.duration_minutes}min, {self.priority.value}{tod}{rec}{due}{done})"


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

    def sort_by_time(self) -> List[Task]:
        """Return all registered tasks sorted chronologically.

        Tasks with a precise start_time (HH:MM) are sorted by that value.
        Tasks with only a time_of_day label fall back to the slot's start time
        (morning=06:00, afternoon=12:00, evening=18:00).
        Tasks with no time information sort last (treated as 23:59).
        Does not modify the internal task list.
        """
        _label_fallback = {"morning": "06:00", "afternoon": "12:00", "evening": "18:00"}
        return sorted(
            self._tasks,
            key=lambda t: t.start_time if t.start_time else _label_fallback.get(t.time_of_day, "23:59")
        )

    def filter_tasks(
        self,
        category: Optional[Category] = None,
        priority: Optional[Priority] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Return a filtered subset of registered tasks.

        All parameters are optional and combinable. Passing None for a parameter
        skips that filter entirely.

        Args:
            category:  Keep only tasks matching this Category enum value.
            priority:  Keep only tasks matching this Priority enum value.
            completed: True returns only completed tasks; False returns only pending tasks.

        Returns:
            A new list of Task objects that match all provided filters.
        """
        result: List[Task] = self._tasks
        if category is not None:
            result = [t for t in result if t.category == category]
        if priority is not None:
            result = [t for t in result if t.priority == priority]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler, raising ValueError on duplicates."""
        if task in self._tasks:
            raise ValueError(f"Task '{task.name}' has already been added")
        self._tasks.append(task)

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and auto-register the next occurrence for recurring tasks; returns it or None."""
        if task not in self._tasks:
            raise ValueError(f"Task '{task.name}' is not registered with this scheduler")
        next_occurrence = task.mark_complete()  # Task handles the timedelta logic
        if next_occurrence is not None:
            self._tasks.append(next_occurrence)  # auto-register — no duplicate risk (new object)
        self._plan_generated = False  # plan is stale; caller must regenerate
        return next_occurrence

    # Slot label → (slot_start_HH:MM, slot_end_HH:MM) — class-level so it isn't rebuilt each call
    _SLOT_RANGE = {"morning": ("06:00", "12:00"), "afternoon": ("12:00", "18:00"), "evening": ("18:00", "23:00")}

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert HH:MM string to minutes since midnight."""
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    def _task_window(self, task: Task) -> Optional[tuple]:
        """Return (start_min, end_min) for a task, or None if no time info is available."""
        if task.start_time:
            s = self._to_minutes(task.start_time)
            return (s, s + task.duration_minutes)
        if task.time_of_day in self._SLOT_RANGE:
            s = self._to_minutes(self._SLOT_RANGE[task.time_of_day][0])
            return (s, s + task.duration_minutes)
        return None

    def detect_conflicts(self) -> List[str]:
        """Return warning strings for tasks whose time windows overlap; never raises."""
        warnings: List[str] = []
        active = [t for t in self._tasks if not t.completed]

        # Check every pair once (i < j avoids duplicate warnings)
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                a, b = active[i], active[j]
                wa, wb = self._task_window(a), self._task_window(b)

                if wa is None or wb is None:
                    continue  # no time info on one task — can't determine conflict

                a_start, a_end = wa
                b_start, b_end = wb

                if a_start < b_end and b_start < a_end:  # standard interval overlap test
                    warnings.append(
                        f"CONFLICT: '{a.name}' and '{b.name}' overlap "
                        f"({a.start_time or a.time_of_day} vs {b.start_time or b.time_of_day})"
                    )

        return warnings

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
