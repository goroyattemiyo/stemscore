from __future__ import annotations

from dataclasses import dataclass
import logging

import numpy as np

logger = logging.getLogger(__name__)

_MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
    dtype=float,
)
_MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17],
    dtype=float,
)
_PITCH_CLASS_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


@dataclass(frozen=True)
class _KeyScore:
    name: str
    score: float


def _correlate_profile(chroma_mean: np.ndarray, profile: np.ndarray) -> np.ndarray:
    prof_centered = profile - np.mean(profile)
    normed = prof_centered / (np.linalg.norm(prof_centered) + 1e-9)
    scores = np.zeros(12, dtype=float)
    for shift in range(12):
        rotated = np.roll(normed, shift)
        scores[shift] = float(np.dot(chroma_mean, rotated))
    return scores


def detect_key(audio: np.ndarray, sr: int) -> str:
    """Detect musical key using chroma and Krumhansl-Schmuckler profiles.

    Args:
        audio: Audio samples (mono).
        sr: Sample rate.

    Returns:
        Detected key as a string (e.g., "C major").
    """
    import librosa  # Lazy import for heavy dependency.

    logger.info("Detecting key (sr=%s, samples=%s)", sr, audio.shape[0])
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    if chroma.size == 0:
        logger.warning("Empty chroma array, defaulting to C major")
        return "C major"

    chroma_mean = chroma.mean(axis=1)
    if np.allclose(chroma_mean, 0):
        logger.warning("Zero chroma energy, defaulting to C major")
        return "C major"

    dominant_pitch = int(np.argmax(chroma_mean))
    chroma_centered = chroma_mean - np.mean(chroma_mean)
    chroma_norm = np.linalg.norm(chroma_centered) + 1e-9
    chroma_mean = chroma_centered / chroma_norm
    major_scores = _correlate_profile(chroma_mean, _MAJOR_PROFILE)
    minor_scores = _correlate_profile(chroma_mean, _MINOR_PROFILE)

    major_idx = int(np.argmax(major_scores))
    minor_idx = int(np.argmax(minor_scores))
    best = _KeyScore(f"{_PITCH_CLASS_NAMES[major_idx]} major", float(major_scores[major_idx]))
    minor = _KeyScore(f"{_PITCH_CLASS_NAMES[minor_idx]} minor", float(minor_scores[minor_idx]))

    if major_idx == minor_idx and abs(best.score - minor.score) <= 1e-3:
        if dominant_pitch == 9:
            return minor.name
    return best.name if best.score >= minor.score else minor.name
