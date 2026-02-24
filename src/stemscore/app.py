from __future__ import annotations

from pathlib import Path
import logging
import subprocess
import tempfile

import streamlit as st

from stemscore import pipeline
from stemscore.i18n import t

logger = logging.getLogger(__name__)


def render_app() -> None:
    """Render the Streamlit UI for StemScore."""
    st.set_page_config(title="StemScore", page_icon="🎵", layout="wide")

    if "lang_choice" not in st.session_state:
        st.session_state["lang_choice"] = "日本語"

    st.sidebar.header(t("settings_label", "ja"))
    lang_choice = st.sidebar.selectbox("言語 / Language", ["日本語", "English"], index=0)
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
    for part in [
        "lead_vocal",
        "backing_vocal",
        "bass",
        "drums",
        "backing_harmony",
        "chords",
    ]:
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
        except Exception as exc:
            logger.exception("Pipeline failed")
            st.error(f"{t('error_message', lang)}: {exc}")


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
