from __future__ import annotations

from pathlib import Path
import logging
import subprocess
import tempfile

import streamlit as st

from stemscore import pipeline

logger = logging.getLogger(__name__)


def render_app() -> None:
    """Render the Streamlit UI for StemScore."""
    st.set_page_config(title="StemScore", page_icon="🎵", layout="wide")

    st.title("StemScore")
    st.caption("MP3 → 6-Part Musical Score")

    st.info(
        "StemScore runs a multi-stage pipeline: analysis, separation (if needed), "
        "transcription, then assembly."
    )

    with st.expander("Pipeline Details"):
        st.write("Analysis: Detects tempo, key, and time signature.")
        st.write("Separation: Splits a full mix into stems (Route B only).")
        st.write("Transcription: Converts stems into note events.")
        st.write("Assembly: Quantizes notes and exports MIDI/MusicXML/PDF.")

    st.sidebar.header("Settings")

    # ジャンル選択
    genre = st.sidebar.selectbox("Genre", ["pop", "jazz", "edm"], index=0)

    st.sidebar.markdown("Parts")
    selected_parts: list[str] = []
    for part in [
        "lead_vocal",
        "backing_vocal",
        "bass",
        "drums",
        "backing_harmony",
        "chords",
    ]:
        # パート選択
        if st.sidebar.checkbox(part, value=True):
            selected_parts.append(part)

    # 出力フォーマット
    formats = st.sidebar.multiselect(
        "Output Formats",
        ["midi", "musicxml", "pdf"],
        default=["midi", "musicxml"],
    )

    # Suno クレジットモード
    credit_mode = st.sidebar.selectbox(
        "Suno Credit Mode",
        ["minimal", "full", "economy"],
        index=0,
    )
    _ = credit_mode

    col_upload, col_path = st.columns(2)
    with col_upload:
        # 音声ファイルアップロード
        uploaded_file = st.file_uploader(
            "Upload audio file", type=["mp3", "wav", "flac", "m4a"]
        )
    with col_path:
        # Suno エクスポートパス
        suno_path = st.text_input("Or enter Suno export directory")

    if st.button("Transcribe"):
        progress_bar = st.progress(0)
        try:
            input_path = _resolve_input_path(uploaded_file, suno_path)
            output_dir = Path("./output")
            progress_bar.progress(25)
            result = pipeline.run_pipeline(
                input_path=input_path,
                output_dir=output_dir,
                parts=selected_parts,
                genre=genre,
                formats=formats,
            )
            progress_bar.progress(100)

            metrics = st.columns(3)
            metrics[0].metric("Tempo", f"{result['tempo']:.1f} bpm")
            metrics[1].metric("Key", result["key"])
            metrics[2].metric("Time Signature", f"{result['time_signature']}/4")

            for fmt, path in result["output_files"].items():
                if path.exists():
                    st.download_button(
                        label=f"Download {fmt}",
                        data=path.read_bytes(),
                        file_name=path.name,
                    )

            if "musicxml" in result["output_files"]:
                st.success(f"MusicXML exported to {result['output_files']['musicxml']}")
        except Exception as exc:
            logger.exception("Pipeline failed")
            st.error(f"Failed to process input: {exc}")


def _resolve_input_path(uploaded_file: object | None, suno_path: str) -> Path:
    if uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
            handle.write(uploaded_file.read())
            return Path(handle.name)
    if suno_path:
        return Path(suno_path)
    raise ValueError("No input provided")


def main() -> None:
    """Launch the Streamlit app."""
    subprocess.run(["streamlit", "run", __file__], check=False)


render_app()
