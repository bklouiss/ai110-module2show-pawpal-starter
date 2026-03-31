# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Phase 4 extended the core `Scheduler` class with four algorithmic improvements:

**Sorting** — `sort_by_time()` orders tasks chronologically using a precise `start_time` field (`HH:MM`) as the primary key, falling back to `time_of_day` slot labels (`morning`, `afternoon`, `evening`) when no precise time is set. Tasks with no time information sort last.

**Filtering** — `filter_tasks(category, priority, completed)` returns a subset of tasks matching any combination of filters. All parameters are optional — pass only what you need. Useful for showing the owner only high-priority incomplete tasks, or only care tasks for a specific pet.

**Recurring tasks** — `Task` now has a `recurrence` field (`NONE`, `DAILY`, `WEEKLY`) and a `due_date`. Calling `Scheduler.complete_task(task)` marks the task done and automatically registers the next occurrence using Python's `timedelta` (`+1 day` for daily, `+7 days` for weekly). One-off tasks return `None`.

**Conflict detection** — `detect_conflicts()` scans all incomplete tasks pairwise and returns a list of human-readable warning strings for any whose time windows overlap. Uses the standard interval overlap test (`a_start < b_end and b_start < a_end`). Never raises — warnings are returned, not thrown, so the UI can display them without crashing.

## Testing PawPal+

### Running the tests

```bash
python -m pytest
```

Or for verbose output showing each test name:

```bash
python -m pytest tests/ -v
```

### What the tests cover

The test suite (`tests/test_pawpal.py`) contains **50 tests** across five areas:

| Area | Tests | What is verified |
|---|---|---|
| `add_task` | 5 | Count increments, tasks with start_time/recurrence accepted, duplicate same-object rejected, same-name different-object allowed |
| `complete_task` | 8 | Daily +1 day, weekly +7 days, one-off returns None, next occurrence auto-registered and starts incomplete, plan invalidated after completion, unregistered task raises |
| `filter_tasks` | 8 | Filter by category, priority, and completed status individually and combined; no-match returns empty list without raising |
| `sort_by_time` | 5 | Precise HH:MM chronological order, time_of_day label fallback, no-time-info sorts last, mixed precise+label, does not mutate internal task order |
| `detect_conflicts` | 8 | Overlapping start_time windows flagged, same time_of_day label flagged, adjacent (touching) tasks not flagged, completed tasks excluded, multiple pairs each produce their own warning, no-time-info tasks silently skipped |
| Scheduling & guards | 16 | Time budget respected, priority ordering, special-needs boost, empty plan without crash, all guard clauses (duplicate, wrong call order, zero/negative inputs) |

### Confidence level

**4 / 5 stars**

The core scheduling logic, recurring task generation, sorting, filtering, and conflict detection are all well-covered with both happy-path and edge-case tests. One test (`test_add_task_same_name_different_object`) caught a real bug during development — the duplicate guard was comparing by value instead of identity, which would have silently blocked valid use cases. The main gap is integration-level testing between `pawpal_system.py` and `app.py` (the Streamlit UI layer is not tested), and there are no tests for concurrent or multi-pet scenarios.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
