# Prototype overview

This document gives a short tour of the prototype and where to find the most important components.

Structure
- `pkms_core/` — core package implementing TaskManager, DocumentManager, ChatEngine, Agent heuristics, CLI and small LLM adapter.
- `scripts/demo_pkms_chat.py` — simple demo that runs a conversation using the MockLLM when no API key is present.
- `tests/` and `tasks3/tests/` — focused unit tests used in CI.

Entry points
- CLI: `python -m pkms_core.cli` or `python pkms_core/cli.py` (depending on execution environment).

Data
- Runtime example data can be found in `data/` and `data_pkms/` — these are small examples used for demos and tests.
