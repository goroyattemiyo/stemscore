from __future__ import annotations

import sys
import types

from stemscore.assembler import merger


def test_merge_parts_creates_score_and_parts(monkeypatch) -> None:
    class FakeScore:
        def __init__(self) -> None:
            self.inserted: list[object] = []
            self.parts: list[object] = []

        def insert(self, offset: float, obj: object) -> None:
            self.inserted.append((offset, obj))

        def append(self, part: object) -> None:
            self.parts.append(part)

    class FakePart:
        def __init__(self) -> None:
            self.id = None
            self.partName = None
            self.appended: list[object] = []
            self.inserted: list[object] = []

        def append(self, obj: object) -> None:
            self.appended.append(obj)

        def insert(self, offset: float, obj: object) -> None:
            self.inserted.append((offset, obj))

    class FakeInstrument:
        pass

    class FakeTempo:
        class MetronomeMark:
            def __init__(self, number: float) -> None:
                self.number = number

    class FakeMeter:
        class TimeSignature:
            def __init__(self, value: str) -> None:
                self.value = value

    class FakeKey:
        class Key:
            def __init__(self, value: str) -> None:
                self.value = value

    class FakeNote:
        class Note:
            def __init__(self, pitch: int) -> None:
                self.pitch = pitch
                self.duration = types.SimpleNamespace(quarterLength=0.0)

        class Unpitched:
            def __init__(self) -> None:
                self.duration = types.SimpleNamespace(quarterLength=0.0)

    class FakeStream:
        Score = FakeScore
        Part = FakePart

    class FakeInstrumentModule:
        Soprano = FakeInstrument
        Alto = FakeInstrument
        Bass = FakeInstrument
        Percussion = FakeInstrument
        Piano = FakeInstrument
        Guitar = FakeInstrument
        Instrument = FakeInstrument

    fake_music21 = types.ModuleType("music21")
    fake_music21.instrument = FakeInstrumentModule
    fake_music21.key = FakeKey
    fake_music21.meter = FakeMeter
    fake_music21.note = FakeNote
    fake_music21.stream = FakeStream
    fake_music21.tempo = FakeTempo

    monkeypatch.setitem(sys.modules, "music21", fake_music21)
    monkeypatch.setattr(merger, "_instrument_for_name", lambda name, module: module.Instrument)

    parts = {
        "lead_vocal": [{"tick": 0, "duration_ticks": 120, "pitch": 60}],
        "drums": [{"tick": 0, "duration_ticks": 120}],
    }

    score = merger.merge_parts(parts, tempo=120.0, key="C", time_signature=4)

    assert isinstance(score, FakeScore)
    assert len(score.parts) == 2
    assert {part.id for part in score.parts} == {"lead_vocal", "drums"}
