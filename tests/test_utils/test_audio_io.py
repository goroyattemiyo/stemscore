from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest

from stemscore.utils.audio_io import load_audio, save_audio
from stemscore.utils.exceptions import AudioLoadError


def test_load_audio_calls_librosa(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    audio = np.zeros(10, dtype=np.float32)
    sr = 22050

    class DummyLibrosa:
        @staticmethod
        def load(path: Path, sr: int | None, mono: bool) -> tuple[np.ndarray, int]:
            assert path == tmp_path / "test.wav"
            assert sr is None
            assert mono is True
            return audio, sr

    monkeypatch.setitem(__import__("sys").modules, "librosa", DummyLibrosa)

    result_audio, result_sr = load_audio(tmp_path / "test.wav")
    assert np.array_equal(result_audio, audio)
    assert result_sr == sr


def test_load_audio_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class DummyLibrosa:
        @staticmethod
        def load(path: Path, sr: int | None, mono: bool) -> tuple[np.ndarray, int]:
            raise RuntimeError("boom")

    monkeypatch.setitem(__import__("sys").modules, "librosa", DummyLibrosa)

    with pytest.raises(AudioLoadError):
        load_audio(tmp_path / "test.wav")


def test_save_audio_calls_soundfile(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    audio = np.zeros(10, dtype=np.float32)
    sr = 22050
    calls: dict[str, Any] = {}

    class DummySoundFile:
        @staticmethod
        def write(path: Path, data: np.ndarray, samplerate: int) -> None:
            calls["path"] = path
            calls["data"] = data
            calls["samplerate"] = samplerate

    monkeypatch.setitem(__import__("sys").modules, "soundfile", DummySoundFile)

    save_audio(tmp_path / "out.wav", audio, sr)
    assert calls["path"] == tmp_path / "out.wav"
    assert np.array_equal(calls["data"], audio)
    assert calls["samplerate"] == sr


def test_save_audio_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class DummySoundFile:
        @staticmethod
        def write(path: Path, data: np.ndarray, samplerate: int) -> None:
            raise RuntimeError("boom")

    monkeypatch.setitem(__import__("sys").modules, "soundfile", DummySoundFile)

    with pytest.raises(AudioLoadError):
        save_audio(tmp_path / "out.wav", np.zeros(10, dtype=np.float32), 22050)
