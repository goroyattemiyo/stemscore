from __future__ import annotations

import numpy as np
import pytest

from stemscore.analyzer.time_sig import detect_time_signature


def test_detect_time_signature_three(monkeypatch: pytest.MonkeyPatch) -> None:
    audio = np.zeros(22050, dtype=np.float32)
    sr = 22050
    tempo = 120.0

    onset_env = np.zeros(12, dtype=np.float32)
    onset_env[[0, 3, 6, 9]] = 2.0
    onset_env[[0, 4, 8]] = 1.0

    class DummyOnset:
        @staticmethod
        def onset_strength(y: np.ndarray, sr: int) -> np.ndarray:
            return onset_env

    class DummyBeat:
        @staticmethod
        def beat_track(
            y: np.ndarray, sr: int, bpm: float, units: str
        ) -> tuple[float, np.ndarray]:
            return bpm, np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

    class DummyLibrosa:
        onset = DummyOnset
        beat = DummyBeat

    monkeypatch.setitem(__import__("sys").modules, "librosa", DummyLibrosa)

    assert detect_time_signature(audio, sr, tempo) == 3


def test_detect_time_signature_four(monkeypatch: pytest.MonkeyPatch) -> None:
    audio = np.zeros(22050, dtype=np.float32)
    sr = 22050
    tempo = 100.0

    onset_env = np.zeros(12, dtype=np.float32)
    onset_env[[0, 4, 8]] = 2.0
    onset_env[[0, 3, 6, 9]] = 1.0

    class DummyOnset:
        @staticmethod
        def onset_strength(y: np.ndarray, sr: int) -> np.ndarray:
            return onset_env

    class DummyBeat:
        @staticmethod
        def beat_track(
            y: np.ndarray, sr: int, bpm: float, units: str
        ) -> tuple[float, np.ndarray]:
            return bpm, np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

    class DummyLibrosa:
        onset = DummyOnset
        beat = DummyBeat

    monkeypatch.setitem(__import__("sys").modules, "librosa", DummyLibrosa)

    assert detect_time_signature(audio, sr, tempo) == 4
