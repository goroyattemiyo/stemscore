from __future__ import annotations

from pathlib import Path
import sys
from types import ModuleType

import numpy as np
import pytest

from stemscore.transcriber.chord_recognizer import recognize_chords


def _install_fake_librosa(monkeypatch: pytest.MonkeyPatch, chroma: np.ndarray) -> None:
    librosa = ModuleType("librosa")
    feature = ModuleType("librosa.feature")

    def chroma_cqt(y: np.ndarray, sr: int) -> np.ndarray:
        return chroma

    def frames_to_time(frames: np.ndarray, sr: int, hop_length: int = 512) -> np.ndarray:
        return np.array([0.0, 1.0, 2.0, 3.0])

    feature.chroma_cqt = chroma_cqt
    librosa.feature = feature
    librosa.frames_to_time = frames_to_time

    monkeypatch.setitem(sys.modules, "librosa", librosa)
    monkeypatch.setitem(sys.modules, "librosa.feature", feature)


def test_recognize_chords_outputs_segments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    audio_path = tmp_path / "harmony.wav"
    audio_path.write_bytes(b"fake")

    chroma = np.zeros((12, 3))
    chroma[[0, 4, 7], 0] = 1.0
    chroma[[0, 4, 7], 1] = 1.0
    chroma[[9, 0, 4], 2] = 1.0

    _install_fake_librosa(monkeypatch, chroma)
    monkeypatch.setattr(
        "stemscore.transcriber.chord_recognizer.load_audio",
        lambda path: (np.zeros(10), 22050),
    )

    events = recognize_chords(audio_path)

    assert len(events) == 2
    assert events[0]["chord"] == "Cmaj"
    assert events[1]["chord"] == "Amin"
