from __future__ import annotations

from pathlib import Path
import sys
from types import ModuleType

import pytest

from stemscore.separator.demucs_wrapper import separate
from stemscore.utils.exceptions import SeparationError


def _install_fake_demucs(
    monkeypatch: pytest.MonkeyPatch,
    *,
    result: object | None = None,
    raise_exc: Exception | None = None,
) -> list[tuple[object, Path, int]]:
    api = ModuleType("demucs.api")
    calls: list[tuple[object, Path, int]] = []

    class FakeSeparator:
        def __init__(self, model: str) -> None:
            self.model = model
            self.samplerate = 44_100

        def separate_audio_file(self, audio_path: Path) -> object:
            if raise_exc is not None:
                raise raise_exc
            return result

    def save_audio(audio: object, path: Path, samplerate: int) -> None:
        calls.append((audio, path, samplerate))

    api.Separator = FakeSeparator
    api.save_audio = save_audio

    demucs = ModuleType("demucs")
    demucs.api = api

    monkeypatch.setitem(sys.modules, "demucs", demucs)
    monkeypatch.setitem(sys.modules, "demucs.api", api)
    return calls


def test_separate_returns_stem_dict(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    audio_path = tmp_path / "input.wav"
    audio_path.write_bytes(b"fake")

    stems_audio = {"vocals": object(), "drums": object(), "bass": object(), "other": object()}
    _install_fake_demucs(monkeypatch, result=stems_audio)

    output_dir = tmp_path / "stems"
    stems = separate(audio_path, output_dir)

    assert set(stems.keys()) == set(stems_audio.keys())
    for stem_name, stem_path in stems.items():
        assert stem_path == output_dir / f"{stem_name}.wav"


def test_separate_raises_on_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    audio_path = tmp_path / "input.wav"
    audio_path.write_bytes(b"fake")

    _install_fake_demucs(monkeypatch, raise_exc=RuntimeError("boom"))

    with pytest.raises(SeparationError):
        separate(audio_path, tmp_path / "stems")


def test_output_paths_and_save_audio_calls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    audio_path = tmp_path / "input.wav"
    audio_path.write_bytes(b"fake")

    stems_audio = {"vocals": object(), "drums": object()}
    calls = _install_fake_demucs(monkeypatch, result=stems_audio)

    output_dir = tmp_path / "stems"
    stems = separate(audio_path, output_dir)

    assert len(calls) == len(stems_audio)
    for audio, path, samplerate in calls:
        assert path.parent == output_dir
        assert path.suffix == ".wav"
        assert samplerate == 44_100
        assert path in stems.values()
