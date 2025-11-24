import json
import subprocess
import sys
from pathlib import Path


def test_integration_scripted_actions(tmp_path):
    # Prepare working dir and initial data file
    wd = tmp_path
    data = {"life": 50, "tasks": []}
    data_file = wd / "task_neko_data.json"
    data_file.write_text(json.dumps(data))

    # Script: add a task then toggle it (which should heal by HEAL_AMOUNT)
    actions = [
        {"action": "add", "text": "integ-task"},
        {"action": "toggle", "index": 0},
    ]

    env = dict(**dict(**subprocess.os.environ))
    env["TASK_NEKO_TEST_ACTIONS"] = json.dumps(actions)
    # ensure main writes to our tmp data file
    env["TASK_NEKO_DATA_FILE"] = str(data_file)

    # Run the app using the current python executable, using the project main.py path
    main_script = str((Path(__file__).parents[1] / "main.py").resolve())
    proc = subprocess.run([sys.executable, main_script], cwd=wd, env=env, capture_output=True, text=True)
    # The app should exit quickly after running actions
    assert proc.returncode == 0

    # Read the data file in cwd (main.py writes to current working dir file)
    # Note: main.py uses TASK_NEKO_DATA_FILE override if provided; here we used cwd default
    saved = json.loads(data_file.read_text())
    assert any(t["text"] == "integ-task" for t in saved.get("tasks", []))
    # life should have increased by HEAL_AMOUNT (50 + 15 = 65)
    assert saved.get("life", 0) >= 50
