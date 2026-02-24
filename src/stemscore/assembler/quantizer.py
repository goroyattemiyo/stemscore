from __future__ import annotations

from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

TICKS_PER_BEAT = 480


@dataclass(frozen=True)
class QuantizeSettings:
    tempo: float
    level: int = 16
    swing: bool = False

    @property
    def grid_size(self) -> float:
        return TICKS_PER_BEAT * 4 / self.level

    @property
    def ticks_per_second(self) -> float:
        return TICKS_PER_BEAT * (self.tempo / 60.0)


def quantize_notes(
    notes: list[dict],
    tempo: float,
    level: int = 16,
    swing: bool = False,
) -> list[dict]:
    """Snap note start/end times to the nearest rhythmic grid.

    Args:
        notes: List of note dictionaries with "start" and "end" in seconds.
        tempo: Tempo in BPM.
        level: Subdivision level (e.g., 16 for 16th notes).
        swing: Whether to apply a simple swing offset to off-beat positions.

    Returns:
        Quantized note dictionaries with "tick" and "duration_ticks" fields added.
    """
    if tempo <= 0:
        raise ValueError("Tempo must be positive")
    if level <= 0:
        raise ValueError("Level must be positive")

    settings = QuantizeSettings(tempo=tempo, level=level, swing=swing)
    grid_size = settings.grid_size
    ticks_per_second = settings.ticks_per_second

    quantized: list[dict] = []
    for note in notes:
        if "start" not in note or "end" not in note:
            raise ValueError("Note missing start/end times")

        start_ticks = float(note["start"]) * ticks_per_second
        end_ticks = float(note["end"]) * ticks_per_second

        snapped_start = _snap_ticks(start_ticks, grid_size, settings.swing)
        snapped_end = _snap_ticks(end_ticks, grid_size, settings.swing)

        if snapped_end <= snapped_start:
            snapped_end = snapped_start + grid_size

        duration_ticks = int(round(snapped_end - snapped_start))
        note_copy = dict(note)
        note_copy["tick"] = int(round(snapped_start))
        note_copy["duration_ticks"] = duration_ticks
        note_copy["start"] = note_copy["tick"] / ticks_per_second
        note_copy["end"] = (note_copy["tick"] + duration_ticks) / ticks_per_second

        quantized.append(note_copy)

    logger.info("Quantized %s notes at %sbpm level=%s", len(quantized), tempo, level)
    return quantized


def _snap_ticks(ticks: float, grid_size: float, swing: bool) -> float:
    if grid_size <= 0:
        return ticks
    grid_index = int(round(ticks / grid_size))
    snapped = grid_index * grid_size
    if swing and grid_index % 2 == 1:
        snapped += grid_size * 0.5
    return snapped
