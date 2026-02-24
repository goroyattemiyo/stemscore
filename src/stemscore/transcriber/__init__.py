from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging

from stemscore.config import TranscriptionConfig
from stemscore.transcriber.chord_recognizer import recognize_chords
from stemscore.transcriber.drum_transcriber import transcribe_drums
from stemscore.transcriber.pitch_transcriber import transcribe_pitch

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TranscriptionResult:
    """Output from a transcription stage."""

    notes: list[dict]
    part_name: str
    method: str


def transcribe_part(audio_path: Path, part: str, config: TranscriptionConfig) -> TranscriptionResult:
    """Dispatch transcription based on part name."""
    logger.info("Dispatching transcription for part %s", part)
    normalized = part.lower()
    if normalized == "drums":
        notes = transcribe_drums(audio_path, num_classes=config.drum_classes)
        method = "onset_heuristic"
    elif normalized in {"chords", "harmony"}:
        notes = recognize_chords(audio_path)
        method = "chroma_template"
    else:
        notes = transcribe_pitch(audio_path, min_note_ms=config.vocal_min_note_ms)
        method = "basic_pitch"
    return TranscriptionResult(notes=notes, part_name=part, method=method)


__all__ = ["TranscriptionResult", "transcribe_part"]
