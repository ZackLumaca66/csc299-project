Here is the development summary rewritten to be informal, personal, and plain-spoken, without using slang.

Development Summary: How I Built This
This is a look at how I developed the software, the tools I used to get there, the mistakes I made along the way, and the practical steps I took to get the final version onto the main branch.

What I actually worked on (Scope)
My main focus was giving proper input and commands to the VScode gpt5 ai helper to make sure that it understood my vision for a software that would include personal knowledge management, system (PKMS), apersonal task management system, a terminal-based chat interface to interact with your stored knowledge and tasks, and AI agents that interact with the stored knowledge. I had to make sure that the work it was doing and the features it would implement would match the course requirements and my own ideas and requirements for the software I wanted to build. I also had it improve the experience in the terminal—specifically, I made sure notes are properly linked to tasks and that the "reset" command doesn't crash the automated testing system by waiting for a human to press a key. I also refined the "agent" so it can read notes and figure out priorities without getting confused. I also did hours of my own testing using the software as I didn't fully trust the ai helpers testing, and it didn't always understand my full vision. 

How I used AI Assistance
Chatting through the design: I used a chat-based assistant heavily for the big-picture thinking. When I needed to figure out the logic behind a feature or decide how to structure the code, I talked it through in the chat first. It was my primary place for experimenting with ideas before committing to them. I used Google Gemini for this as it was able to turn my ideas into a clear plan for making that software.

Inline coding help: Inside my code editor (VS Code), I used the inline suggestions to handle the repetitive typing. It was great for setting up data structures or writing standard functions. I treated these suggestions like rough drafts—I accepted them and then made sure they were working fine

Big refactors: When I needed to change how the storage worked across multiple files, I used larger prompts to generate the initial code, which I then double-checked with my tests.

Local testing: I used a "mock" (simulated) AI tool locally. This let me test the agent's advice features without needing an internet connection or worrying about random results from a real API.

I also used Gemini to just brainstorm features and get advice on how to handle git workflows. This helped me prioritize what to build first.

How I planned the work
Initially I used google gemini to create the initial plan for the software I wanted to make, but over time I used co pilot's helper to better refine and improve it, and then I coontinuosly used VScodes's helper to help me build the rest of it and run tests and make sure the software was functioning as I wanted it to. 

Testing and Validating
The testing routine: I used VsCodes helper to run 1000s of tests over this process. I made sure the helper would create all the tests needed to ensure this software would work well. Any change to the software was immediately followed by a full test and then multiple tests to that new change.

Using Mocks: The local simulator allowed me to check if the agent was behaving correctly without spending money on API credits.

The feedback loop: My cycle was simple: Edit the code -> Run the test -> Fix the bug -> Run all tests -> Commit the changes. This saved me a lot of headaches.

What worked well
The tests saved me: The automated tests caught several issues I would have missed, especially regarding how the commands interact with the user.

Hybrid AI workflow: Alternating between chatting for high-level ideas with Copilot and Gemini and using VsCodes ai helper for implementing them fast and efficent was very helpful and it was a good balance. 
Local simulation: Being able to test the agent features offline was a huge win.

Incremental updates: Writing a small script to handle database updates was much safer than trying to manually edit the database files.

What didn't work (The bumps in the road)
Breaking the database: At one point, I accidentally removed the support for task_id in notes. This broke the tests immediately. It was a good reminder of why tests are important when changing how data is saved.

Freezing the automation: I made a change where the reset command always asked for confirmation. This caused the automated tests to freeze because there was no human to type "yes." I fixed this by making the command auto-confirm when it detects it's running in a script.

Git stash issues: I tried to switch branches while I had uncommitted changes in my local data folder, and it caused conflicts. I learned I need to be more careful about managing local files before switching tasks.

Ai Features: I implemented all the proper ai features for this software and the requirements but I did not buy an OpenAi Api key.

Practical steps I took (The Rundown)
I put the task_id field back into the Note model.

I updated the storage systems (JSON and SQLite) to correctly save that ID.

I fixed the function signatures so the code stopped complaining about missing arguments.

I updated the command-line interface to be smarter about when to ask for user confirmation.

I added a Python script to handle text replacement properly across different operating systems.

I ran all the tests until they passed, committed the work, and pushed it to the main repository.

Addendum: Putting it all together
For the final integration, I consolidated the code into a single core folder (pkms_core). This solved a lot of messy import issues and made the project much cleaner.

The Design Philosophy:

Keep the core stable: I made sure the basic models and storage didn't change just because I added new chat features.

Make it replaceable: The "intelligence" layer starts simple (just summaries), but can be upgraded to a real AI later without breaking the rest of the app.

Keep it portable: Everything runs locally on your machine.

Don't overwhelm the user: The new chat commands are there if you want them, but they don't get in the way of the standard tasks.

Basically, the architecture is now set up for any user to implement their own Api Key to use the Open AI agents and the features that come with it, but right now, it's a solid quality working tool with all the required features and overall is a really good Productivity Task Management Terminal  Software that has features of 
-personal knowledge management system (PKMS)
-personal task management system
-a terminal-based chat interface to interact with your stored knowledge and tasks
-AI agents that interact with the stored knowledge or tasks
