from __future__ import annotations

from pathlib import Path
import logging

import numpy as np

from stemscore.utils.audio_io import load_audio
from stemscore.utils.exceptions import TranscriptionError

logger = logging.getLogger(__name__)

PITCH_CLASS_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def recognize_chords(audio_path: Path) -> list[dict]:
    """Recognize chord changes using chroma template matching.

    Args:
        audio_path: Path to the input audio file.

    Returns:
        List of chord event dictionaries.

    Raises:
        TranscriptionError: If recognition fails.
    """
    logger.info("Recognizing chords for %s", audio_path)
    if not audio_path.exists():
        raise TranscriptionError(f"Input audio not found: {audio_path}")

    try:
        import librosa  # lazy import for heavy deps

        audio, sr = load_audio(audio_path)
        chroma = librosa.feature.chroma_cqt(y=audio, sr=sr)
        if chroma.size == 0:
            return []

        templates = _build_templates()
        labels = list(templates.keys())
        template_matrix = np.stack([templates[label] for label in labels], axis=0)

        norm_chroma = chroma / (np.linalg.norm(chroma, axis=0, keepdims=True) + 1e-6)
        scores = template_matrix @ norm_chroma
        best_indices = np.argmax(scores, axis=0)
        best_labels = [labels[idx] for idx in best_indices]

        hop_length = 512
        frame_times = librosa.frames_to_time(np.arange(chroma.shape[1] + 1), sr=sr, hop_length=hop_length)

        events: list[dict] = []
        current_label = best_labels[0]
        start_time = float(frame_times[0])
        for frame_idx in range(1, len(best_labels)):
            if best_labels[frame_idx] != current_label:
                end_time = float(frame_times[frame_idx])
                events.append({"start": start_time, "end": end_time, "chord": current_label})
                current_label = best_labels[frame_idx]
                start_time = float(frame_times[frame_idx])

        events.append(
            {
                "start": start_time,
                "end": float(frame_times[-1]),
                "chord": current_label,
            }
        )

        logger.info("Recognized %s chord segments for %s", len(events), audio_path)
        return events
    except TranscriptionError:
        raise
    except Exception as exc:  # pragma: no cover - defensive wrapper
        logger.exception("Chord recognition failed")
        raise TranscriptionError("Chord recognition failed") from exc


def _build_templates() -> dict[str, np.ndarray]:
    templates: dict[str, np.ndarray] = {}
    for root_idx, root_name in enumerate(PITCH_CLASS_NAMES):
        templates[f"{root_name}maj"] = _template(root_idx, [0, 4, 7])
        templates[f"{root_name}min"] = _template(root_idx, [0, 3, 7])
        templates[f"{root_name}7"] = _template(root_idx, [0, 4, 7, 10])
    return templates


def _template(root_idx: int, intervals: list[int]) -> np.ndarray:
    vector = np.zeros(12, dtype=float)
    for interval in intervals:
        vector[(root_idx + interval) % 12] = 1.0
    return vector / (np.linalg.norm(vector) + 1e-6)
