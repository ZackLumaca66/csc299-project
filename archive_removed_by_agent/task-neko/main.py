import json
import os
import random
import logging
from pathlib import Path
from rich.align import Align
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Input, ListView, ListItem
from textual.reactive import reactive

# --- CONFIGURATION ---
DATA_FILE = "task_neko_data.json"
# Default starting life when no data file exists (overridable via env TASK_NEKO_DEFAULT_LIFE)
DEFAULT_LIFE = int(os.environ.get("TASK_NEKO_DEFAULT_LIFE", "50"))
DECAY_RATE = 3600.0  # Seconds (Set to 3600 for 1 hour. Set to 5.0 to test death quickly)
HEAL_AMOUNT = 15

# Setup simple file logger for diagnostics
try:
    _log_dir = Path(__file__).parent
    _log_dir.mkdir(parents=True, exist_ok=True)
    LOG_FILE = _log_dir / "debug.log"
    logger = logging.getLogger("task_neko")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(fh)
except Exception:
    # If logging setup fails, fall back to a no-op logger
    logger = logging.getLogger("task_neko")

# --- ASSETS: VISUALS ---
CATS = {
    "THRIVING": r"""
      ★   /\_/\   ★
         ( ≧ω≦ )
          > ^ <
    """,
    "HAPPY": r"""
          /\_/\
         ( ^_^ )
          > ^ <
    """,
    "IDLE": r"""
          /\_/\
         ( o.o )
          > ^ <
    """,
    "SAD": r"""
          /\_/\
         ( ._.)
          > ^ <
    """,
    "CRITICAL": r"""
          /\_/\
         ( T_T )
          > ^ <
    """,
    "DEAD": r"""
           .  .
          ( X_X )
      ~  (  RIP  ) ~
         /      \
    """
}

# --- ASSETS: DIALOGUE ---
VIBES = {
    "THRIVING": [
        "I feel INFINITE! ✨",
        "We are actually unstoppable.",
        "High energy detected! Zoomies time!",
        "You are my favorite human.",
    ],
    "HAPPY": [
        "Purring... ♫",
        "Good flow. Let's keep this up.",
        "I saved a spot in the sun for you.",
        "This looks like a good day.",
    ],
    "IDLE": [
        "Waiting for orders...",
        "Nap time? Or work time?",
        "Just vibing.",
        "Did you drink water today?",
    ],
    "SAD": [
        "It's getting dark in here...",
        "I miss the way we used to work.",
        "My hunger is growing...",
        "Please don't forget me.",
    ],
    "CRITICAL": [
        "I don't feel so good...",
        "Please... one task...",
        "Fading away...",
        "Don't let me become a ghost.",
    ],
    "DEAD": [
        "...",
        "(Spooky ghost noises)",
        "I see the light...",
        "Press F to pay respects.",
    ]
}

# --- LOGIC: DATA PERSISTENCE ---
class DataManager:
    """Handles saving and loading data to a JSON file."""
    @staticmethod
    def load_data():
        # Prefer an env override. Otherwise prefer a data file next to this module
        env_file = os.environ.get("TASK_NEKO_DATA_FILE")
        if env_file:
            data_path = Path(env_file)
        else:
            # First choice: data file in the same directory as this module
            module_dir = Path(__file__).parent
            candidate = module_dir / DATA_FILE
            if candidate.exists():
                data_path = candidate
            else:
                # Fallback: data file in current working directory
                data_path = Path(DATA_FILE)

        if not data_path.exists():
            return {"life": DEFAULT_LIFE, "tasks": []}
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"life": DEFAULT_LIFE, "tasks": []}

    @staticmethod
    def save_data(life, tasks):
        env_file = os.environ.get("TASK_NEKO_DATA_FILE")
        if env_file:
            data_path = Path(env_file)
        else:
            module_dir = Path(__file__).parent
            candidate = module_dir / DATA_FILE
            # Prefer writing next to the module (task-neko folder)
            data_path = candidate

        data = {"life": life, "tasks": tasks}
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        try:
            logger.info(f"Saved data to {data_path}: life={life}, tasks={len(tasks)}")
        except Exception:
            pass

# --- WIDGET: THE PET ---
class Tamagotchi(Static):
    """The Pet Widget that handles health and mood."""
    life = reactive(100) 
    current_vibe = reactive("Ready to work!")
    
    def on_mount(self) -> None:
        """Start the decay timer when app starts."""
        self.set_interval(DECAY_RATE, self.decay)
        self.update_vibe()

    def decay(self) -> None:
        """Time makes the cat sadder."""
        if self.life > 0:
            self.life -= 1
            self.update_vibe()
            self.app.save_state()

    def heal(self) -> None:
        """Called when a task is completed."""
        if self.life <= 0:
            self.life = 20  # Phoenix Protocol: Revive if dead
        else:
            self.life = min(self.life + HEAL_AMOUNT, 100)
        self.update_vibe()
        try:
            logger.info(f"Tamagotchi.heal: new life={self.life}")
        except Exception:
            pass
        self.app.save_state()

    def get_mood(self) -> str:
        """Calculates mood based on Life %."""
        if self.life <= 0: return "DEAD"
        if self.life >= 90: return "THRIVING"
        if self.life >= 70: return "HAPPY"
        if self.life >= 40: return "IDLE"
        if self.life >= 20: return "SAD"
        return "CRITICAL"

    def update_vibe(self):
        """Picks a random quote based on current mood."""
        mood = self.get_mood()
        if mood in VIBES:
            self.current_vibe = random.choice(VIBES[mood])

    def render(self) -> str:
        mood = self.get_mood()
        
        # Color logic for the bar
        color = "#00ff00" # Green
        if self.life < 50: color = "#ffff00" # Yellow
        if self.life < 20: color = "#ff0000" # Red
        
        # Draw the health bar
        bar_fill = int(self.life / 5) # 20 blocks total
        bar = "█" * bar_fill + "░" * (20 - bar_fill)
        
        status_text = f"[{color}]{bar}[/] {self.life}%"
        if self.life <= 0: status_text = "[#ff0000]GHOST (Complete task to revive)[/]"

        # Renders: CAT + QUOTE + BAR — center align the whole block
        content = f"{CATS[mood]}\n\n[i]\"{self.current_vibe}\"[/]\n\n{status_text}"
        try:
            return Align(content, "center")
        except Exception:
            return content

# --- WIDGET: A SINGLE TASK ---
class TaskItem(ListItem):
    """A custom widget for a single task item. Simpler: render() returns the label."""
    def __init__(self, text: str, done: bool = False) -> None:
        super().__init__()
        self.task_text = text
        self.done = done

    def render(self) -> str:
        if self.done:
            icon = "[#00ff00]✔[/]"
            style = "[dim strike]"
        else:
            icon = "[ ]"
            style = ""
        if style:
            return f"{icon} {style}{self.task_text}[/]"
        else:
            return f"{icon} {self.task_text}"

    def toggle(self):
        """Switches state and returns the new state."""
        self.done = not self.done
        try:
            # ask the widget to refresh its rendered output
            self.refresh()
        except Exception:
            pass
        return self.done

# --- MAIN APP ---
class TaskNekoApp(App):
    CSS_PATH = "styles.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._editing_item = None

    def compose(self) -> ComposeResult:
        yield Container(
            Tamagotchi(id="pet-display"),
            Vertical(
                Input(placeholder="Add a new task...", id="task-input"),
                ListView(id="task-list"),
                Static("[dim]Click to toggle status • 'Del' to remove[/]", id="help-text"),
                id="bottom-container"
            ),
            id="main-layout"
        )

    def on_mount(self) -> None:
        """Load data when app starts."""
        data = DataManager.load_data()
        self.query_one(Tamagotchi).life = data.get("life", 100)
        self.query_one(Tamagotchi).update_vibe()
        
        task_list = self.query_one("#task-list")
        for t in data.get("tasks", []):
            new_item = TaskItem(t["text"], t["done"])
            try:
                task_list.append(new_item)
            except Exception:
                # fallback to mount if append isn't available on this Textual version
                task_list.mount(new_item)

        # Test-mode: allow scripted actions via env var TASK_NEKO_TEST_ACTIONS (JSON array)
        # Example: [{"action":"add","text":"hi"},{"action":"toggle","index":0}]
        test_actions = os.environ.get("TASK_NEKO_TEST_ACTIONS")
        if test_actions:
            try:
                actions = json.loads(test_actions)
            except Exception:
                actions = []

            for a in actions:
                act = a.get("action")
                if act == "add":
                    txt = a.get("text", "")
                    item = TaskItem(txt, False)
                    try:
                        task_list.append(item)
                    except Exception:
                        task_list.mount(item)
                elif act == "toggle":
                    idx = int(a.get("index", 0))
                    # ensure index exists
                    children = [c for c in task_list.children if isinstance(c, TaskItem)]
                    if 0 <= idx < len(children):
                        was_done = children[idx].toggle()
                        if was_done:
                            self.query_one(Tamagotchi).heal()
                elif act == "delete":
                    idx = int(a.get("index", 0))
                    children = [c for c in task_list.children if isinstance(c, TaskItem)]
                    if 0 <= idx < len(children):
                        children[idx].remove()
                elif act == "edit":
                    idx = int(a.get("index", 0))
                    new_text = a.get("text", "")
                    children = [c for c in task_list.children if isinstance(c, TaskItem)]
                    if 0 <= idx < len(children):
                        children[idx].task_text = new_text
                        try:
                            children[idx].refresh()
                        except Exception:
                            pass

            # save and exit immediately when in test mode
            self.save_state()
            self.exit()

    def save_state(self):
        """Gather all data and write to disk."""
        pet = self.query_one(Tamagotchi)
        task_list = self.query_one("#task-list")
        
        tasks_data = []
        for item in task_list.children:
            if isinstance(item, TaskItem):
                tasks_data.append({"text": item.task_text, "done": item.done})
        
        DataManager.save_data(pet.life, tasks_data)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Add a new task."""
        text = event.value.strip()
        if text:
            # If currently editing, update that item instead of adding
            if getattr(self, "_editing_item", None) is not None:
                item = self._editing_item
                item.task_text = text
                try:
                    item.refresh()
                except Exception:
                    pass
                try:
                    logger.info(f"Edit task: {text}")
                except Exception:
                    pass
                self._editing_item = None
            else:
                item = TaskItem(text, False)
                try:
                    self.query_one("#task-list").append(item)
                except Exception:
                    self.query_one("#task-list").mount(item)
                try:
                    logger.info(f"Add task: {text}")
                except Exception:
                    pass

            self.query_one("#task-input").value = ""
            self.save_state()

    def key_e(self) -> None:
        """Begin editing the currently highlighted task (prefill input)."""
        list_view = self.query_one("#task-list")
        if list_view.highlighted_child and isinstance(list_view.highlighted_child, TaskItem):
            item = list_view.highlighted_child
            self._editing_item = item
            try:
                inp = self.query_one("#task-input")
                inp.value = item.task_text
                inp.focus()
            except Exception:
                pass

    def key_enter(self) -> None:
        """When Enter is pressed, if a list item is highlighted toggle it; otherwise handled by Input.Submitted."""
        list_view = self.query_one("#task-list")
        if list_view.highlighted_child and isinstance(list_view.highlighted_child, TaskItem):
            item = list_view.highlighted_child
            is_now_done = item.toggle()
            if is_now_done:
                try:
                    logger.info(f"Task toggled done: {getattr(item, 'task_text', '<unknown>')} -> {item.done}")
                except Exception:
                    pass
                self.query_one(Tamagotchi).heal()
            self.save_state()
            return

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle clicking a task."""
        item = event.item
        if isinstance(item, TaskItem):
            is_now_done = item.toggle()
            # Only heal the cat if we just marked it DONE (not unchecking)
            if is_now_done:
                try:
                    logger.info(f"Task toggled done: {getattr(item, 'task_text', '<unknown>')} -> {item.done}")
                except Exception:
                    pass
                self.query_one(Tamagotchi).heal()
            self.save_state()

    def key_delete(self) -> None:
        """Press 'Del' key to remove selected task."""
        list_view = self.query_one("#task-list")
        if list_view.highlighted_child:
            try:
                removed = list_view.highlighted_child
                txt = getattr(removed, 'task_text', None)
                logger.info(f"Delete task: {txt}")
            except Exception:
                pass
            list_view.highlighted_child.remove()
            self.save_state()

if __name__ == "__main__":
    app = TaskNekoApp()
    app.run()
