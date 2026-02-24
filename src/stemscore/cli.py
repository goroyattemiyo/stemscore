"""StemScore CLI entry point."""
import typer

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
    typer.echo(f"StemScore v0.1.0 — Processing: {input_path}")
    typer.echo(f"Parts: {parts} | Genre: {genre} | Format: {format}")
    typer.echo("🚧 Pipeline not yet implemented. See docs/design/ for specification.")


@app.command()
def version() -> None:
    """Show version."""
    typer.echo("stemscore 0.1.0")


if __name__ == "__main__":
    app()
