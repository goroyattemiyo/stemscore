from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


def detect_tempo(audio: np.ndarray, sr: int) -> float:
    """Detect tempo in beats per minute.

    Args:
        audio: Audio samples (mono).
        sr: Sample rate.

    Returns:
        Estimated tempo in BPM.
    """
    import librosa  # Lazy import for heavy dependency.

    logger.info("Detecting tempo (sr=%s, samples=%s)", sr, audio.shape[0])
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    return float(np.asarray(tempo).flatten()[0])
