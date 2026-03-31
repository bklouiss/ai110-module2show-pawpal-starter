import pytest
from datetime import date, timedelta
from pawpal_system import Category, Owner, Pet, Priority, Recurrence, Scheduler, Task


# ---------------------------------------------------------------------------
# Fixtures
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
# add_task — happy paths
# ---------------------------------------------------------------------------

def test_add_task_increases_count(basic_pet, basic_owner, high_task, medium_task):
    """Each add_task() call must increase the scheduler's task count by one."""
    scheduler = Scheduler(basic_pet, basic_owner)
    assert scheduler.task_count == 0
    scheduler.add_task(high_task)
    assert scheduler.task_count == 1
    scheduler.add_task(medium_task)
    assert scheduler.task_count == 2

def test_add_task_with_start_time(basic_pet, basic_owner):
    """Task with a valid start_time should be added without error."""
    task = Task("Meds", duration_minutes=5, priority=Priority.HIGH, category=Category.CARE, start_time="08:30")
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(task)
    assert scheduler.task_count == 1

def test_add_task_with_recurrence(basic_pet, basic_owner):
    """Task with recurrence set should be added without error."""
    task = Task("Daily Walk", duration_minutes=20, priority=Priority.HIGH, category=Category.ACTIVITY,
                recurrence=Recurrence.DAILY, due_date=date.today())
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(task)
    assert scheduler.task_count == 1


# ---------------------------------------------------------------------------
# add_task — edge cases
# ---------------------------------------------------------------------------

def test_add_task_duplicate_raises(basic_pet, basic_owner, high_task):
    """add_task() must raise ValueError when the same task object is added twice."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    with pytest.raises(ValueError, match="already been added"):
        scheduler.add_task(high_task)

def test_add_task_same_name_different_object(basic_pet, basic_owner):
    """Two distinct Task objects with the same name are not duplicates — both should be accepted."""
    t1 = Task("Walk", duration_minutes=20, priority=Priority.HIGH, category=Category.ACTIVITY)
    t2 = Task("Walk", duration_minutes=20, priority=Priority.HIGH, category=Category.ACTIVITY)
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert scheduler.task_count == 2


# ---------------------------------------------------------------------------
# complete_task — happy paths
# ---------------------------------------------------------------------------

def test_complete_task_daily_due_date_increments_by_one_day(basic_pet, basic_owner):
    """complete_task() on a DAILY task must set next due_date to today + 1 day."""
    today = date.today()
    task = Task("Daily Walk", duration_minutes=20, priority=Priority.HIGH, category=Category.ACTIVITY,
                recurrence=Recurrence.DAILY, due_date=today)
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(task)
    next_task = scheduler.complete_task(task)
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)

def test_complete_task_weekly_due_date_increments_by_seven_days(basic_pet, basic_owner):
    """complete_task() on a WEEKLY task must set next due_date to today + 7 days."""
    today = date.today()
    task = Task("Weekly Groom", duration_minutes=20, priority=Priority.MEDIUM, category=Category.CARE,
                recurrence=Recurrence.WEEKLY, due_date=today)
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(task)
    next_task = scheduler.complete_task(task)
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)

def test_complete_task_one_off_returns_none(basic_pet, basic_owner, high_task):
    """complete_task() on a NONE-recurrence task must return None."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    result = scheduler.complete_task(high_task)
    assert result is None

def test_complete_task_one_off_count_unchanged(basic_pet, basic_owner, high_task, medium_task):
    """Completing a one-off task must not change the task count."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    scheduler.add_task(medium_task)
    scheduler.complete_task(high_task)
    assert scheduler.task_count == 2  # no new task added

def test_complete_task_recurring_auto_registers_next(basic_pet, basic_owner):
    """Completing a recurring task must automatically add the next occurrence to the scheduler."""
    task = Task("Daily Walk", duration_minutes=20, priority=Priority.HIGH, category=Category.ACTIVITY,
                recurrence=Recurrence.DAILY, due_date=date.today())
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(task)
    assert scheduler.task_count == 1
    scheduler.complete_task(task)
    assert scheduler.task_count == 2  # original + next occurrence


# ---------------------------------------------------------------------------
# complete_task — edge cases
# ---------------------------------------------------------------------------

def test_complete_task_marks_original_as_done(basic_pet, basic_owner, high_task):
    """The original task object must be marked completed after complete_task()."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    scheduler.complete_task(high_task)
    assert high_task.completed is True

def test_complete_task_next_occurrence_starts_incomplete(basic_pet, basic_owner):
    """The next occurrence returned by complete_task() must not be pre-marked as completed."""
    task = Task("Daily Walk", duration_minutes=20, priority=Priority.HIGH, category=Category.ACTIVITY,
                recurrence=Recurrence.DAILY, due_date=date.today())
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(task)
    next_task = scheduler.complete_task(task)
    assert next_task.completed is False

def test_complete_task_invalidates_plan(basic_pet, basic_owner, high_task):
    """complete_task() must reset _plan_generated so explain_plan() raises until regenerated."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    scheduler.generate_plan()
    scheduler.complete_task(high_task)
    with pytest.raises(RuntimeError, match="generate_plan"):
        scheduler.explain_plan()

def test_complete_task_unregistered_raises(basic_pet, basic_owner):
    """complete_task() must raise ValueError for a task not registered with this scheduler."""
    foreign = Task("Unknown", duration_minutes=10, priority=Priority.LOW, category=Category.CARE)
    scheduler = Scheduler(basic_pet, basic_owner)
    with pytest.raises(ValueError, match="is not registered"):
        scheduler.complete_task(foreign)

def test_complete_task_no_due_date_falls_back_to_today(basic_pet, basic_owner):
    """Recurring task with no due_date must compute next occurrence relative to today."""
    task = Task("Daily Walk", duration_minutes=20, priority=Priority.HIGH, category=Category.ACTIVITY,
                recurrence=Recurrence.DAILY)  # no due_date
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(task)
    next_task = scheduler.complete_task(task)
    assert next_task.due_date == date.today() + timedelta(days=1)


# ---------------------------------------------------------------------------
# filter_tasks — happy paths
# ---------------------------------------------------------------------------

def test_filter_by_category_returns_only_matching(basic_pet, basic_owner, high_task, medium_task, low_task):
    """filter_tasks(category=CARE) must return only CARE tasks."""
    scheduler = Scheduler(basic_pet, basic_owner)
    for t in (high_task, medium_task, low_task):
        scheduler.add_task(t)
    result = scheduler.filter_tasks(category=Category.CARE)
    assert all(t.category == Category.CARE for t in result)
    assert high_task not in result  # ACTIVITY — excluded

def test_filter_by_priority_returns_only_matching(basic_pet, basic_owner, high_task, medium_task, low_task):
    """filter_tasks(priority=HIGH) must return only HIGH priority tasks."""
    scheduler = Scheduler(basic_pet, basic_owner)
    for t in (high_task, medium_task, low_task):
        scheduler.add_task(t)
    result = scheduler.filter_tasks(priority=Priority.HIGH)
    assert result == [high_task]

def test_filter_by_completed_false(basic_pet, basic_owner, high_task, medium_task):
    """filter_tasks(completed=False) must exclude completed tasks."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    scheduler.add_task(medium_task)
    scheduler.complete_task(high_task)
    result = scheduler.filter_tasks(completed=False)
    assert high_task not in result
    assert medium_task in result

def test_filter_by_completed_true(basic_pet, basic_owner, high_task, medium_task):
    """filter_tasks(completed=True) must return only completed tasks."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    scheduler.add_task(medium_task)
    scheduler.complete_task(high_task)
    result = scheduler.filter_tasks(completed=True)
    assert result == [high_task]

def test_filter_combined_priority_and_completed(basic_pet, basic_owner, high_task, medium_task, low_task):
    """filter_tasks with multiple params must satisfy all conditions."""
    scheduler = Scheduler(basic_pet, basic_owner)
    for t in (high_task, medium_task, low_task):
        scheduler.add_task(t)
    scheduler.complete_task(high_task)
    result = scheduler.filter_tasks(priority=Priority.HIGH, completed=False)
    assert result == []  # high_task is done; no other HIGH tasks

def test_filter_no_params_returns_all(basic_pet, basic_owner, high_task, medium_task, low_task):
    """filter_tasks() with no arguments must return all registered tasks."""
    scheduler = Scheduler(basic_pet, basic_owner)
    for t in (high_task, medium_task, low_task):
        scheduler.add_task(t)
    assert scheduler.filter_tasks() == [high_task, medium_task, low_task]


# ---------------------------------------------------------------------------
# filter_tasks — edge cases
# ---------------------------------------------------------------------------

def test_filter_no_match_returns_empty_list(basic_pet, basic_owner, high_task):
    """filter_tasks() with no matching tasks must return [] not raise."""
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    result = scheduler.filter_tasks(category=Category.FEEDING)
    assert result == []

def test_filter_on_empty_scheduler_returns_empty(basic_pet, basic_owner):
    """filter_tasks() on a scheduler with no tasks must return []."""
    scheduler = Scheduler(basic_pet, basic_owner)
    assert scheduler.filter_tasks(priority=Priority.HIGH) == []


# ---------------------------------------------------------------------------
# sort_by_time — happy paths
# ---------------------------------------------------------------------------

def test_sort_by_time_precise_start_times(basic_pet, basic_owner):
    """Tasks with start_time must be sorted chronologically by HH:MM."""
    evening = Task("Evening Meds",  duration_minutes=5,  priority=Priority.HIGH, category=Category.CARE,     start_time="19:30")
    morning = Task("Morning Walk",  duration_minutes=30, priority=Priority.HIGH, category=Category.ACTIVITY, start_time="07:00")
    midday  = Task("Lunch Feeding", duration_minutes=10, priority=Priority.HIGH, category=Category.FEEDING,  start_time="12:15")
    scheduler = Scheduler(basic_pet, basic_owner)
    for t in (evening, morning, midday):
        scheduler.add_task(t)
    sorted_tasks = scheduler.sort_by_time()
    assert sorted_tasks == [morning, midday, evening]

def test_sort_by_time_label_fallback(basic_pet, basic_owner):
    """Tasks with only time_of_day labels must sort in morning < afternoon < evening order."""
    eve  = Task("Evening Brush",  duration_minutes=10, priority=Priority.LOW,  category=Category.CARE,     time_of_day="evening")
    morn = Task("Morning Feed",   duration_minutes=10, priority=Priority.HIGH, category=Category.FEEDING,  time_of_day="morning")
    aft  = Task("Afternoon Play", duration_minutes=20, priority=Priority.LOW,  category=Category.ACTIVITY, time_of_day="afternoon")
    scheduler = Scheduler(basic_pet, basic_owner)
    for t in (eve, morn, aft):
        scheduler.add_task(t)
    sorted_tasks = scheduler.sort_by_time()
    assert sorted_tasks == [morn, aft, eve]


# ---------------------------------------------------------------------------
# sort_by_time — edge cases
# ---------------------------------------------------------------------------

def test_sort_by_time_no_time_info_sorts_last(basic_pet, basic_owner):
    """Tasks with no time_of_day and no start_time must appear at the end."""
    morning = Task("Morning Walk", duration_minutes=20, priority=Priority.HIGH, category=Category.ACTIVITY, start_time="07:00")
    no_time = Task("Anytime Task", duration_minutes=10, priority=Priority.LOW,  category=Category.CARE)
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(no_time)   # added first
    scheduler.add_task(morning)
    sorted_tasks = scheduler.sort_by_time()
    assert sorted_tasks[-1] == no_time

def test_sort_by_time_mixed_precise_and_label(basic_pet, basic_owner):
    """Precise start_time tasks must sort correctly against time_of_day label tasks."""
    label_afternoon = Task("Afternoon Play", duration_minutes=20, priority=Priority.LOW, category=Category.ACTIVITY, time_of_day="afternoon")
    precise_early   = Task("Early Meds",     duration_minutes=5,  priority=Priority.HIGH, category=Category.CARE,    start_time="10:00")
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(label_afternoon)
    scheduler.add_task(precise_early)
    sorted_tasks = scheduler.sort_by_time()
    # 10:00 < 12:00 (afternoon fallback) — precise_early must come first
    assert sorted_tasks.index(precise_early) < sorted_tasks.index(label_afternoon)

def test_sort_by_time_does_not_mutate_internal_order(basic_pet, basic_owner, high_task, medium_task, low_task):
    """sort_by_time() must return a new sorted list without modifying _tasks order."""
    scheduler = Scheduler(basic_pet, basic_owner)
    for t in (high_task, medium_task, low_task):
        scheduler.add_task(t)
    original_count = scheduler.task_count
    scheduler.sort_by_time()
    # Internal list unchanged — verify by checking count and filter still works normally
    assert scheduler.task_count == original_count
    assert scheduler.filter_tasks()[0] == high_task  # insertion order preserved


# ---------------------------------------------------------------------------
# detect_conflicts — conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_overlapping_start_times(basic_pet, basic_owner):
    """Two tasks whose HH:MM windows overlap must produce exactly one conflict warning."""
    walk = Task("Morning Walk", duration_minutes=30, priority=Priority.HIGH, category=Category.ACTIVITY, start_time="08:00")
    meds = Task("Morning Meds", duration_minutes=10, priority=Priority.HIGH, category=Category.CARE,     start_time="08:15")
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(walk)
    scheduler.add_task(meds)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "Morning Walk" in conflicts[0]
    assert "Morning Meds" in conflicts[0]

def test_detect_conflicts_same_time_of_day_label(basic_pet, basic_owner):
    """Two tasks sharing the same time_of_day label must be flagged as a conflict."""
    t1 = Task("Rest",    duration_minutes=20, priority=Priority.LOW, category=Category.ACTIVITY, time_of_day="afternoon")
    t2 = Task("Feeding", duration_minutes=10, priority=Priority.HIGH, category=Category.FEEDING,  time_of_day="afternoon")
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1

def test_detect_conflicts_no_overlap_returns_empty(basic_pet, basic_owner):
    """Tasks in non-overlapping time windows must produce no warnings."""
    morning = Task("Morning Walk",   duration_minutes=30, priority=Priority.HIGH,   category=Category.ACTIVITY, start_time="07:00")
    evening = Task("Evening Feeding",duration_minutes=10, priority=Priority.HIGH,   category=Category.FEEDING,  start_time="18:00")
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(morning)
    scheduler.add_task(evening)
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_adjacent_tasks_do_not_conflict(basic_pet, basic_owner):
    """A task ending exactly when the next one starts must NOT be flagged (touching, not overlapping)."""
    walk  = Task("Walk",    duration_minutes=30, priority=Priority.HIGH, category=Category.ACTIVITY, start_time="08:00")  # ends 08:30
    feeding = Task("Feeding", duration_minutes=10, priority=Priority.HIGH, category=Category.FEEDING,  start_time="08:30")  # starts 08:30
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(walk)
    scheduler.add_task(feeding)
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_completed_tasks_excluded(basic_pet, basic_owner):
    """Completed tasks must not be included in conflict detection."""
    walk = Task("Morning Walk", duration_minutes=30, priority=Priority.HIGH, category=Category.ACTIVITY, start_time="08:00")
    meds = Task("Morning Meds", duration_minutes=10, priority=Priority.HIGH, category=Category.CARE,     start_time="08:15")
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(walk)
    scheduler.add_task(meds)
    scheduler.complete_task(walk)  # remove walk from active set
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_multiple_conflicts(basic_pet, basic_owner):
    """Multiple overlapping pairs must each produce their own warning."""
    t1 = Task("Task A", duration_minutes=60, priority=Priority.HIGH,   category=Category.ACTIVITY, start_time="08:00")
    t2 = Task("Task B", duration_minutes=30, priority=Priority.MEDIUM, category=Category.CARE,     start_time="08:30")
    t3 = Task("Task C", duration_minutes=20, priority=Priority.LOW,    category=Category.FEEDING,  start_time="08:45")
    scheduler = Scheduler(basic_pet, basic_owner)
    for t in (t1, t2, t3):
        scheduler.add_task(t)
    conflicts = scheduler.detect_conflicts()
    # A overlaps B, A overlaps C, B overlaps C — 3 pairs
    assert len(conflicts) == 3

def test_detect_conflicts_no_time_info_ignored(basic_pet, basic_owner):
    """Tasks with no time information must be silently skipped — not falsely flagged."""
    t1 = Task("Anytime Task 1", duration_minutes=30, priority=Priority.HIGH, category=Category.ACTIVITY)
    t2 = Task("Anytime Task 2", duration_minutes=30, priority=Priority.HIGH, category=Category.CARE)
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_never_raises_on_empty_scheduler(basic_pet, basic_owner):
    """detect_conflicts() on a scheduler with no tasks must return [] without raising."""
    scheduler = Scheduler(basic_pet, basic_owner)
    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Previously existing tests (Phase 3 required + scheduling + guard cases)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status(high_task):
    """mark_complete() must flip completed from False to True."""
    assert high_task.completed is False
    high_task.mark_complete()
    assert high_task.completed is True

def test_is_high_priority_true_for_high(high_task):
    assert high_task.is_high_priority() is True

def test_is_high_priority_false_for_medium(medium_task):
    assert medium_task.is_high_priority() is False

def test_is_high_priority_false_for_low(low_task):
    assert low_task.is_high_priority() is False

def test_generate_plan_respects_time_budget(basic_pet, high_task, medium_task):
    tight_owner = Owner("Tight", available_minutes=30)
    scheduler = Scheduler(basic_pet, tight_owner)
    scheduler.add_task(high_task)
    scheduler.add_task(medium_task)
    plan = scheduler.generate_plan()
    assert high_task in plan
    assert medium_task not in plan

def test_generate_plan_all_tasks_over_budget(basic_pet):
    tiny_owner = Owner("Tiny", available_minutes=5)
    big_task = Task("Long Hike", duration_minutes=180, priority=Priority.HIGH, category=Category.ACTIVITY)
    scheduler = Scheduler(basic_pet, tiny_owner)
    scheduler.add_task(big_task)
    assert scheduler.generate_plan() == []

def test_generate_plan_orders_high_before_low(basic_pet, basic_owner, high_task, low_task):
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(low_task)
    scheduler.add_task(high_task)
    plan = scheduler.generate_plan()
    assert plan.index(high_task) < plan.index(low_task)

def test_special_needs_boosts_care_task(pet_with_needs, basic_owner):
    activity = Task("Play",        duration_minutes=20, priority=Priority.MEDIUM, category=Category.ACTIVITY)
    care     = Task("Anxiety Med", duration_minutes=10, priority=Priority.MEDIUM, category=Category.CARE)
    scheduler = Scheduler(pet_with_needs, basic_owner)
    scheduler.add_task(activity)
    scheduler.add_task(care)
    plan = scheduler.generate_plan()
    assert plan.index(care) < plan.index(activity)

def test_explain_plan_before_generate_raises(basic_pet, basic_owner, high_task):
    scheduler = Scheduler(basic_pet, basic_owner)
    scheduler.add_task(high_task)
    with pytest.raises(RuntimeError, match="generate_plan"):
        scheduler.explain_plan()

def test_generate_plan_with_no_tasks_raises(basic_pet, basic_owner):
    with pytest.raises(ValueError, match="No tasks added"):
        Scheduler(basic_pet, basic_owner).generate_plan()

def test_owner_zero_minutes_raises():
    with pytest.raises(ValueError):
        Owner("Bad", available_minutes=0)

def test_pet_negative_age_raises():
    with pytest.raises(ValueError):
        Pet("Ghost", "dog", age=-1)

def test_task_zero_duration_raises():
    with pytest.raises(ValueError):
        Task("Zero", duration_minutes=0, priority=Priority.LOW, category=Category.ACTIVITY)

def test_owner_deduplicates_preferences():
    owner = Owner("Jordan", available_minutes=60, preferences=["morning", "morning", "evening"])
    assert owner.preferences == ["morning", "evening"]
