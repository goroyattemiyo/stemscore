from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

TICKS_PER_BEAT = 480

PART_NAME_MAP = {
    "lead_vocal": "Soprano",
    "backing_vocal": "Alto",
    "bass": "Bass",
    "drums": "Percussion",
    "backing_harmony": "Piano",
    "chords": "Guitar",
}


def merge_parts(
    parts: dict[str, list[dict]],
    tempo: float,
    key: str,
    time_signature: int,
) -> object:
    """Merge part note dictionaries into a music21 Score.

    Args:
        parts: Mapping of part name to note dictionaries.
        tempo: Tempo in BPM.
        key: Key signature string (e.g., "C", "Gm").
        time_signature: Time signature numerator (e.g., 4 for 4/4).

    Returns:
        A music21 Score object.
    """
    if tempo <= 0:
        raise ValueError("Tempo must be positive")
    if time_signature <= 0:
        raise ValueError("Time signature must be positive")

    from music21 import instrument, key as mkey, meter, note, stream, tempo as mtempo

    score = stream.Score()
    score.insert(0, mtempo.MetronomeMark(number=tempo))
    score.insert(0, mkey.Key(key))
    score.insert(0, meter.TimeSignature(f"{time_signature}/4"))

    for part_name, notes in parts.items():
        part = stream.Part()
        part.id = part_name
        part_name_mapped = PART_NAME_MAP.get(part_name, part_name.title())
        part.partName = part_name_mapped

        instrument_class = _instrument_for_name(part_name, instrument)
        part.append(instrument_class())

        for note_dict in notes:
            _insert_note(part, note_dict, note, part_name)

        score.append(part)

    logger.info("Merged %s parts into score", len(parts))
    return score


def _instrument_for_name(part_name: str, instrument_module: object) -> type:
    if part_name == "lead_vocal":
        return instrument_module.Soprano
    if part_name == "backing_vocal":
        return instrument_module.Alto
    if part_name == "bass":
        return instrument_module.Bass
    if part_name == "drums":
        return instrument_module.Percussion
    if part_name == "backing_harmony":
        return instrument_module.Piano
    if part_name == "chords":
        return instrument_module.Guitar
    return instrument_module.Instrument


def _insert_note(part: object, note_dict: dict, note_module: object, part_name: str) -> None:
    tick = _coerce_float(note_dict, "tick")
    duration_ticks = _coerce_float(note_dict, "duration_ticks")

    if tick is None or duration_ticks is None:
        start = _coerce_float(note_dict, "start")
        end = _coerce_float(note_dict, "end")
        if start is None or end is None:
            logger.warning("Skipping note without timing data: %s", note_dict)
            return
        tick = start * TICKS_PER_BEAT
        duration_ticks = max((end - start) * TICKS_PER_BEAT, 1.0)

    offset_quarter = tick / TICKS_PER_BEAT
    duration_quarter = duration_ticks / TICKS_PER_BEAT

    if part_name == "drums":
        event = note_module.Unpitched()
    else:
        pitch = _coerce_int(note_dict, "pitch")
        if pitch is None:
            logger.warning("Skipping note without pitch: %s", note_dict)
            return
        event = note_module.Note(int(pitch))

    event.duration.quarterLength = duration_quarter
    part.insert(offset_quarter, event)


def _coerce_float(note_dict: dict, key: str) -> float | None:
    if key not in note_dict:
        return None
    return float(note_dict[key])


def _coerce_int(note_dict: dict, key: str) -> int | None:
    if key not in note_dict:
        return None
    return int(note_dict[key])
