"""Tests for tempo detection."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from stemscore.analyzer.tempo import detect_tempo


def test_detect_tempo_uses_librosa(monkeypatch: pytest.MonkeyPatch) -> None:
    audio = np.zeros(22050, dtype=np.float32)
    sr = 22050

    class DummyBeat:
        @staticmethod
        def beat_track(y: np.ndarray, sr: int) -> tuple[float, Any]:
            assert y is audio
            assert sr == 22050
            return 123.4, np.array([0, 1, 2])

    class DummyLibrosa:
        beat = DummyBeat

    monkeypatch.setitem(__import__("sys").modules, "librosa", DummyLibrosa)

    tempo = detect_tempo(audio, sr)
    assert tempo == pytest.approx(123.4)
