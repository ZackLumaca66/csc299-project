# tasks1: Simple JSON Task Manager

This is a prototype command-line application (CLI) for managing tasks. It's the first iteration of the `csc299-project`.

All tasks are stored in a JSON file named `tasks.json` in this same directory.

## Features

* **Add:** Add a new task.
* **List:** List all current tasks.
* **Search:** Search for tasks by a keyword.

## How to Run

All commands should be run from your terminal while inside the `tasks1` directory.

### List All Tasks

To see all saved tasks:

```bash
python tasks.py list
```

### Add a New Task

Use the `add` command followed by the task description. Quotes are helpful if you want to include spaces:

```bash
python tasks.py add "Write the README.md file for tasks1"
python tasks.py add "Submit the assignment"
```

### Search for Tasks

Search descriptions (case-insensitive):

```bash
python tasks.py search "README"
```

### Get Help

Show the available commands:

```bash
python tasks.py help
```

---

## Suggested Git Commands

From the root of your repository:

```bash
git add tasks1/
git commit -m "feat: Add tasks1 prototype CLI application"
git push origin main
```

## Example Workflow

```bash
python tasks.py add "Finish project outline"
python tasks.py add "Review JSON handling"
python tasks.py list
python tasks.py search project
```

## Next Ideas (Optional Enhancements)

* Mark tasks as completed
* Delete tasks
* Persist creation timestamps
* Export to CSV
* Add unit tests (pytest)
* Use argparse for richer CLI

Let me know if you’d like help adding any of these.
