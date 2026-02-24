from __future__ import annotations

from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


_PART_MAP = {
    "vocals": "lead_vocal",
    "backing_vox": "backing_vocal",
    "bass": "bass",
    "drums": "drums",
    "guitar": "backing_harmony",
    "synth": "backing_harmony",
    "pad": "backing_harmony",
    "keys": "backing_harmony",
}


def import_suno(input_dir: Path) -> dict[str, Path]:
    """Import Suno stems from an export directory.

    Args:
        input_dir: Suno export directory containing a stems/ subfolder.

    Returns:
        Mapping of part name to WAV path.

    Raises:
        FileNotFoundError: If no stems are found.
    """
    stems_dir = input_dir / "stems"
    if not stems_dir.exists():
        raise FileNotFoundError(f"Missing stems directory: {stems_dir}")

    _log_metadata(input_dir)

    stems: dict[str, Path] = {}
    for wav_path in stems_dir.glob("*.wav"):
        part_name = _map_stem_name(wav_path.stem.lower())
        if part_name is None:
            logger.info("Skipping unmapped stem: %s", wav_path.name)
            continue
        stems[part_name] = wav_path

    if not stems:
        raise FileNotFoundError(f"No supported stems found in {stems_dir}")

    logger.info("Imported %s Suno stems", len(stems))
    return stems


def _map_stem_name(stem_name: str) -> str | None:
    if stem_name in _PART_MAP:
        return _PART_MAP[stem_name]
    for key, value in _PART_MAP.items():
        if key in stem_name:
            return value
    return None


def _log_metadata(input_dir: Path) -> None:
    metadata_path = input_dir / "metadata.json"
    if not metadata_path.exists():
        return
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("Malformed Suno metadata: %s", metadata_path)
        return

    tempo = payload.get("tempo") if isinstance(payload, dict) else None
    if tempo is not None:
        logger.info("Suno metadata tempo: %s", tempo)
