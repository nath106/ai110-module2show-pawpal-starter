# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
    Owner and Pet Information
    - Take in basic owner and pet info

    Pet Care Task
    - Be able to add pet care tasks
    - Hold the information of each task
    Constraints
    - Task priority/constraints such as meds being at a certain time everyday or grooming appointments
    - Owner has preference for when certain task should be done such as only wanting walks in the morning
    - Owner can time block parts of day when they are busy with other tasks.

    Daily Plan
    - Produced a clean plan based on constraints and priorities
    - Explain reasoning behind plan
    - Be able to edit plan (MAYBE)

- Briefly describe your initial UML design.

- What classes did you include, and what responsibilities did you assign to each?
    The classes I included were DailyPlan, Owner, Pet, PetCareTask, and Constraints.
    Class: DailyPlan
    Responsibilites: Generate plan, edit plan, and display plan.
    Class: Owner
    Responsibilites: Add a pet, add a busy block, and get available slots.
    Class: Pet
    Responsibilites: Add and get tasks.
    Class: Pet Care Task
    Responsibilites: set constraints and get duration.
    Class: Constraint
    Responsibilites: Determine if its timed satisfied and a description of the constraint.

**b. Design changes**

- Did your design change during implementation? Yes
- If yes, describe at least one change and why you made it.
    The change I made was to add the Constraint class. I did this because it will allow the user to reuse the same constraint objects across multiple tasks. For example, if medication needs to be done during feeding, then the fixed time can be used in making the scheduling logic in daily plan easier to query cleanly.



---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
