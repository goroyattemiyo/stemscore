# AGENTS.md – StemScore

## Project
StemScore: open-source Python CLI. MP3→6-part MIDI score.
Pipeline: Analyzer→Separator→Transcriber→Assembler + Suno integration.

## Build & Test
- Install: `pip install -e ".[dev]"`
- Test: `pytest tests/ -v --cov=stemscore`
- Lint: `ruff check src/ tests/`
- Format: `ruff format src/ tests/`
- Type check: `mypy src/stemscore/`

## Code Style
- Python 3.10+, type hints on all public functions
- Google-style docstrings, 99 char line limit
- pathlib.Path (no os.path), logging (no print)
- Adapter pattern for all ML model wrappers
- Lazy imports for heavy deps (torch, tensorflow)

## Architecture
- Source: `src/stemscore/`, Tests: `tests/`
- Design docs: `docs/design/` — ALWAYS read before implementing
- Audio: internal 22050 Hz mono
- MIDI: Type 1, GM, drums ch10
- Genre presets: `src/stemscore/config.py`

## Rules
- One feature per PR, all tests must pass
- Never commit model weights or audio >1MB
- ≥85% code coverage target
