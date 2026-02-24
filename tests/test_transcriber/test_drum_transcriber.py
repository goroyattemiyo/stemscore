from __future__ import annotations

from pathlib import Path
import sys
from types import ModuleType

import numpy as np
import pytest

from stemscore.transcriber.drum_transcriber import transcribe_drums


def _install_fake_librosa(monkeypatch: pytest.MonkeyPatch) -> None:
    librosa = ModuleType("librosa")
    onset = ModuleType("librosa.onset")
    feature = ModuleType("librosa.feature")

    def onset_strength(y: np.ndarray, sr: int) -> np.ndarray:
        return np.array([0.1, 0.8, 0.2])

    def onset_detect(onset_envelope: np.ndarray, sr: int) -> np.ndarray:
        return np.array([0, 1])

    def frames_to_time(frames: np.ndarray, sr: int) -> np.ndarray:
        return np.array([0.0, 0.5])

    def spectral_centroid(y: np.ndarray, sr: int) -> np.ndarray:
        return np.array([[100.0, 3000.0]])

    onset.onset_strength = onset_strength
    onset.onset_detect = onset_detect
    librosa.frames_to_time = frames_to_time
    feature.spectral_centroid = spectral_centroid
    librosa.onset = onset
    librosa.feature = feature

    monkeypatch.setitem(sys.modules, "librosa", librosa)
    monkeypatch.setitem(sys.modules, "librosa.onset", onset)
    monkeypatch.setitem(sys.modules, "librosa.feature", feature)


def test_transcribe_drums_maps_to_gm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    audio_path = tmp_path / "drums.wav"
    audio_path.write_bytes(b"fake")

    _install_fake_librosa(monkeypatch)
    monkeypatch.setattr(
        "stemscore.transcriber.drum_transcriber.load_audio",
        lambda path: (np.zeros(10), 22050),
    )

    events = transcribe_drums(audio_path, num_classes=3)

    assert len(events) == 2
    assert events[0]["pitch"] in {36, 38, 42}
    assert events[1]["pitch"] in {36, 38, 42}
