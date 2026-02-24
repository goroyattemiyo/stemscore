from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from stemscore import preview


def _make_fake_score() -> SimpleNamespace:
    class FakeDuration:
        def __init__(self, quarter_length: float) -> None:
            self.quarterLength = quarter_length

    class FakePitch:
        def __init__(self, midi: int) -> None:
            self.midi = midi

    class FakeNote:
        def __init__(self, offset: float, duration: float, midi: int) -> None:
            self.offset = offset
            self.duration = FakeDuration(duration)
            self.pitch = FakePitch(midi)

    class FakePart:
        def __init__(self, part_id: str, part_name: str) -> None:
            self.id = part_id
            self.partName = part_name
            self._notes = [FakeNote(0.0, 1.0, 60), FakeNote(1.0, 0.5, 64)]

        def recurse(self) -> "FakePart":
            return self

        @property
        def notes(self):
            return self._notes

    class FakeScore:
        def __init__(self) -> None:
            self.parts = [FakePart("lead_vocal", "Lead Vocal")]

        def recurse(self) -> "FakeScore":
            return self

        def getElementsByClass(self, _name: str):
            return []

    return FakeScore()


def test_midi_to_piano_roll_returns_figure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(preview, "_load_score", lambda path: _make_fake_score())
    fig = mock.MagicMock()
    ax = mock.MagicMock()
    monkeypatch.setattr(preview, "plt", mock.MagicMock(subplots=lambda **_: (fig, ax)))

    midi_path = tmp_path / "test.mid"
    midi_path.write_bytes(b"MThd")

    result = preview.midi_to_piano_roll(midi_path)

    assert result is fig


def test_midi_to_simple_score_returns_figure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(preview, "_load_score", lambda path: _make_fake_score())
    fig = mock.MagicMock()
    ax = mock.MagicMock()
    monkeypatch.setattr(preview, "plt", mock.MagicMock(subplots=lambda **_: (fig, ax)))

    midi_path = tmp_path / "test.mid"
    midi_path.write_bytes(b"MThd")

    result = preview.midi_to_simple_score(midi_path)

    assert result is fig
