from datetime import date
from pawpal_system import Category, Owner, Pet, Priority, Recurrence, Scheduler, Task

# =============================================================================
# HAPPY PATH — two pets, shared owner, real schedule output
# =============================================================================

owner = Owner("Jordan", available_minutes=120, preferences=["morning", "morning"])  # dup pref intentional

buddy = Pet("Buddy", "dog", age=3)
luna  = Pet("Luna",  "cat", age=2, special_needs=["anxiety"])

buddy_tasks = [
    Task("Morning Walk",    duration_minutes=30, priority=Priority.HIGH,   category=Category.ACTIVITY, time_of_day="morning"),
    Task("Fetch Playtime",  duration_minutes=20, priority=Priority.MEDIUM, category=Category.ACTIVITY, time_of_day="afternoon"),
    Task("Evening Feeding", duration_minutes=10, priority=Priority.HIGH,   category=Category.FEEDING,  time_of_day="evening"),
]

luna_tasks = [
    Task("Morning Feeding",    duration_minutes=10, priority=Priority.HIGH,   category=Category.FEEDING,  time_of_day="morning"),
    Task("Enrichment Puzzle",  duration_minutes=15, priority=Priority.MEDIUM, category=Category.CARE,     time_of_day="afternoon"),
    Task("Evening Grooming",   duration_minutes=10, priority=Priority.LOW,    category=Category.CARE,     time_of_day="evening"),
]

scheduler_buddy = Scheduler(buddy, owner)
for task in buddy_tasks:
    scheduler_buddy.add_task(task)
scheduler_buddy.generate_plan()
print(scheduler_buddy.explain_plan())

print()

scheduler_luna = Scheduler(luna, owner)
for task in luna_tasks:
    scheduler_luna.add_task(task)
scheduler_luna.generate_plan()
print(scheduler_luna.explain_plan())


# =============================================================================
# SORTING — tasks added deliberately out of chronological order
# =============================================================================

print("\n--- Sorting Demo ---\n")

owner2 = Owner("Alex", available_minutes=180)
pet2   = Pet("Rex", "dog", age=5)

# Added in random order — evening first, then morning, then afternoon
out_of_order_tasks = [
    Task("Evening Meds",     duration_minutes=5,  priority=Priority.HIGH,   category=Category.CARE,     start_time="19:30"),
    Task("Lunch Walk",       duration_minutes=25, priority=Priority.MEDIUM, category=Category.ACTIVITY, start_time="12:15"),
    Task("Morning Feeding",  duration_minutes=10, priority=Priority.HIGH,   category=Category.FEEDING,  start_time="07:00"),
    Task("Afternoon Play",   duration_minutes=20, priority=Priority.LOW,    category=Category.ACTIVITY, start_time="14:45"),
    Task("Early Grooming",   duration_minutes=15, priority=Priority.MEDIUM, category=Category.CARE,     start_time="08:30"),
]

sched2 = Scheduler(pet2, owner2)
for t in out_of_order_tasks:
    sched2.add_task(t)

print("Added order:")
for t in out_of_order_tasks:
    print(f"  {t.start_time}  {t.name}")

print("\nSorted by start_time (HH:MM lambda key):")
for t in sched2.sort_by_time():
    print(f"  {t.start_time}  {t.name}")

# Mix of HH:MM and label-based tasks to show fallback
print("\nSorted with label fallback (no start_time tasks):")
owner3 = Owner("Sam", available_minutes=90)
pet3   = Pet("Pip", "cat", age=1)
mixed_tasks = [
    Task("Evening Brush",   duration_minutes=10, priority=Priority.LOW,    category=Category.CARE,     time_of_day="evening"),
    Task("Morning Feed",    duration_minutes=10, priority=Priority.HIGH,   category=Category.FEEDING,  start_time="07:30"),
    Task("Afternoon Nap",   duration_minutes=30, priority=Priority.LOW,    category=Category.ACTIVITY, time_of_day="afternoon"),
    Task("Mid-morning Med", duration_minutes=5,  priority=Priority.HIGH,   category=Category.CARE,     start_time="10:00"),
]
sched3 = Scheduler(pet3, owner3)
for t in mixed_tasks:
    sched3.add_task(t)
for t in sched3.sort_by_time():
    slot = t.start_time if t.start_time else f"({t.time_of_day})"
    print(f"  {slot:<15}  {t.name}")


# =============================================================================
# FILTERING — by category, priority, and completion status
# =============================================================================

print("\n--- Filtering Demo ---\n")

# Mark one task complete to test completed filter
out_of_order_tasks[2].mark_complete()   # Morning Feeding marked done

print("All tasks:")
for t in sched2.filter_tasks():
    print(f"  [{t.category.value:<8}] [{t.priority.value:<6}] {'done' if t.completed else '----'}  {t.name}")

print("\nFilter — category=CARE:")
for t in sched2.filter_tasks(category=Category.CARE):
    print(f"  {t.name}")

print("\nFilter — priority=HIGH:")
for t in sched2.filter_tasks(priority=Priority.HIGH):
    print(f"  {t.name}")

print("\nFilter — completed=False (incomplete only):")
for t in sched2.filter_tasks(completed=False):
    print(f"  {t.name}")

print("\nFilter — completed=True (done tasks):")
for t in sched2.filter_tasks(completed=True):
    print(f"  {t.name}")

print("\nFilter — priority=HIGH + completed=False (high priority, not yet done):")
for t in sched2.filter_tasks(priority=Priority.HIGH, completed=False):
    print(f"  {t.name}")


# =============================================================================
# RECURRING TASKS — complete_task() auto-generates the next occurrence
# =============================================================================

print("\n--- Recurring Tasks Demo ---\n")

rec_owner = Owner("Jordan", available_minutes=120)
rec_pet   = Pet("Buddy", "dog", age=3)
rec_sched = Scheduler(rec_pet, rec_owner)

today = date.today()

daily_walk = Task(
    "Morning Walk",
    duration_minutes=30,
    priority=Priority.HIGH,
    category=Category.ACTIVITY,
    time_of_day="morning",
    recurrence=Recurrence.DAILY,
    due_date=today,
)
weekly_groom = Task(
    "Grooming Session",
    duration_minutes=20,
    priority=Priority.MEDIUM,
    category=Category.CARE,
    time_of_day="afternoon",
    recurrence=Recurrence.WEEKLY,
    due_date=today,
)
one_off_vet = Task(
    "Vet Checkup",
    duration_minutes=60,
    priority=Priority.HIGH,
    category=Category.CARE,
    recurrence=Recurrence.NONE,
    due_date=today,
)

for t in (daily_walk, weekly_groom, one_off_vet):
    rec_sched.add_task(t)

print(f"Tasks before completing anything: {rec_sched.task_count}")

# Complete the daily walk — should auto-register tomorrow's occurrence
next_walk = rec_sched.complete_task(daily_walk)
print(f"\nCompleted: {daily_walk}")
print(f"Next occurrence: {next_walk}")
print(f"Tasks after completing daily walk: {rec_sched.task_count}  (was 3, now 4)")

# Complete the weekly groom — should auto-register next week's occurrence
next_groom = rec_sched.complete_task(weekly_groom)
print(f"\nCompleted: {weekly_groom}")
print(f"Next occurrence: {next_groom}")
print(f"Tasks after completing weekly groom: {rec_sched.task_count}  (was 4, now 5)")

# Complete the one-off vet visit — should NOT generate a next occurrence
next_vet = rec_sched.complete_task(one_off_vet)
print(f"\nCompleted: {one_off_vet}")
print(f"Next occurrence: {next_vet}  (expected None — one-off task)")
print(f"Tasks after completing one-off: {rec_sched.task_count}  (stays 5)")

# Verify dates are correct using timedelta
from datetime import timedelta
assert next_walk.due_date  == today + timedelta(days=1),  "Daily: due date should be today + 1"
assert next_groom.due_date == today + timedelta(weeks=1), "Weekly: due date should be today + 7"
assert next_vet is None,                                  "One-off: should return None"
print("\n[PASS] All recurrence due dates verified with timedelta")

# Regenerate plan — should now include the next occurrences
rec_sched.generate_plan()
print(f"\nRegenerated plan ({len(rec_sched._plan)} tasks scheduled):")
for t in rec_sched._plan:
    rec_str = f" [{t.recurrence.value}]" if t.recurrence != Recurrence.NONE else ""
    print(f"  {t.name}{rec_str}  due {t.due_date}  ({'done' if t.completed else 'pending'})")


# =============================================================================
# CONFLICT DETECTION — detect_conflicts() returns warnings, never crashes
# =============================================================================

print("\n--- Conflict Detection Demo ---\n")

conf_owner = Owner("Jordan", available_minutes=180)
conf_pet   = Pet("Buddy", "dog", age=3)
conf_sched = Scheduler(conf_pet, conf_owner)

# Two tasks with overlapping precise start_time windows
morning_walk  = Task("Morning Walk",    duration_minutes=30, priority=Priority.HIGH,   category=Category.ACTIVITY, start_time="08:00")
morning_meds  = Task("Morning Meds",    duration_minutes=10, priority=Priority.HIGH,   category=Category.CARE,     start_time="08:15")  # starts inside walk window
afternoon_run = Task("Afternoon Run",   duration_minutes=20, priority=Priority.MEDIUM, category=Category.ACTIVITY, start_time="13:00")  # no conflict
evening_feed  = Task("Evening Feeding", duration_minutes=10, priority=Priority.HIGH,   category=Category.FEEDING,  start_time="18:00")
evening_brush = Task("Evening Brush",   duration_minutes=15, priority=Priority.LOW,    category=Category.CARE,     start_time="18:05")  # overlaps with evening_feed

# Two tasks sharing the same time_of_day label (slot collision)
nap1 = Task("Rest Period",   duration_minutes=20, priority=Priority.LOW, category=Category.ACTIVITY, time_of_day="afternoon")
nap2 = Task("Puzzle Game",   duration_minutes=15, priority=Priority.LOW, category=Category.ACTIVITY, time_of_day="afternoon")

for t in (morning_walk, morning_meds, afternoon_run, evening_feed, evening_brush, nap1, nap2):
    conf_sched.add_task(t)

conflicts = conf_sched.detect_conflicts()

if conflicts:
    print(f"Found {len(conflicts)} conflict(s):")
    for w in conflicts:
        print(f"  {w}")
else:
    print("No conflicts detected.")

# Verify specific conflicts were caught
assert any("Morning Walk" in w and "Morning Meds" in w for w in conflicts),    "Expected Walk vs Meds conflict"
assert any("Evening Feeding" in w and "Evening Brush" in w for w in conflicts), "Expected Feeding vs Brush conflict"
assert any("Rest Period" in w and "Puzzle Game" in w for w in conflicts),       "Expected afternoon slot collision"
assert not any("Afternoon Run" in w for w in conflicts),                         "Afternoon Run should have no conflict"
print("\n[PASS] All expected conflicts detected, non-conflicting task clear")

# Confirm detect_conflicts() does NOT raise — it only warns
print("\nCompleting 'Morning Walk' and re-checking (completed tasks excluded):")
conf_sched.complete_task(morning_walk)
conflicts_after = conf_sched.detect_conflicts()
print(f"  Conflicts remaining: {len(conflicts_after)}")
assert not any("Morning Walk" in w for w in conflicts_after), "Completed task should not appear in conflicts"
print("[PASS] Completed tasks are excluded from conflict detection")


# =============================================================================
# EDGE CASE TESTS — intentionally break things, verify correct errors
# =============================================================================

print("\n--- Edge Case Tests ---\n")

# 1. Duplicate task — same object added twice
try:
    scheduler_buddy.add_task(buddy_tasks[0])
    print("[FAIL] Duplicate task was not caught")
except ValueError as e:
    print(f"[PASS] Duplicate task: {e}")

# 2. Owner with zero available minutes
try:
    Owner("Ghost", available_minutes=0)
    print("[FAIL] Zero minutes was not caught")
except ValueError as e:
    print(f"[PASS] Zero minutes: {e}")

# 3. Owner with negative available minutes
try:
    Owner("Ghost", available_minutes=-30)
    print("[FAIL] Negative minutes was not caught")
except ValueError as e:
    print(f"[PASS] Negative minutes: {e}")

# 4. explain_plan() called before generate_plan()
try:
    fresh = Scheduler(buddy, owner)
    fresh.add_task(buddy_tasks[0])
    fresh.explain_plan()
    print("[FAIL] explain before generate was not caught")
except RuntimeError as e:
    print(f"[PASS] explain before generate: {e}")

# 5. All tasks exceed the available time budget — plan is valid but empty
tiny_owner  = Owner("Tiny", available_minutes=5)
long_task   = Task("Long Hike", duration_minutes=180, priority=Priority.HIGH, category=Category.ACTIVITY)
tight_sched = Scheduler(buddy, tiny_owner)
tight_sched.add_task(long_task)
tight_sched.generate_plan()
print(f"[PASS] All tasks over budget:\n{tight_sched.explain_plan()}\n")

# 6. Pet with negative age
try:
    Pet("Ghost", "dog", age=-1)
    print("[FAIL] Negative age was not caught")
except ValueError as e:
    print(f"[PASS] Negative pet age: {e}")

# 7. Task with blank name
try:
    Task("   ", duration_minutes=10, priority=Priority.LOW, category=Category.ACTIVITY)
    print("[FAIL] Blank task name was not caught")
except ValueError as e:
    print(f"[PASS] Blank task name: {e}")

# 8. Task with zero duration
try:
    Task("Zero", duration_minutes=0, priority=Priority.LOW, category=Category.ACTIVITY)
    print("[FAIL] Zero duration was not caught")
except ValueError as e:
    print(f"[PASS] Zero duration: {e}")

# 9. generate_plan() with no tasks added
try:
    empty_sched = Scheduler(buddy, owner)
    empty_sched.generate_plan()
    print("[FAIL] Empty task list was not caught")
except ValueError as e:
    print(f"[PASS] Empty task list: {e}")

# 10. Verify duplicate preferences are silently de-duped on Owner
o = Owner("Jordan", available_minutes=60, preferences=["morning", "morning", "evening"])
print(f"[PASS] De-duped preferences: {o.preferences}")

# 11. Invalid start_time format
try:
    Task("Bad time", duration_minutes=10, priority=Priority.LOW, category=Category.ACTIVITY, start_time="9:5")
    print("[FAIL] Bad start_time format was not caught")
except ValueError as e:
    print(f"[PASS] Bad start_time format: {e}")

# 12. Out-of-range start_time
try:
    Task("Bad time", duration_minutes=10, priority=Priority.LOW, category=Category.ACTIVITY, start_time="25:00")
    print("[FAIL] Out-of-range start_time was not caught")
except ValueError as e:
    print(f"[PASS] Out-of-range start_time: {e}")
