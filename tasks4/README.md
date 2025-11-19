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