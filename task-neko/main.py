import json
import os
import random
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Input, ListView, ListItem
from textual.reactive import reactive

# --- CONFIGURATION ---
DATA_FILE = "task_neko_data.json"
DECAY_RATE = 3600.0  # Seconds (Set to 3600 for 1 hour. Set to 5.0 to test death quickly)
HEAL_AMOUNT = 15

# --- ASSETS: VISUALS ---
CATS = {
    "THRIVING": """
      ★   /\_/\   ★
         ( ≧ω≦ )
          > ^ <
    """,
    "HAPPY": """
          /\_/\
         ( ^_^ )
          > ^ <
    """,
    "IDLE": """
          /\_/\
         ( o.o )
          > ^ <
    """,
    "SAD": """
          /\_/\
         ( ._.)
          > ^ <
    """,
    "CRITICAL": """
          /\_/\
         ( T_T )
          > ^ <
    """,
    "DEAD": """
           .  .
          ( X_X )
      ~  (  RIP  ) ~
         /      \\
    """,
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
    ],
}

# --- LOGIC: DATA PERSISTENCE ---
class DataManager:
    """Handles saving and loading data to a JSON file."""
    @staticmethod
    def load_data():
        if not os.path.exists(DATA_FILE):
            return {"life": 100, "tasks": []}
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {"life": 100, "tasks": []}

    @staticmethod
    def save_data(life, tasks):
        data = {"life": life, "tasks": tasks}
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

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

        # Renders: CAT + QUOTE + BAR
        return f"{CATS[mood]}\n\n[i]\"{self.current_vibe}\"[/]\n\n{status_text}"

# --- WIDGET: A SINGLE TASK ---
class TaskItem(ListItem):
    """A custom widget for a single task item."""
    def __init__(self, text: str, done: bool = False) -> None:
        super().__init__()
        self.task_text = text
        self.done = done
        self.refresh_label()

    def refresh_label(self):
        """Updates visual style based on done state."""
        if self.done:
            icon = "[#00ff00][x][/]'" 
            style = "[dim strike]"
        else:
            icon = "[#ff00ff][ ][/]" 
            style = "[#ffffff]"
            
        self.update(Static(f"{icon} {style}{self.task_text}[/]"))

    def toggle(self):
        """Switches state and returns the new state."""
        self.done = not self.done
        self.refresh_label()
        return self.done

# --- MAIN APP ---
class TaskNekoApp(App):
    CSS_PATH = "styles.tcss"

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
            task_list.mount(new_item)

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
            self.query_one("#task-list").mount(TaskItem(text, False))
            self.query_one("#task-input").value = ""
            self.save_state()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle clicking a task."""
        item = event.item
        if isinstance(item, TaskItem):
            is_now_done = item.toggle()
            # Only heal the cat if we just marked it DONE (not unchecking)
            if is_now_done:
                self.query_one(Tamagotchi).heal()
            self.save_state()

    def key_delete(self) -> None:
        """Press 'Del' key to remove selected task."""
        list_view = self.query_one("#task-list")
        if list_view.highlighted_child:
            list_view.highlighted_child.remove()
            self.save_state()

if __name__ == "__main__":
    app = TaskNekoApp()
    app.run()
