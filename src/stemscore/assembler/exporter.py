from __future__ import annotations

from pathlib import Path
import logging

logger = logging.getLogger(__name__)


_FORMAT_MAP = {
    "midi": ("midi", ".mid"),
    "mid": ("midi", ".mid"),
    "musicxml": ("musicxml", ".musicxml"),
    "xml": ("musicxml", ".musicxml"),
    "pdf": ("musicxml.pdf", ".pdf"),
}


def export_score(score: object, output_dir: Path, formats: list[str]) -> dict[str, Path]:
    """Export a music21 score to requested formats.

    Args:
        score: music21 Score-like object with a write() method.
        output_dir: Directory to write output files into.
        formats: List of format strings (midi, musicxml, pdf).

    Returns:
        Mapping of format key to output file path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    for fmt in formats:
        fmt_key = fmt.lower()
        if fmt_key not in _FORMAT_MAP:
            logger.warning("Skipping unsupported format: %s", fmt)
            continue
        music21_fmt, suffix = _FORMAT_MAP[fmt_key]
        output_path = output_dir / f"score{suffix}"
        score.write(music21_fmt, fp=str(output_path))
        written[fmt_key] = output_path

    logger.info("Exported score formats: %s", list(written))
    return written
