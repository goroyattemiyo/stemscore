# CLAUDE.md – StemScore

## What
StemScore: MP3→6-part MIDI/score (lead vocal, backing vocal, bass, drums, backing harmony, chords).

## Layout
- `src/stemscore/` — source code (4-phase pipeline + suno/)
- `docs/design/` — 8-chapter design spec (READ before coding)
- `tests/` — pytest suite

## Commands
- `pip install -e ".[dev]"` — install
- `pytest tests/ -v` — test
- `ruff check src/ tests/` — lint
- `ruff format src/ tests/` — format
- `mypy src/stemscore/` — type check

## Conventions
- Python 3.10+, type hints, Google docstrings
- pathlib.Path, logging (no print), 99 char lines
- Adapter pattern for ML models
- Lazy import torch/tensorflow
- Audio: 22050 Hz mono | MIDI: Type 1, GM, drums ch10

## Do NOT
- Commit model weights or large audio files
- Use global state/singletons
- Import torch/tensorflow at module level
- Skip error handling on file I/O
