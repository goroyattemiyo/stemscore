from __future__ import annotations

from pathlib import Path
import logging
import subprocess
import tempfile

import streamlit as st

from stemscore import pipeline
from stemscore.i18n import t
from stemscore.preview import midi_to_piano_roll, midi_to_simple_score, render_preview_html

logger = logging.getLogger(__name__)


PART_KEYS = [
    "lead_vocal",
    "backing_vocal",
    "bass",
    "drums",
    "backing_harmony",
    "chords",
]


def render_app() -> None:
    """Render the Streamlit UI for StemScore."""
    st.set_page_config(title=t("app_title", "ja"), page_icon="🎵", layout="wide")

    if "lang_choice" not in st.session_state:
        st.session_state["lang_choice"] = "日本語"

    st.sidebar.header(t("settings_label", "ja"))
    lang_choice = st.sidebar.selectbox(t("language_label", "ja"), ["日本語", "English"], index=0)
    st.session_state["lang_choice"] = lang_choice
    lang = "ja" if lang_choice == "日本語" else "en"

    st.title(t("app_title", lang))
    st.caption(t("subtitle", lang))

    st.info(t("info_text", lang))

    with st.expander(t("pipeline_info_title", lang)):
        st.write(t("pipeline_step_analysis", lang))
        st.write(t("pipeline_step_separation", lang))
        st.write(t("pipeline_step_transcription", lang))
        st.write(t("pipeline_step_assembly", lang))

    st.sidebar.header(t("settings_label", lang))

    # ジャンル選択
    genre = st.sidebar.selectbox(t("genre_label", lang), ["pop", "jazz", "edm"], index=0)

    st.sidebar.markdown(t("parts_label", lang))
    selected_parts: list[str] = []
    for part in PART_KEYS:
        # パート選択
        if st.sidebar.checkbox(t(part, lang), value=True):
            selected_parts.append(part)

    # 出力フォーマット
    formats = st.sidebar.multiselect(
        t("format_label", lang),
        ["midi", "musicxml", "pdf"],
        default=["midi", "musicxml"],
    )

    # Suno クレジットモード
    credit_mode = st.sidebar.selectbox(
        t("credit_mode_label", lang),
        ["minimal", "full", "economy"],
        index=0,
    )
    _ = credit_mode

    col_upload, col_path = st.columns(2)
    with col_upload:
        # 音声ファイルアップロード
        uploaded_file = st.file_uploader(
            t("upload_label", lang), type=["mp3", "wav", "flac", "m4a"]
        )
    with col_path:
        # Suno エクスポートパス
        suno_path = st.text_input(t("suno_path_label", lang))

    if st.button(t("transcribe_button", lang)):
        progress_bar = st.progress(0)
        try:
            progress_bar.progress(10, text=t("processing", lang))
            input_path = _resolve_input_path(uploaded_file, suno_path)
            output_dir = Path("./output")
            result = pipeline.run_pipeline(
                input_path=input_path,
                output_dir=output_dir,
                parts=selected_parts,
                genre=genre,
                formats=formats,
            )
            progress_bar.progress(100)

            st.subheader(t("analysis_header", lang))
            metrics = st.columns(3)
            metrics[0].metric(t("tempo_label", lang), f"{result['tempo']:.1f} bpm")
            metrics[1].metric(t("key_label", lang), result["key"])
            metrics[2].metric(t("time_sig_label", lang), f"{result['time_signature']}/4")

            st.subheader(t("output_header", lang))
            for fmt, path in result["output_files"].items():
                if path.exists():
                    st.download_button(
                        label=f"{t('download_button', lang)} {fmt}",
                        data=path.read_bytes(),
                        file_name=path.name,
                    )

            if "musicxml" in result["output_files"]:
                st.success(t("success_message", lang))

            _render_preview(result, selected_parts, lang)
        except Exception as exc:
            logger.exception("Pipeline failed")
            st.error(f"{t('error_message', lang)}: {exc}")


def _render_preview(result: dict, selected_parts: list[str], lang: str) -> None:
    midi_path = result.get("output_files", {}).get("midi")
    if not midi_path:
        return

    st.subheader(t("preview_header", lang))

    preview_parts = st.multiselect(
        t("preview_parts_label", lang),
        [t(part, lang) for part in PART_KEYS],
        default=[t(part, lang) for part in selected_parts] if selected_parts else None,
    )
    preview_keys = _map_preview_parts(preview_parts, lang)
    preview_midi = _filter_midi_parts(Path(midi_path), preview_keys)

    tab_piano, tab_simple, tab_xml = st.tabs(
        [
            t("preview_tab_piano", lang),
            t("preview_tab_simple", lang),
            t("preview_tab_xml", lang),
        ]
    )

    with tab_piano:
        try:
            fig = midi_to_piano_roll(preview_midi)
            st.pyplot(fig)
        except Exception as exc:
            logger.exception("Piano roll preview failed")
            st.error(f"{t('preview_error', lang)}: {exc}")

    with tab_simple:
        try:
            fig = midi_to_simple_score(preview_midi)
            st.pyplot(fig)
        except Exception as exc:
            logger.exception("Simple score preview failed")
            st.error(f"{t('preview_error', lang)}: {exc}")

    with tab_xml:
        musicxml_path = result.get("output_files", {}).get("musicxml")
        if musicxml_path and Path(musicxml_path).exists():
            html = render_preview_html(Path(musicxml_path))
            st.components.v1.html(html, height=600, scrolling=True)
        else:
            st.info(t("preview_missing_xml", lang))


def _filter_midi_parts(midi_path: Path, parts: list[str]) -> Path:
    if not parts:
        return midi_path
    try:
        from music21 import converter, stream

        score = converter.parse(str(midi_path))
        filtered = stream.Score()
        for part in score.parts:
            part_id = (part.id or "").lower()
            part_name = (part.partName or "").lower()
            if part_id in parts or any(p in part_name for p in parts):
                filtered.append(part)

        if not filtered.parts:
            return midi_path

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as handle:
            filtered.write("midi", fp=handle.name)
            return Path(handle.name)
    except Exception:
        logger.exception("Failed to filter MIDI parts")
        return midi_path


def _map_preview_parts(labels: list[str], lang: str) -> list[str]:
    label_map = {t(key, lang): key for key in PART_KEYS}
    return [label_map[label] for label in labels if label in label_map]


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
