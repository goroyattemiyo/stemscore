from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging

from stemscore.analyzer.key_detect import detect_key
from stemscore.analyzer.tempo import detect_tempo
from stemscore.analyzer.time_sig import detect_time_signature
from stemscore.utils.audio_io import load_audio
from stemscore.utils.exceptions import AnalysisError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnalysisResult:
    """Analysis results from the Phase 1 analyzer."""

    tempo: float
    key: str
    time_signature: int


def analyze(audio_path: Path) -> AnalysisResult:
    """Analyze an audio file and return global musical attributes.

    Args:
        audio_path: Path to the audio file.

    Returns:
        AnalysisResult containing tempo, key, and time signature.

    Raises:
        AnalysisError: If analysis fails.
    """
    try:
        audio, sr = load_audio(audio_path)
        tempo = detect_tempo(audio, sr)
        key = detect_key(audio, sr)
        time_signature = detect_time_signature(audio, sr, tempo)
        return AnalysisResult(tempo=tempo, key=key, time_signature=time_signature)
    except Exception as exc:
        logger.exception("Analyzer failed for %s", audio_path)
        raise AnalysisError(f"Analyzer failed for {audio_path}") from exc


__all__ = ["AnalysisResult", "analyze"]
