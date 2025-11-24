"""Lightweight headless 'neko' manager reused from task-neko visuals and logic.
This headless version stores `life` in `data/neko.json` and exposes simple methods
to heal, get mood, and render a text visualization.
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Dict

# Small ASCII cat art and vibes copied/adapted from task-neko
CATS: Dict[str, str] = {
    "THRIVING": "( ^_^ )",
    "HAPPY": "( ^_^ )",
    "IDLE": "( o.o )",
    "SAD": "( ._. )",
    "CRITICAL": "( T_T )",
    "DEAD": "( X_X )",
}

VIBES = {
    "THRIVING": ["I feel INFINITE! ✨", "High energy detected!"],
    "HAPPY": ["Purring... ♫", "Good flow."],
    "IDLE": ["Just vibing.", "Waiting for orders..."],
    "SAD": ["Please don't forget me.", "My hunger is growing..."],
    "CRITICAL": ["Fading away...", "Don't let me become a ghost."],
    "DEAD": ["...", "(Spooky ghost noises)"],
}


class NekoManager:
    def __init__(self, path: str | None = None, default_life: int = 50):
        root = os.getcwd()
        data_dir = os.path.join(root, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.path = path or os.path.join(data_dir, "neko.json")
        self.default_life = default_life
        self.life = self.default_life
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                self.life = int(data.get("life", self.default_life))
            except Exception:
                self.life = self.default_life
        else:
            self.life = self.default_life

    def save(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump({"life": self.life}, fh, indent=2)

    def heal(self, amount: int = 15):
        if self.life <= 0:
            self.life = 20
        else:
            self.life = min(100, self.life + amount)
        self.save()

    def get_mood(self) -> str:
        if self.life <= 0:
            return "DEAD"
        if self.life >= 90:
            return "THRIVING"
        if self.life >= 70:
            return "HAPPY"
        if self.life >= 40:
            return "IDLE"
        if self.life >= 20:
            return "SAD"
        return "CRITICAL"

    def render(self) -> str:
        mood = self.get_mood()
        cat = CATS.get(mood, CATS["IDLE"])
        vibe = random.choice(VIBES.get(mood, ["..."]))
        bar_fill = int(self.life / 5)
        bar = "█" * bar_fill + "░" * (20 - bar_fill)
        return f"{cat} {mood}\n\"{vibe}\"\n[{bar}] {self.life}%"

    def reset(self):
        self.life = self.default_life
        self.save()

    # Hook for TaskManager: called when a task is toggled
    def on_task_toggled(self, task, completed: bool):
        # If task newly completed, heal
        if completed:
            self.heal()
