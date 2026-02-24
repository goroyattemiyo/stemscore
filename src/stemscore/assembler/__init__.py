from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging

from stemscore.assembler.exporter import export_score
from stemscore.assembler.merger import merge_parts
from stemscore.assembler.quantizer import quantize_notes

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AssemblyResult:
    """Result metadata for assembled scores."""

    output_files: dict[str, Path]
    num_parts: int
    total_notes: int


def assemble(
    parts: dict[str, list[dict]],
    tempo: float,
    key: str,
    time_signature: int,
    output_dir: Path,
    formats: list[str],
    level: int = 16,
    swing: bool = False,
) -> AssemblyResult:
    """Quantize, merge, and export a score.

    Args:
        parts: Mapping of part name to note dictionaries.
        tempo: Tempo in BPM.
        key: Key signature string (e.g., "C", "Gm").
        time_signature: Time signature numerator (e.g., 4 for 4/4).
        output_dir: Directory to write output files into.
        formats: List of output formats (midi, musicxml, pdf).
        level: Quantization level (e.g., 16 for 16th notes).
        swing: Whether to apply swing quantization.

    Returns:
        AssemblyResult with output file paths and summary stats.
    """
    quantized_parts: dict[str, list[dict]] = {}
    total_notes = 0

    for part_name, notes in parts.items():
        quantized = quantize_notes(notes, tempo=tempo, level=level, swing=swing)
        quantized_parts[part_name] = quantized
        total_notes += len(quantized)

    score = merge_parts(quantized_parts, tempo=tempo, key=key, time_signature=time_signature)
    output_files = export_score(score, output_dir=output_dir, formats=formats)

    logger.info("Assembled score with %s parts and %s notes", len(parts), total_notes)
    return AssemblyResult(output_files=output_files, num_parts=len(parts), total_notes=total_notes)


__all__ = ["AssemblyResult", "assemble", "export_score", "merge_parts", "quantize_notes"]
