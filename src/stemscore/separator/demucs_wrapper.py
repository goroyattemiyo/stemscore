from __future__ import annotations

from pathlib import Path
import logging

from stemscore.utils.exceptions import SeparationError

logger = logging.getLogger(__name__)


def separate(audio_path: Path, output_dir: Path, model: str = "htdemucs_ft") -> dict[str, Path]:
    """Separate an audio file into stems using Demucs.

    Args:
        audio_path: Path to the input audio file.
        output_dir: Directory to write separated stems.
        model: Demucs model name.

    Returns:
        Mapping of stem names to output WAV paths.

    Raises:
        SeparationError: If separation fails for any reason.
    """
    logger.info("Starting separation for %s", audio_path)
    if not audio_path.exists():
        raise SeparationError(f"Input audio not found: {audio_path}")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Using Demucs model %s", model)

        from demucs.api import Separator, save_audio  # lazy import for heavy deps

        separator = Separator(model=model)
        result = separator.separate_audio_file(audio_path)
        stems_audio = _extract_stems(result)

        stems: dict[str, Path] = {}
        for stem_name, stem_audio in stems_audio.items():
            stem_path = output_dir / f"{stem_name}.wav"
            save_audio(stem_audio, stem_path, samplerate=separator.samplerate)
            stems[stem_name] = stem_path
            logger.info("Wrote stem %s to %s", stem_name, stem_path)

        logger.info("Separation complete: %s stems", len(stems))
        return stems
    except SeparationError:
        raise
    except Exception as exc:  # pragma: no cover - defensive wrapper
        logger.exception("Separation failed")
        raise SeparationError("Demucs separation failed") from exc


def _extract_stems(result: object) -> dict[str, object]:
    """Normalize Demucs output into a stem dictionary."""
    if isinstance(result, dict):
        return result
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
        return result[1]
    raise SeparationError("Unexpected Demucs separation result format")
