from __future__ import annotations

from pathlib import Path
import sys
from types import ModuleType

import pytest

from stemscore.transcriber.pitch_transcriber import transcribe_pitch


def _install_fake_basic_pitch(monkeypatch: pytest.MonkeyPatch, result: object) -> None:
    inference = ModuleType("basic_pitch.inference")

    def predict(path: str) -> object:
        return result

    inference.predict = predict
    basic_pitch = ModuleType("basic_pitch")
    basic_pitch.inference = inference

    monkeypatch.setitem(sys.modules, "basic_pitch", basic_pitch)
    monkeypatch.setitem(sys.modules, "basic_pitch.inference", inference)


def test_transcribe_pitch_note_event_structure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    audio_path = tmp_path / "melody.wav"
    audio_path.write_bytes(b"fake")

    note_events = [
        {"start": 0.0, "end": 0.5, "pitch": 60, "velocity": 90, "confidence": 0.8},
        {"start": 0.6, "end": 1.0, "pitch": 62, "velocity": 100, "confidence": 0.9},
    ]
    _install_fake_basic_pitch(monkeypatch, {"note_events": note_events})

    result = transcribe_pitch(audio_path)

    assert len(result) == 2
    for event in result:
        assert set(event.keys()) == {"start", "end", "pitch", "velocity", "confidence"}
