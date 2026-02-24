from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


def _score_bars(onset_env: np.ndarray, beat_frames: np.ndarray, beats_per_bar: int) -> float:
    if beat_frames.size == 0:
        return 0.0
    bar_starts = beat_frames[::beats_per_bar]
    if bar_starts.size == 0:
        return 0.0
    return float(onset_env[bar_starts].mean())


def detect_time_signature(audio: np.ndarray, sr: int, tempo: float) -> int:
    """Detect time signature as beats per bar.

    Args:
        audio: Audio samples (mono).
        sr: Sample rate.
        tempo: Estimated tempo in BPM.

    Returns:
        Beats per bar (3 or 4).
    """
    import librosa  # Lazy import for heavy dependency.

    logger.info("Detecting time signature (sr=%s, tempo=%.2f)", sr, tempo)
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    _, beat_frames = librosa.beat.beat_track(y=audio, sr=sr, bpm=tempo, units="frames")

    beat_frames = np.asarray(beat_frames, dtype=int)
    if beat_frames.size < 4:
        logger.warning("Insufficient beats for time signature detection, defaulting to 4")
        return 4

    score_3 = _score_bars(onset_env, beat_frames, 3)
    score_4 = _score_bars(onset_env, beat_frames, 4)
    return 3 if score_3 > score_4 else 4
