from __future__ import annotations

from pathlib import Path
import logging

import numpy as np

from stemscore.utils.audio_io import load_audio
from stemscore.utils.exceptions import TranscriptionError

logger = logging.getLogger(__name__)


def transcribe_drums(audio_path: Path, num_classes: int = 9) -> list[dict]:
    """Transcribe drum hits using onset detection and spectral heuristics.

    Args:
        audio_path: Path to the input audio file.
        num_classes: Number of drum classes to map into GM MIDI notes.

    Returns:
        List of drum event dictionaries.

    Raises:
        TranscriptionError: If transcription fails.
    """
    logger.info("Transcribing drums for %s", audio_path)
    if not audio_path.exists():
        raise TranscriptionError(f"Input audio not found: {audio_path}")

    try:
        import librosa  # lazy import for heavy deps

        audio, sr = load_audio(audio_path)
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        if len(onset_frames) == 0:
            logger.info("No drum onsets detected for %s", audio_path)
            return []

        times = librosa.frames_to_time(onset_frames, sr=sr)
        centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)

        max_env = float(np.max(onset_env)) if onset_env.size else 1.0
        gm_notes = _gm_note_classes(num_classes)

        events: list[dict] = []
        for frame, time_sec in zip(onset_frames, times):
            frame_idx = min(frame, centroid.shape[1] - 1)
            centroid_hz = float(centroid[0, frame_idx])
            pitch = _map_centroid_to_gm(centroid_hz, gm_notes)
            velocity = _velocity_from_env(onset_env, frame, max_env)
            events.append(
                {
                    "start": float(time_sec),
                    "pitch": int(pitch),
                    "velocity": int(velocity),
                }
            )

        logger.info("Transcribed %s drum hits for %s", len(events), audio_path)
        return events
    except TranscriptionError:
        raise
    except Exception as exc:  # pragma: no cover - defensive wrapper
        logger.exception("Drum transcription failed")
        raise TranscriptionError("Drum transcription failed") from exc


def _gm_note_classes(num_classes: int) -> list[int]:
    base = [36, 38, 42, 46, 41, 45, 49, 51, 57]
    if num_classes <= 0:
        return [36]
    if num_classes <= len(base):
        return base[:num_classes]
    return base + [42] * (num_classes - len(base))


def _map_centroid_to_gm(centroid_hz: float, gm_notes: list[int]) -> int:
    if len(gm_notes) == 1:
        return gm_notes[0]
    normalized = min(max(centroid_hz / 5000.0, 0.0), 0.999)
    index = int(normalized * len(gm_notes))
    return gm_notes[index]


def _velocity_from_env(onset_env: np.ndarray, frame: int, max_env: float) -> int:
    if onset_env.size == 0 or max_env <= 0:
        return 80
    value = float(onset_env[min(frame, onset_env.shape[0] - 1)])
    normalized = min(max(value / max_env, 0.0), 1.0)
    return int(1 + normalized * 126)
