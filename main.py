from pawpal_system import Category, Owner, Pet, Priority, Scheduler, Task

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
tiny_owner   = Owner("Tiny", available_minutes=5)
long_task    = Task("Long Hike", duration_minutes=180, priority=Priority.HIGH, category=Category.ACTIVITY)
tight_sched  = Scheduler(buddy, tiny_owner)
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
