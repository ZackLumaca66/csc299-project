from __future__ import annotations

try:
    from textual.app import App
    from textual.widgets import Header, Footer, Static
    from textual.containers import Vertical
except Exception:  # textual not installed
    App = None


class DashboardApp:
    """Minimal Textual scaffold. If `textual` isn't installed this is a harmless stub."""
    def __init__(self, tm=None, dm=None, agent=None):
        self.tm = tm
        self.dm = dm
        self.agent = agent

    def run(self):
        if App is None:
            print("Textual not installed — install 'textual' to enable the TUI scaffold.")
            return

        class _App(App):
            CSS = """
            Screen {
                align: center middle;
            }
            """

            def compose(self):
                yield Header()
                yield Vertical(Static("Tasks panel - placeholder"), Static("Docs panel - placeholder"))
                yield Footer()

        _App().run()


__all__ = ["DashboardApp"]
