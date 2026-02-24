# StemScore Project Overview

## What This Project Does
StemScore converts MP3/WAV audio files into 6-part musical scores (MIDI + MusicXML + PDF).
The 6 parts are: lead vocal, backing vocal, bass, drums, backing harmony, chords.

## Tech Stack
- Python 3.11, pip, editable install (`pip install -e ".[dev]"`)
- Key libraries: typer, rich, pydantic, numpy, librosa, soundfile, midiutil, music21
- ML libraries (optional install): basic-pitch, demucs, torch, madmom
- Testing: pytest, ruff (linter), mypy (type checker)

## Repository Structure
src/stemscore/ ├── init.py ├── cli.py # Typer CLI (entry point) ├── config.py # Pydantic genre presets ├── router.py # Route A (Suno stems) vs Route B (full mix) ├── analyzer/ # Phase 1: tempo, key, time-sig detection ├── separator/ # Phase 2: stem separation (Demucs wrapper) ├── transcriber/ # Phase 3: audio→MIDI (Basic Pitch, Omnizart, chord models) ├── assembler/ # Phase 4: MIDI merge, quantize, MusicXML export ├── suno/ # Suno import adapter └── utils/ # Audio I/O, logging, helpers tests/ docs/design/