# Task-Neko
A terminal pet productivity companion built with [Textual]. Complete tasks to keep your cyber cat thriving. Neglect it and it fades into a ghost.

[![Task-Neko tests](https://github.com/ZackLumaca66/csc299-project/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ZackLumaca66/csc299-project/actions/workflows/python-tests.yml)

## Features
- Mood-based ASCII cat with dynamic health bar
- Hourly decay (configurable) + healing on task completion
- Phoenix revive: completing a task at 0% revives to 20%
- Random vibe messages per mood tier
- Persistent JSON storage (`task_neko_data.json`)
- Fast task interactions: Enter to add, Click to toggle, Del to delete

## Quick Start (Windows Git Bash)
```bash
# Inside the project virtual environment or system Python
pip install textual
winpty python task-neko/main.py
```
If using the workspace venv: replace `python` with the full path shown when the environment was configured.

## Configuration
Edit constants at top of `main.py`:
- `DATA_FILE` (default: task_neko_data.json)
- `DECAY_RATE` seconds per health point loss (3600 prod, try 5 for quick testing)
- `HEAL_AMOUNT` percent restored per completed task

## Usage
1. Launch app.
2. Type a task and press Enter.
3. Click a task to toggle done/undone. Completing (marking done) heals the cat.
4. Press `Del` key while a task is highlighted to remove it.
5. Health auto-saves along with all task states.

## Moods
| Life %        | Mood       |
|---------------|------------|
| 90-100        | THRIVING   |
| 70-89         | HAPPY      |
| 40-69         | IDLE       |
| 20-39         | SAD        |
| 1-19          | CRITICAL   |
| 0             | DEAD (revivable) |

## Data File Structure
```json
{
  "life": 100,
  "tasks": [
    {"text": "Write project proposal", "done": false},
    {"text": "Refactor search module", "done": true},
    {"text": "Drink water", "done": false}
  ]
}
```
Delete or modify `task_neko_data.json` anytime; the app recreates it if missing.

## Customization Ideas
- Change ASCII art or add color gradients
- Add a streak counter
- Integrate with external task sources
- Add sounds (Textual + external libs)

## License / Attribution
Include this component in your personal productivity toolkit. ASCII art intentionally simple for easy modification.

Enjoy keeping Task-Neko happy 🐾

## Test Mode

Task-Neko supports a scripted test mode to enable deterministic integration testing without driving the interactive TUI. Use the following environment variables when running `main.py`:

- `TASK_NEKO_TEST_ACTIONS`: JSON array of actions the app will perform on startup. Supported actions:
  - `{ "action": "add", "text": "..." }` — add a new task
  - `{ "action": "toggle", "index": N }` — toggle task at index N (0-based)
  - `{ "action": "delete", "index": N }` — delete task at index N

- `TASK_NEKO_DATA_FILE`: Path to the JSON data file to read/write (defaults to `task_neko_data.json`).

Example (Bash):

```bash
export TASK_NEKO_DATA_FILE="/tmp/task_neko_data.json"
export TASK_NEKO_TEST_ACTIONS='[{"action":"add","text":"ci-task"},{"action":"toggle","index":0}]'
python main.py
```

When `TASK_NEKO_TEST_ACTIONS` is present the app will apply the actions, save state, and exit immediately — perfect for CI integration tests.
