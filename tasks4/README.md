# tasks4: Task Description Summarizer (OpenAI Chat Completions API)

Standalone experiment: summarize paragraph-length task descriptions into short phrases using the OpenAI Chat Completions API.

## Structure
```
tasks4/
  README.md
  pyproject.toml
  src/
    __init__.py
    tasks4/
      __init__.py
      tasks4.py
```

## Requirements
- Python >= 3.11
- Dependency: `openai`
- Environment variable: `OPENAI_API_KEY`

## Run (direct)
```bash
export OPENAI_API_KEY="sk-your-real-key"
python tasks4/src/tasks4/tasks4.py
```

## Run (uv) (optional)
```bash
cd tasks4
uv add openai
cd ..
export OPENAI_API_KEY="sk-your-real-key"
uv run tasks4
```

## Model
Default: `chatgpt-5-mini` (change `MODEL_NAME` in `tasks4.py` if necessary).

## Fallback
If key missing or API fails, prints heuristic summary (first ~8 words).

## Sample Output
```
Summarizing task descriptions...

Paragraph 1 summary: Refactor authentication module for scalability
Paragraph 2 summary: Weekly analytics reporting pipeline
```

## Next (Optional)
- Add CLI (Typer) to read paragraphs from a file.
- Add pytest tests with mocked OpenAI.
- Integrate summarizer into Task-Neko later.

## Implementation Notes (2025-11-19)

I added a concrete Chat Completions summarizer implementation and unit tests:

- `tasks4/src/tasks4/tasks4.py` — summarizer implementation. It attempts to use the `openai` Chat Completions API
  (model `chatgpt-5-mini` by default) and falls back to a simple heuristic (first few words) if the library or API
  key is not available or a call fails. The module exposes:
  - `summarize_paragraph(paragraph: str, model: str = "chatgpt-5-mini") -> str`
  - `summarize_paragraphs(paragraphs: List[str], model: str = "chatgpt-5-mini") -> List[str]`
  - `main()` that runs sample paragraphs and prints summaries.

- `tasks4/tests/unit/test_summarizer.py` — unit tests that mock the `openai` module and verify both mocked
  completions responses and the fallback behavior when `openai` is not available.

### How to run the summarizer (local)

On Windows PowerShell (example):

```powershell
# Run the summarizer (uses SAMPLE_PARAGRAPHS embedded in the module)
python tasks4/src/tasks4/tasks4.py

# If you want to use the real OpenAI API set your key first (optional):
$env:OPENAI_API_KEY = "sk-your-real-key"
python tasks4/src/tasks4/tasks4.py
```

The code gracefully falls back to a heuristic summary if `OPENAI_API_KEY` is not set or the `openai` client
is not installed.

### Running tests (recommended)

Install `pytest` in your environment (or use the repository `.venv`):

```powershell
# from repo root (example using the workspace venv python)
C:/Users/<you>/.../.venv/Scripts/python.exe -m pip install -U pytest

# Run the tasks4 tests (set PYTHONPATH so tests import the local package)
$env:PYTHONPATH = 'c:\Users\zackm\Documents\dev\csc299-project\tasks4\src'
C:/Users/<you>/.../.venv/Scripts/python.exe -m pytest tasks4/tests -q
```

The tests mock `openai` and will pass even without a network call or API key.

### Next suggestions

- Add a small CLI wrapper (Typer) to accept input files or stdin for batched summarization.
- Add a mocked integration test for the `main()` entrypoint.
- Optionally wire a small Cache to avoid re-summarizing identical paragraphs.