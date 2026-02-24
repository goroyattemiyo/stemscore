from __future__ import annotations

from pathlib import Path
import json
import logging

from stemscore import analyzer, assembler, router, separator, transcriber
from stemscore.config import GENRE_PRESETS, GenrePreset
from stemscore.suno import import_suno

logger = logging.getLogger(__name__)


_ROUTE_B_MAP = {
    "vocals": "lead_vocal",
    "drums": "drums",
    "bass": "bass",
    "other": "backing_harmony",
}


def run_pipeline(
    input_path: Path,
    output_dir: Path,
    parts: list[str],
    genre: str,
    formats: list[str],
) -> dict:
    """Run the end-to-end StemScore pipeline.

    Args:
        input_path: Input mix or Suno export directory.
        output_dir: Directory to write outputs.
        parts: Requested parts to process.
        genre: Genre preset name.
        formats: Output formats.

    Returns:
        Dictionary containing analysis results and output files.
    """
    preset = _resolve_genre(genre)
    requested_parts = [part.lower() for part in parts]

    route_selector = router.InputRouter()
    route = route_selector.route(input_path)

    if route == "route_b":
        analysis = analyzer.analyze(input_path)
        stems = separator.separate(
            input_path,
            output_dir / "stems",
            model=preset.separation.stage1_model,
        )
        mapped = _map_route_b_stems(stems)
    elif route == "route_a":
        stems = import_suno(input_path)
        analysis_path = _select_analysis_stem(stems)
        analysis = analyzer.analyze(analysis_path)
        mapped = stems
        tempo_override = _read_suno_tempo(input_path)
        if tempo_override is not None:
            analysis = analyzer.AnalysisResult(
                tempo=tempo_override,
                key=analysis.key,
                time_signature=analysis.time_signature,
            )
    else:
        raise ValueError(f"Unsupported route: {route}")

    filtered = _filter_parts(mapped, requested_parts)
    if not filtered:
        raise ValueError("No matching stems found for requested parts")

    note_parts: dict[str, list[dict]] = {}
    for part_name, stem_path in filtered.items():
        result = transcriber.transcribe_part(stem_path, part_name, preset.transcription)
        note_parts[part_name] = result.notes

    assembly = assembler.assemble(
        note_parts,
        tempo=analysis.tempo,
        key=analysis.key,
        time_signature=analysis.time_signature,
        output_dir=output_dir,
        formats=formats,
        level=preset.assembly.quantize_level,
        swing=preset.assembly.swing_detection,
    )

    logger.info("Pipeline complete for %s", input_path)
    return {
        "route": route,
        "tempo": analysis.tempo,
        "key": analysis.key,
        "time_signature": analysis.time_signature,
        "output_files": assembly.output_files,
        "num_parts": assembly.num_parts,
        "total_notes": assembly.total_notes,
    }


def _resolve_genre(genre: str) -> GenrePreset:
    return GENRE_PRESETS.get(genre, GENRE_PRESETS["pop"])


def _map_route_b_stems(stems: dict[str, Path]) -> dict[str, Path]:
    mapped: dict[str, Path] = {}
    for stem_name, stem_path in stems.items():
        part_name = _ROUTE_B_MAP.get(stem_name.lower(), stem_name.lower())
        mapped[part_name] = stem_path
    return mapped


def _filter_parts(stems: dict[str, Path], parts: list[str]) -> dict[str, Path]:
    if not parts:
        return stems
    return {name: path for name, path in stems.items() if name.lower() in parts}


def _select_analysis_stem(stems: dict[str, Path]) -> Path:
    if "lead_vocal" in stems:
        return stems["lead_vocal"]
    return next(iter(stems.values()))


def _read_suno_tempo(input_dir: Path) -> float | None:
    metadata_path = input_dir / "metadata.json"
    if not metadata_path.exists():
        return None
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("Malformed Suno metadata: %s", metadata_path)
        return None
    if isinstance(payload, dict) and "tempo" in payload:
        try:
            return float(payload["tempo"])
        except (TypeError, ValueError):
            logger.warning("Invalid tempo in Suno metadata: %s", payload.get("tempo"))
    return None
