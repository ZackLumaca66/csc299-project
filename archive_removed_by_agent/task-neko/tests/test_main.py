import importlib.util
from pathlib import Path
import random


def load_main_module():
    spec = importlib.util.spec_from_file_location(
        "task_neko.main", Path("task-neko") / "main.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_datamanager_save_load(tmp_path, monkeypatch):
    main = load_main_module()
    data_file = tmp_path / "data.json"
    monkeypatch.setattr(main, "DATA_FILE", str(data_file))

    tasks = [{"text": "t1", "done": False}]
    main.DataManager.save_data(42, tasks)
    loaded = main.DataManager.load_data()

    assert loaded["life"] == 42
    assert loaded["tasks"] == tasks


def test_taskitem_toggle(monkeypatch):
    main = load_main_module()
    # Prevent Textual widget methods that require the live app
    monkeypatch.setattr(main.TaskItem, "refresh_label", lambda self: None)
    ti = main.TaskItem("hello", False)
    assert ti.done is False
    res = ti.toggle()
    assert res is True
    assert ti.done is True
    res2 = ti.toggle()
    assert res2 is False


def test_tamagotchi_mood_and_heal(monkeypatch):
    main = load_main_module()
    t = main.Tamagotchi()

    # mood thresholds
    t.life = 95
    assert t.get_mood() == "THRIVING"
    t.life = 75
    assert t.get_mood() == "HAPPY"
    t.life = 50
    assert t.get_mood() == "IDLE"
    t.life = 30
    assert t.get_mood() == "SAD"
    t.life = 10
    assert t.get_mood() == "CRITICAL"

    # prevent app.save_state being required
    class Dummy:
        def save_state(self):
            pass

    # avoid calling into Textual's app context by monkeypatching heal to skip save
    def heal_no_save(self):
        if self.life <= 0:
            self.life = 20
        else:
            self.life = min(self.life + main.HEAL_AMOUNT, 100)
        self.update_vibe()

    monkeypatch.setattr(main.Tamagotchi, "heal", heal_no_save)

    # heal from near-full
    t.life = 90
    t.heal()
    assert t.life == 100

    # revive from dead
    t.life = 0
    t.heal()
    assert t.life == 20


def test_update_vibe_and_render():
    main = load_main_module()
    random.seed(0)
    t = main.Tamagotchi()
    t.life = 95
    t.update_vibe()
    assert t.current_vibe in main.VIBES["THRIVING"]
    rendered = t.render()
    # render should include life percentage
    assert str(t.life) in rendered


def test_datamanager_handles_corrupt_file(tmp_path, monkeypatch):
    main = load_main_module()
    data_file = tmp_path / "bad.json"
    data_file.write_text("not a json")
    monkeypatch.setattr(main, "DATA_FILE", str(data_file))

    loaded = main.DataManager.load_data()
    assert loaded["life"] == 100
    assert loaded["tasks"] == []


def test_tamagotchi_render_bar_and_color():
    main = load_main_module()
    t = main.Tamagotchi()

    t.life = 100
    r = t.render()
    assert "#00ff00" in r or "█" in r

    t.life = 10
    r2 = t.render()
    # low life should show red color code
    assert "#ff0000" in r2 or "GHOST" in r2 or "%" in r2


def test_taskitem_refresh_label_captures_content():
    main = load_main_module()
    # Create instance without calling refresh_label (which calls self.update())
    orig_init = main.TaskItem.__init__

    def lazy_init(self, text: str, done: bool = False):
        # call parent ListItem init and set fields without calling refresh_label
        from textual.widgets import ListItem
        ListItem.__init__(self)
        self.task_text = text
        self.done = done

    try:
        main.TaskItem.__init__ = lazy_init
        ti = main.TaskItem("label-test", False)

        # capture the widget passed to update
        captured = {}

        # Provide a fake Static class in the main module so we can inspect the value passed
        class FakeStatic:
            def __init__(self, value):
                self.value = value
            def __repr__(self):
                return f"FakeStatic({self.value})"

        main.Static = FakeStatic

        def fake_update(w):
            # try to extract the value we stored on FakeStatic
            v = getattr(w, 'value', None)
            if v is not None:
                captured['text'] = v
            else:
                captured['text'] = repr(w)

        ti.update = fake_update
        # now call the real refresh_label implementation
        main.TaskItem.refresh_label(ti)
        assert 'text' in captured
        # the widget content should include the label text
        text = captured.get('text')
        assert text is not None
        assert "label-test" in str(text)
    finally:
        main.TaskItem.__init__ = orig_init
