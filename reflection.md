# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design consists of an Tasks class, a Pet class, and a Scheduler class. The task class handles any task such as walks, meds, etc. A Pet class to handle names, ages, types, and info like illnesses. And finally a Scheduler Class that can handler the constraints and display an ordered plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The main design change from the inital was accounting for the edgecases for example in the cases of duplicate classes, accounting for accessing certain methods before data is entered, etc. Claude helped analyze potential parts where guards should be added.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses a greedy algorithm: it sorts tasks by priority and fills the day one task at a time, stopping when a task won't fit in the remaining time. This means it never backtracks or tries alternate combinations. For example, if a 60-minute HIGH priority task is scheduled first and uses most of the budget, three shorter HIGH priority tasks that would have collectively fit are skipped entirely — even though skipping the single long task would have been the better outcome for the pet.

This tradeoff is reasonable for a daily pet care planner because the number of tasks is small (typically under 15 per day), and the owner can see the skipped tasks listed in the output and manually adjust. Implementing an optimal scheduler (such as 0/1 knapsack) would add significant complexity for a marginal gain in a low-stakes, single-user context. The greedy approach is also more predictable — the owner can reason about why the schedule looks the way it does without needing to understand combinatorial optimization.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
