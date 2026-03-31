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

The main use of AI besides generating code, was mainly breaking the code to test edge cases and also having a partner to converse with to make sure I am not overthinking but also to test my ideas to see what I liked compared to what it proposed and refine the ideas throughout the process.

- What kinds of prompts or questions were most helpful?

My main prompt was analyze my request structured prompts or the goal is to break the code stype prompts to test edge cases and also think about my request before generating anything so I can atune the response it generates to fit what I actually want for it.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

When I was prompting it for my UML the main point was verifying variables and relationships. I didn't like the automatically generated fields and verified what variables and methods needed to be private versus public.

- How did you evaluate or verify what the AI suggested?

I had it go back and analyze future relationships between how variables should interact and looked at it's suggestions and constaintly verified the class relationships/interactions and variable access.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I wanted to test the behaviors of the Scheduler Class to make sure it properly handled the addition of tasks.

- Why were these tests important?

These tests were important to make sure that the scheduler functions as planned so that was extra tasks aren't added and tasks don't conflict with one another

**b. Confidence**

- How confident are you that your scheduler works correctly?

I feel pretty confident in my edge cases with my scheduler working well

- What edge cases would you test next if you had more time?

If I had more time I would check to verify appointment interactions to make sure they don't conflict but also make sure real time updates work

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am happy with the edge cases functionality.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I think I would redesign the UI. I understand the assignment uses streamlit for the UI functionality but I would reoganize it so that the schedule lived on a seperate page

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that there is a need to constantly check and test for edge cases and especially with information sensitive projects, perform injections to see where there are security vulnerablilities to make sure important information is safe.