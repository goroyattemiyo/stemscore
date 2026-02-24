from __future__ import annotations

from pathlib import Path
import logging

from stemscore.utils.exceptions import TranscriptionError

logger = logging.getLogger(__name__)


def transcribe_pitch(audio_path: Path, min_note_ms: int = 80) -> list[dict]:
    """Transcribe melodic audio into note events using Basic Pitch.

    Args:
        audio_path: Path to the input audio file.
        min_note_ms: Minimum note length in milliseconds.

    Returns:
        List of note event dictionaries.

    Raises:
        TranscriptionError: If transcription fails.
    """
    logger.info("Transcribing pitch for %s", audio_path)
    if not audio_path.exists():
        raise TranscriptionError(f"Input audio not found: {audio_path}")

    try:
        from basic_pitch.inference import predict  # lazy import for heavy deps

        result = predict(str(audio_path))
        note_events = _extract_note_events(result)
        filtered: list[dict] = []
        min_note_seconds = max(min_note_ms, 0) / 1000.0

        for event in note_events:
            note = _normalize_note_event(event)
            if note["end"] - note["start"] < min_note_seconds:
                continue
            filtered.append(note)

        logger.info("Transcribed %s notes for %s", len(filtered), audio_path)
        return filtered
    except TranscriptionError:
        raise
    except Exception as exc:  # pragma: no cover - defensive wrapper
        logger.exception("Pitch transcription failed")
        raise TranscriptionError("Pitch transcription failed") from exc


def _extract_note_events(result: object) -> list[dict]:
    if isinstance(result, dict) and "note_events" in result:
        note_events = result["note_events"]
    elif isinstance(result, tuple) and len(result) >= 3:
        note_events = result[2]
    else:
        raise TranscriptionError("Unexpected Basic Pitch result format")

    if not isinstance(note_events, list):
        raise TranscriptionError("Basic Pitch note events must be a list")

    return note_events


def _normalize_note_event(event: object) -> dict:
    if not isinstance(event, dict):
        raise TranscriptionError("Note event must be a dict")

    start = _coerce_float(event, ("start", "start_time", "onset"))
    end = _coerce_float(event, ("end", "end_time", "offset"))
    pitch = _coerce_int(event, ("pitch", "note"))
    velocity = _coerce_int(event, ("velocity",), default=100)
    confidence = _coerce_float(event, ("confidence", "probability"), default=1.0)

    if start is None or end is None or pitch is None:
        raise TranscriptionError("Note event missing required fields")

    return {
        "start": float(start),
        "end": float(end),
        "pitch": int(pitch),
        "velocity": int(velocity),
        "confidence": float(confidence),
    }


def _coerce_float(event: dict, keys: tuple[str, ...], default: float | None = None) -> float | None:
    for key in keys:
        if key in event:
            return float(event[key])
    return default


def _coerce_int(event: dict, keys: tuple[str, ...], default: int | None = None) -> int | None:
    for key in keys:
        if key in event:
            return int(event[key])
    return default
