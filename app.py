import streamlit as st
from pawpal_system import Category, Owner, Pet, Priority, Recurrence, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("Daily pet care planner — build a schedule, catch conflicts, track recurring tasks.")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "owner"    not in st.session_state: st.session_state.owner    = None
if "pet"      not in st.session_state: st.session_state.pet      = None
if "tasks"    not in st.session_state: st.session_state.tasks    = []
if "schedule" not in st.session_state: st.session_state.schedule = None

_priority_map  = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
_category_map  = {"activity": Category.ACTIVITY, "care": Category.CARE, "feeding": Category.FEEDING}
_recurrence_map = {"none": Recurrence.NONE, "daily": Recurrence.DAILY, "weekly": Recurrence.WEEKLY}

# ---------------------------------------------------------------------------
# Helper — build a temporary Scheduler from session state (read-only, no side effects)
# ---------------------------------------------------------------------------
def _build_temp_scheduler() -> Scheduler | None:
    """Return a Scheduler loaded with current session tasks, or None if owner/pet missing."""
    if st.session_state.owner is None or st.session_state.pet is None:
        return None
    s = Scheduler(st.session_state.pet, st.session_state.owner)
    for t in st.session_state.tasks:
        s.add_task(t)
    return s

# ---------------------------------------------------------------------------
# Owner + Pet — side by side
# ---------------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Owner Info")
    owner_name        = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Available minutes today", min_value=1, max_value=1440, value=120)
    if st.button("Save Owner", use_container_width=True):
        if not owner_name.strip():
            st.error("Owner name cannot be empty.")
        else:
            try:
                st.session_state.owner    = Owner(owner_name.strip(), available_minutes=int(available_minutes))
                st.session_state.schedule = None
                st.success(f"Saved: {st.session_state.owner}")
            except ValueError as e:
                st.error(str(e))
    if st.session_state.owner:
        st.info(f"Current owner: {st.session_state.owner}")
    else:
        st.caption("No owner saved yet.")

with right:
    st.subheader("Pet Info")
    pet_name          = st.text_input("Pet name", value="Mochi")
    c1, c2            = st.columns(2)
    with c1: species  = st.selectbox("Species", ["dog", "cat", "other"])
    with c2: pet_age  = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    special_needs_input = st.text_input("Special needs (comma-separated, optional)", value="")
    if st.button("Save Pet", use_container_width=True):
        if not pet_name.strip():
            st.error("Pet name cannot be empty.")
        else:
            try:
                special_needs = [s.strip() for s in special_needs_input.split(",") if s.strip()]
                st.session_state.pet      = Pet(pet_name.strip(), species, age=int(pet_age), special_needs=special_needs)
                st.session_state.tasks    = []
                st.session_state.schedule = None
                st.success(f"Saved: {st.session_state.pet}. Task list cleared.")
            except ValueError as e:
                st.error(str(e))
    if st.session_state.pet:
        st.info(f"Current pet: {st.session_state.pet}")
    else:
        st.caption("No pet saved yet.")

st.divider()

# ---------------------------------------------------------------------------
# Task input form
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

c1, c2, c3, c4 = st.columns(4)
with c1: task_title    = st.text_input("Task name", value="Morning walk")
with c2: duration      = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with c3: priority_str  = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with c4: category_str  = st.selectbox("Category", ["activity", "care", "feeding"])

c5, c6, c7 = st.columns(3)
with c5: time_of_day_str = st.selectbox("Time of day", ["(none)", "morning", "afternoon", "evening"])
with c6: start_time_str  = st.text_input("Start time (HH:MM, optional)", value="", placeholder="e.g. 08:30")
with c7: recurrence_str  = st.selectbox("Recurrence", ["none", "daily", "weekly"])

col_add, col_clear = st.columns([3, 1])
with col_add:
    if st.button("Add task", use_container_width=True):
        if not task_title.strip():
            st.error("Task name cannot be empty.")
        elif any(t.name == task_title.strip() for t in st.session_state.tasks):
            st.error(f"'{task_title}' has already been added.")
        else:
            tod        = None if time_of_day_str == "(none)" else time_of_day_str
            start_time = start_time_str.strip() if start_time_str.strip() else None
            try:
                new_task = Task(
                    name=task_title.strip(),
                    duration_minutes=int(duration),
                    priority=_priority_map[priority_str],
                    category=_category_map[category_str],
                    time_of_day=tod,
                    start_time=start_time,
                    recurrence=_recurrence_map[recurrence_str],
                )
                st.session_state.tasks.append(new_task)
                st.session_state.schedule = None
                st.success(f"Added '{new_task.name}'.")
            except ValueError as e:
                st.error(str(e))

with col_clear:
    if st.button("Clear all tasks", use_container_width=True):
        st.session_state.tasks    = []
        st.session_state.schedule = None

# ---------------------------------------------------------------------------
# Task list — sorted by time using Scheduler.sort_by_time()
# ---------------------------------------------------------------------------
if st.session_state.tasks:
    temp = _build_temp_scheduler()

    # Live conflict detection — shown as soon as tasks are entered, before scheduling
    if temp:
        conflicts = temp.detect_conflicts()
        if conflicts:
            st.markdown("**Scheduling conflicts detected in your task list:**")
            for w in conflicts:
                # Strip the "CONFLICT: " prefix for cleaner UI display
                st.warning(w.replace("CONFLICT: ", ""))

    # Display sorted by time
    sorted_tasks = temp.sort_by_time() if temp else st.session_state.tasks
    st.markdown(f"**Current tasks** ({len(sorted_tasks)} total, sorted by time):")
    st.table(
        [
            {
                "Name": t.name,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority.value,
                "Category": t.category.value,
                "Start time": t.start_time or "—",
                "Time of day": t.time_of_day or "—",
                "Recurrence": t.recurrence.value if t.recurrence != Recurrence.NONE else "—",
            }
            for t in sorted_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary", use_container_width=True):
    if st.session_state.owner is None:
        st.error("No owner saved — fill in Owner Info and click Save Owner.")
    elif st.session_state.pet is None:
        st.error("No pet saved — fill in Pet Info and click Save Pet.")
    elif not st.session_state.tasks:
        st.error("Add at least one task before generating a schedule.")
    else:
        try:
            scheduler = Scheduler(st.session_state.pet, st.session_state.owner)
            for task in st.session_state.tasks:
                scheduler.add_task(task)
            plan        = scheduler.generate_plan()
            explanation = scheduler.explain_plan()
            conflicts   = scheduler.detect_conflicts()
            skipped     = scheduler._skipped

            st.session_state.schedule = {
                "plan":        plan,
                "explanation": explanation,
                "conflicts":   conflicts,
                "skipped":     skipped,
            }
        except ValueError as e:
            st.error(f"Could not build schedule: {e}")

# ---------------------------------------------------------------------------
# Schedule output — persists across reruns via session_state
# ---------------------------------------------------------------------------
if st.session_state.schedule:
    plan      = st.session_state.schedule["plan"]
    conflicts = st.session_state.schedule["conflicts"]
    skipped   = st.session_state.schedule["skipped"]

    # 1. Conflict warnings — shown first, most prominent
    if conflicts:
        st.markdown("### Conflicts in this schedule")
        st.caption("These tasks overlap. Consider adjusting their times or removing one.")
        for w in conflicts:
            st.warning(w.replace("CONFLICT: ", ""))

    # 2. Scheduled tasks
    if plan:
        st.success(f"Schedule ready — {len(plan)} task(s) planned for {st.session_state.pet.name}.")
        st.table(
            [
                {
                    "Name": t.name,
                    "Start time": t.start_time or (t.time_of_day or "—"),
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.value,
                    "Category": t.category.value,
                    "Recurrence": t.recurrence.value if t.recurrence != Recurrence.NONE else "—",
                }
                for t in plan
            ]
        )
        total = sum(t.duration_minutes for t in plan)
        budget = st.session_state.owner.available_minutes
        st.progress(min(total / budget, 1.0), text=f"Time used: {total} / {budget} min")
    else:
        st.warning("No tasks fit within the available time budget.")

    # 3. Skipped tasks — shown as a secondary warning
    if skipped:
        with st.expander(f"Skipped tasks ({len(skipped)} over budget)"):
            st.table(
                [
                    {
                        "Name": t.name,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority.value,
                    }
                    for t in skipped
                ]
            )

    # 4. Full text explanation
    with st.expander("Full schedule explanation"):
        st.text(st.session_state.schedule["explanation"])
