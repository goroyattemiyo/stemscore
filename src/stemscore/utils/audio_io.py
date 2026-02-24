from __future__ import annotations

from pathlib import Path
import logging

import numpy as np

from stemscore.utils.exceptions import AudioLoadError

logger = logging.getLogger(__name__)


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    """Load audio from disk.

    Args:
        path: Path to the audio file.

    Returns:
        A tuple of audio samples (mono) and sample rate.

    Raises:
        AudioLoadError: If loading fails.
    """
    try:
        import librosa  # Lazy import for heavy dependency.
    except Exception as exc:  # pragma: no cover - defensive for missing deps
        logger.exception("Failed to import librosa for audio loading: %s", path)
        raise AudioLoadError(f"Failed to import librosa for {path}") from exc

    try:
        logger.info("Loading audio: %s", path)
        audio, sr = librosa.load(path, sr=None, mono=True)
        if sr is None:
            logger.warning("librosa returned sr=None for %s; defaulting to 22050", path)
            sr = 22050
        logger.debug("Loaded audio: %s (sr=%s, samples=%s)", path, sr, audio.shape[0])
        return audio, int(sr)
    except Exception as exc:
        logger.exception("Failed to load audio: %s", path)
        raise AudioLoadError(f"Failed to load audio from {path}") from exc


def save_audio(path: Path, audio: np.ndarray, sr: int) -> None:
    """Save audio to disk.

    Args:
        path: Destination path for the audio file.
        audio: Audio samples.
        sr: Sample rate.

    Raises:
        AudioLoadError: If saving fails.
    """
    try:
        import soundfile as sf
    except Exception as exc:  # pragma: no cover - defensive for missing deps
        logger.exception("Failed to import soundfile for audio saving: %s", path)
        raise AudioLoadError(f"Failed to import soundfile for {path}") from exc

    try:
        logger.info("Saving audio: %s", path)
        sf.write(path, audio, sr)
    except Exception as exc:
        logger.exception("Failed to save audio: %s", path)
        raise AudioLoadError(f"Failed to save audio to {path}") from exc
