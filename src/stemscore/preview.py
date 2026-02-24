from __future__ import annotations

from pathlib import Path
import base64
import tempfile

import matplotlib.pyplot as plt

_COLOR_PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
]


def midi_to_piano_roll(midi_path: Path):
    """Create a piano roll figure from a MIDI file.

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        Matplotlib figure representing a piano roll.
    """
    score = _load_score(midi_path)
    fig, ax = plt.subplots(figsize=(10, 4))

    part_labels: set[str] = set()
    for idx, part in enumerate(score.parts):
        color = _COLOR_PALETTE[idx % len(_COLOR_PALETTE)]
        label = part.partName or part.id or f"Part {idx + 1}"
        for element in part.recurse().notes:
            for pitch in _extract_pitches(element):
                start = float(element.offset)
                duration = float(element.duration.quarterLength)
                ax.broken_barh([(start, duration)], (pitch - 0.4, 0.8), facecolors=color)
        part_labels.add(label)
        ax.plot([], [], color=color, label=label)

    ax.set_xlabel("Beats")
    ax.set_ylabel("MIDI Pitch")
    ax.legend(loc="upper right", fontsize="small")
    ax.set_title("Piano Roll")
    ax.grid(True, axis="x", linestyle=":", alpha=0.4)

    return fig


def midi_to_simple_score(midi_path: Path):
    """Create a simplified staff notation view for the lead vocal part.

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        Matplotlib figure showing a simple staff with note heads.
    """
    score = _load_score(midi_path)
    part = _select_lead_part(score)

    fig, ax = plt.subplots(figsize=(10, 3))
    _draw_staff(ax)

    notes = list(part.recurse().notes)
    for element in notes:
        for pitch in _extract_pitches(element):
            x = float(element.offset)
            y = _pitch_to_staff(pitch)
            ax.scatter([x], [y], s=40, color="#1f77b4")

    _draw_bar_lines(ax, score, notes)

    ax.set_yticks([])
    ax.set_xlabel("Beats")
    ax.set_title("Simple Score")
    ax.set_xlim(left=0)

    return fig


def render_preview_html(midi_path: Path) -> str:
    """Render a MusicXML preview using OpenSheetMusicDisplay.

    Args:
        midi_path: Path to a MIDI file.

    Returns:
        HTML string for embedding with Streamlit.
    """
    score = _load_score(midi_path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".musicxml") as handle:
        score.write("musicxml", fp=handle.name)
        musicxml_path = Path(handle.name)

    xml_bytes = musicxml_path.read_bytes()
    encoded = base64.b64encode(xml_bytes).decode("utf-8")

    html = f"""
    <div id="osmd-container"></div>
    <script src="https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.8.9/build/opensheetmusicdisplay.min.js"></script>
    <script>
      const xmlData = atob("{encoded}");
      const osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay("osmd-container");
      osmd.load(xmlData).then(() => osmd.render());
    </script>
    """
    return html


def _load_score(midi_path: Path) -> object:
    from music21 import converter

    return converter.parse(str(midi_path))


def _extract_pitches(element: object) -> list[int]:
    if hasattr(element, "pitches"):
        return [int(p.midi) for p in element.pitches]
    if hasattr(element, "pitch"):
        return [int(element.pitch.midi)]
    return []


def _select_lead_part(score: object) -> object:
    for part in score.parts:
        if (part.id and part.id.lower() == "lead_vocal") or (
            part.partName and "lead" in part.partName.lower()
        ):
            return part
    return score.parts[0]


def _draw_staff(ax: object) -> None:
    for line in range(5):
        ax.hlines(line, 0, 100, color="#999", linewidth=0.8)


def _pitch_to_staff(pitch: int) -> float:
    return (pitch - 60) / 2.0


def _draw_bar_lines(ax: object, score: object, notes: list[object]) -> None:
    time_signature = score.recurse().getElementsByClass("TimeSignature")
    numerator = 4
    if time_signature:
        numerator = int(time_signature[0].numerator)

    max_offset = 0.0
    if notes:
        last_note = notes[-1]
        max_offset = float(last_note.offset + last_note.duration.quarterLength)

    measure = 0
    while measure * numerator <= max_offset:
        x = measure * numerator
        ax.vlines(x, -1, 6, color="#666", linewidth=0.8)
        measure += 1
