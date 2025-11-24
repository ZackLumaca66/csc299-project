"""Small Typer-based CLI for tasks4 summarizer."""
from __future__ import annotations
from typing import List, Optional
import typer
from .tasks4 import summarize_paragraphs, SAMPLE_PARAGRAPHS

app = typer.Typer(help="tasks4 summarizer CLI")


@app.command()
def summarize(file: Optional[str] = typer.Option(None, help="Path to a text file with paragraph descriptions, one per line"),
              model: str = typer.Option("chatgpt-5-mini", help="Model name to request")) -> None:
    """Summarize paragraphs from a file or use built-in sample paragraphs."""
    paragraphs: List[str]
    if file:
        with open(file, "r", encoding="utf-8") as fh:
            paragraphs = [line.strip() for line in fh if line.strip()]
    else:
        paragraphs = SAMPLE_PARAGRAPHS

    summaries = summarize_paragraphs(paragraphs, model=model)
    for i, s in enumerate(summaries, start=1):
        typer.echo(f"Paragraph {i} summary: {s}")


def main(argv: Optional[List[str]] = None) -> int:
    """Console entrypoint used by `uv run tasks4` via package main()."""
    # Typer will handle argv when invoked without parameters.
    app()
    return 0
