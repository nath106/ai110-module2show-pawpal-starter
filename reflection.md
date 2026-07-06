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
    The constraints that are considered are time, priority, and preference.
- How did you decide which constraints mattered most?
    Every task is scheduled around the users busy blocks. If a task is fixed time is during a busy block, then the task will be scheduled at the first avaliable time. Preferred task are scheduled around fixed-time task, and flexable task are scheduled in any avalible spots. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    One tradeoff this scheduler makes is prioritizing time-efficiency rather than the overall apperence of the schedule. Before, the _find_next_free would advance by 15 minutes on every overlap. Now, if a busy block ends at 2:23, then the task could be scheduled at 2:23. 
- Why is that tradeoff reasonable for this scenario?
    This tradeoff is reasonable because it gives the user the ability to create a structured and detailed schedule. If the user know they get home at a certain time, then they can immedietly do the task that is needed. The busy blocks are designed to block out any time the user knows they can't do a certain task, so the times that are avalible for the schedular should be times that the user knows they will be able to do the task.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    I used AI tools mostly for debugging and refactoring. For design brainstorming, I did it by myself and then got input from the AI tool to see what other classes I could add. I also used AI to help me with streamlit, since I'm not very familiar with it.
- What kinds of prompts or questions were most helpful?
    The most helpful promts where the ones where I asked it to explain concepts or asking for help when I got stuck. Something that was also helpful was separating chat sessions by phases/topics. It helped when going to document features and changes.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    I decided to not accept an "edit_task" feature and opted for a "remove_task" feature instead.
- How did you evaluate or verify what the AI suggested?
    I made sure to read any explanation or asked for further details on the suggestions I wasn't sure about. I would also open a new chat and ask the AI what it thought about the suggestion. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    Behaviors that were tested were adding tasks, removing tasks, adding multiple pets, scheduling with multiple pets, and conflicting tasks.
- Why were these tests important?
    These test are important because they are core mechanics for the scheduler. These are common cases that most users will face and there needs to be a way to handle them appropriately.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    My confidence is about  8/10. I have the basic elements of a scheduler, but I know there are many improvements that need to be made. This scheduler program is great for users who have predictable schedules, but not for users who have different busy blocks on different days.

- What edge cases would you test next if you had more time?
    One edge cases the AI agent pointed out where cross-plan recurring logic. When generating a weekly plan, the recurring tasks are assume to take place everyday at the same times. There is no way to customize this.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    I am satisfied with the amount of work I was able to accomplish. If I were to start a project like this from scratch without assistance, it would take double the time. However, with and AI agent, I am able focus more on what is better for the user and less on what is easier for me to program.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    I would improve the multiple pet aspect of the program. I would like for the schedules of each pet to be displayed together. The current version of the app only gives a conflict warning when the tasks of different pets are at the same time. I would also like to add the ability to have tasks that are done for animals. An example of this is feeding multiple animals at the same time.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    I learned that you can't rely on the AI to do everything correctly. AI assisted me with this project, but there were times where it didn't do exactly what I wanted. An example of this is when I wanted to implement my test_pawpal.py logic into the app.py. I am not very familiar with streamlit, so I used the AI to assist me. The AI didn't include my conflict function in the app.py causing multiple pet conflict warnings to go unnoticed.
