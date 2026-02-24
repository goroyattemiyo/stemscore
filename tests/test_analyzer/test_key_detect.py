from __future__ import annotations

import numpy as np
import pytest

from stemscore.analyzer.key_detect import detect_key


def test_detect_key_major(monkeypatch: pytest.MonkeyPatch) -> None:
    chroma = np.zeros((12, 10), dtype=np.float32)
    chroma[0, :] = 1.0

    class DummyFeature:
        @staticmethod
        def chroma_stft(y: np.ndarray, sr: int) -> np.ndarray:
            return chroma

    class DummyLibrosa:
        feature = DummyFeature

    monkeypatch.setitem(__import__("sys").modules, "librosa", DummyLibrosa)

    audio = np.zeros(22050, dtype=np.float32)
    key = detect_key(audio, 22050)
    assert key.endswith("major")


def test_detect_key_minor(monkeypatch: pytest.MonkeyPatch) -> None:
    chroma = np.zeros((12, 10), dtype=np.float32)
    chroma[9, :] = 1.0

    class DummyFeature:
        @staticmethod
        def chroma_stft(y: np.ndarray, sr: int) -> np.ndarray:
            return chroma

    class DummyLibrosa:
        feature = DummyFeature

    monkeypatch.setitem(__import__("sys").modules, "librosa", DummyLibrosa)

    audio = np.zeros(22050, dtype=np.float32)
    key = detect_key(audio, 22050)
    assert key.endswith("minor")
