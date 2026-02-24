from __future__ import annotations

from stemscore.assembler.quantizer import quantize_notes


def test_quantize_snaps_to_grid() -> None:
    notes = [
        {"start": 0.13, "end": 0.36, "pitch": 60, "velocity": 100},
    ]

    quantized = quantize_notes(notes, tempo=120.0, level=16)

    assert len(quantized) == 1
    note = quantized[0]
    assert note["tick"] == 120
    assert note["duration_ticks"] == 240
    assert note["start"] == 0.125
    assert note["end"] == 0.375
