import pytest
from pawpal_system import Category, Owner, Pet, Priority, Scheduler, Task


# ---------------------------------------------------------------------------
# Fixtures — shared objects reused across tests
# ---------------------------------------------------------------------------

@pytest.fixture
def basic_owner():
    return Owner("Jordan", available_minutes=120)

@pytest.fixture
def basic_pet():
    return Pet("Buddy", "dog", age=3)

@pytest.fixture
def pet_with_needs():
    return Pet("Luna", "cat", age=2, special_needs=["anxiety"])

@pytest.fixture
def high_task():
    return Task("Morning Walk", duration_minutes=30, priority=Priority.HIGH, category=Category.ACTIVITY, time_of_day="morning")

@pytest.fixture
def medium_task():
    return Task("Enrichment", duration_minutes=15, priority=Priority.MEDIUM, category=Category.CARE, time_of_day="afternoon")

@pytest.fixture
def low_task():
    return Task("Brushing", duration_minutes=10, priority=Priority.LOW, category=Category.CARE, time_of_day="evening")


# ---------------------------------------------------------------------------
# Step 3 required tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status(high_task):
    """mark_complete() must flip completed from False to True."""
    assert high_task.completed is False
    high_task.mark_complete()
    assert high_task.completed is True

def test_add_task_increases_count(basic_pet, basic_owner, high_task, medium_task):
    """Each add_task() call must increase the scheduler's task count by one."""
    scheduler = Scheduler(basic_pet, basic_owner)
    assert scheduler.task_count == 0
    scheduler.add_task(high_task)
    assert scheduler.task_count == 1
    scheduler.add_task(medium_task)
    assert scheduler.task_count == 2


# ---------------------------------------------------------------------------
# Priority and category logic
# ---------------------------------------------------------------------------

def test_is_high_priority_true_for_high(high_task):
    """is_high_priority() returns True only when priority is HIGH."""
    assert high_task.is_high_priority() is True

def test_is_high_priority_false_for_medium(medium_task):
    """is_high_priority() returns False for MEDIUM priority."""
    assert medium_task.is_high_priority() is False

def test_is_high_priority_false_for_low(low_task):
    """is_high_priority() returns False for LOW priority."""
    assert low_task.is_high_priority() is False


# ---------------------------------------------------------------------------
# Scheduling — time budget
# ---------------------------------------------------------------------------

def test_generate_plan_respects_time_budget(basic_pet, high_task, medium_task):
    """Tasks whose total duration exceeds available_minutes must be excluded from the plan."""
    tight_owner = Owner("Tight", available_minutes=30)  # exactly fits one 30-min task
    scheduler = Scheduler(basic_pet, tight_owner)
    scheduler.add_task(high_task)   # 30 min — fits
    scheduler.add_task(medium_task) # 15 min — would exceed budget
    plan = scheduler.generate_plan()
    assert high_task in plan
    assert medium_task not in plan

def test_generate_plan_all_tasks_over_budget(basic_pet, basic_owner):
    """Plan must be empty (not raise) when every task exceeds available time."""
    tiny_owner = Owner("Tiny", available_minutes=5)
    big_task = Task("Long Hike", duration_minutes=180, priority=Priority.HIGH, category=Category.ACTIVITY)
    scheduler = Scheduler(basic_pet, tiny_owner)
    scheduler.add_task(big_task)
    plan = scheduler.generate_plan()
    assert plan == []

def test_generate_plan_orders_high_before_low(basic_pet, basic_owner, high_task, low_task):
    """HIGH priority tasks must appear before LOW priority tasks in the plan."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(low_task)   # added first
    scheduler.add_task(high_task)  # added second
    plan = scheduler.generate_plan()
    assert plan.index(high_task) < plan.index(low_task)


# ---------------------------------------------------------------------------
# Special needs priority boost
# ---------------------------------------------------------------------------

def test_special_needs_boosts_care_task(pet_with_needs, basic_owner):
    """A CARE task for a pet with special_needs must be scheduled before a same-priority ACTIVITY task."""
    activity = Task("Play", duration_minutes=20, priority=Priority.MEDIUM, category=Category.ACTIVITY)
    care     = Task("Anxiety Med", duration_minutes=10, priority=Priority.MEDIUM, category=Category.CARE)
    scheduler = Scheduler(pet_with_needs, basic_owner)
    scheduler.add_task(activity)  # added first
    scheduler.add_task(care)      # added second — should be boosted ahead
    plan = scheduler.generate_plan()
    assert plan.index(care) < plan.index(activity)


# ---------------------------------------------------------------------------
# Guard / error cases
# ---------------------------------------------------------------------------

def test_duplicate_task_raises(basic_pet, basic_owner, high_task):
    """add_task() must raise ValueError when the same task object is added twice."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    with pytest.raises(ValueError, match="already been added"):
        scheduler.add_task(high_task)

def test_explain_plan_before_generate_raises(basic_pet, basic_owner, high_task):
    """explain_plan() must raise RuntimeError if generate_plan() has not been called."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    with pytest.raises(RuntimeError, match="generate_plan"):
        scheduler.explain_plan()

def test_generate_plan_with_no_tasks_raises(basic_pet, basic_owner):
    """generate_plan() must raise ValueError when no tasks have been added."""
    scheduler = Scheduler(basic_pet, basic_owner)
    with pytest.raises(ValueError, match="No tasks added"):
        scheduler.generate_plan()

def test_owner_zero_minutes_raises():
    """Owner must raise ValueError when available_minutes is zero."""
    with pytest.raises(ValueError):
        Owner("Bad", available_minutes=0)

def test_pet_negative_age_raises():
    """Pet must raise ValueError when age is negative."""
    with pytest.raises(ValueError):
        Pet("Ghost", "dog", age=-1)

def test_task_zero_duration_raises():
    """Task must raise ValueError when duration_minutes is zero."""
    with pytest.raises(ValueError):
        Task("Zero", duration_minutes=0, priority=Priority.LOW, category=Category.ACTIVITY)

def test_owner_deduplicates_preferences():
    """Owner must silently remove duplicate entries from preferences."""
    owner = Owner("Jordan", available_minutes=60, preferences=["morning", "morning", "evening"])
    assert owner.preferences == ["morning", "evening"]
