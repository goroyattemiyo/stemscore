"""StemScore CLI entry point."""
from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
import typer

from stemscore import analyzer, assembler, router, separator, transcriber
from stemscore.config import GENRE_PRESETS
from stemscore.suno import import_suno

app = typer.Typer(
    name="stemscore",
    help="MP3 → 6-part MIDI/Score generator",
)


@app.command()
def transcribe(
    input_path: str = typer.Argument(..., help="Input audio file or Suno export directory"),
    output_dir: str = typer.Option("./output", help="Output directory"),
    parts: str = typer.Option(
        "lead_vocal,backing_vocal,bass,drums,backing_harmony,chords",
        help="Comma-separated parts to extract",
    ),
    genre: str = typer.Option("pop", help="Genre preset"),
    format: str = typer.Option("midi,musicxml", help="Output formats"),
) -> None:
    """Transcribe audio into multi-part score."""
    console = Console()
    input_path_obj = Path(input_path)
    output_dir_obj = Path(output_dir)
    requested_parts = [part.strip().lower() for part in parts.split(",") if part.strip()]
    formats_list = [fmt.strip().lower() for fmt in format.split(",") if fmt.strip()]
    preset = GENRE_PRESETS.get(genre, GENRE_PRESETS["pop"])

    route_selector = router.InputRouter()
    route = route_selector.route(input_path_obj)

    console.print(f"StemScore v0.1.0 — Processing: {input_path_obj}")
    console.print(f"Route: {route} | Parts: {', '.join(requested_parts)} | Genre: {genre}")

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    )

    analysis = None
    stems: dict[str, Path] = {}
    with progress:
        if route == "route_b":
            task = progress.add_task("Analyzing mix", total=1)
            analysis = analyzer.analyze(input_path_obj)
            progress.advance(task)

            task = progress.add_task("Separating stems", total=1)
            stems = separator.separate(
                input_path_obj,
                output_dir_obj / "stems",
                model=preset.separation.stage1_model,
            )
            progress.advance(task)

            stems = _map_route_b_stems(stems)
        elif route == "route_a":
            task = progress.add_task("Importing Suno stems", total=1)
            stems = import_suno(input_path_obj)
            progress.advance(task)

            task = progress.add_task("Analyzing stems", total=1)
            analysis_path = _select_analysis_stem(stems)
            analysis = analyzer.analyze(analysis_path)
            progress.advance(task)
        else:
            raise typer.Exit(code=1)

        stems = _filter_parts(stems, requested_parts)
        if not stems:
            console.print("No matching stems found for requested parts")
            raise typer.Exit(code=1)

        task = progress.add_task("Transcribing stems", total=len(stems))
        note_parts: dict[str, list[dict]] = {}
        for part_name, stem_path in stems.items():
            result = transcriber.transcribe_part(stem_path, part_name, preset.transcription)
            note_parts[part_name] = result.notes
            progress.advance(task)

        task = progress.add_task("Assembling score", total=1)
        assembly = assembler.assemble(
            note_parts,
            tempo=analysis.tempo,
            key=analysis.key,
            time_signature=analysis.time_signature,
            output_dir=output_dir_obj,
            formats=formats_list,
            level=preset.assembly.quantize_level,
            swing=preset.assembly.swing_detection,
        )
        progress.advance(task)

    console.print("Summary")
    console.print(f"Tempo: {analysis.tempo}")
    console.print(f"Key: {analysis.key}")
    console.print(f"Time Signature: {analysis.time_signature}/4")
    for fmt, path in assembly.output_files.items():
        console.print(f"{fmt}: {path}")


@app.command()
def version() -> None:
    """Show version."""
    typer.echo("stemscore 0.1.0")


def _map_route_b_stems(stems: dict[str, Path]) -> dict[str, Path]:
    mapped: dict[str, Path] = {}
    route_map = {
        "vocals": "lead_vocal",
        "drums": "drums",
        "bass": "bass",
        "other": "backing_harmony",
    }
    for stem_name, stem_path in stems.items():
        mapped[route_map.get(stem_name.lower(), stem_name.lower())] = stem_path
    return mapped


def _filter_parts(stems: dict[str, Path], parts: list[str]) -> dict[str, Path]:
    if not parts:
        return stems
    return {name: path for name, path in stems.items() if name.lower() in parts}


def _select_analysis_stem(stems: dict[str, Path]) -> Path:
    if "lead_vocal" in stems:
        return stems["lead_vocal"]
    return next(iter(stems.values()))


if __name__ == "__main__":
    app()
