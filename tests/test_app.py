from __future__ import annotations

import importlib
import sys
from unittest import mock


def _make_streamlit_mock() -> mock.MagicMock:
    st = mock.MagicMock()
    st.sidebar = mock.MagicMock()

    def _columns(count: int):
        return [mock.MagicMock() for _ in range(count)]

    st.columns.side_effect = _columns
    st.button.return_value = False
    st.file_uploader.return_value = None
    st.text_input.return_value = ""
    return st


def test_app_imports_without_error() -> None:
    st_mock = _make_streamlit_mock()
    pipeline_mock = mock.MagicMock()
    with mock.patch.dict(
        sys.modules,
        {"streamlit": st_mock, "stemscore.pipeline": pipeline_mock},
    ):
        import stemscore.app

        importlib.reload(stemscore.app)


def test_app_main_exists() -> None:
    st_mock = _make_streamlit_mock()
    pipeline_mock = mock.MagicMock()
    with mock.patch.dict(
        sys.modules,
        {"streamlit": st_mock, "stemscore.pipeline": pipeline_mock},
    ):
        import stemscore.app

        importlib.reload(stemscore.app)
        assert hasattr(stemscore.app, "main")


def test_sidebar_config_values() -> None:
    st_mock = _make_streamlit_mock()
    st_mock.sidebar.selectbox.side_effect = lambda label, options, index=0: options[index]
    st_mock.sidebar.multiselect.return_value = ["midi", "musicxml"]
    st_mock.sidebar.checkbox.return_value = True

    pipeline_mock = mock.MagicMock()
    with mock.patch.dict(
        sys.modules,
        {"streamlit": st_mock, "stemscore.pipeline": pipeline_mock},
    ):
        import stemscore.app

        importlib.reload(stemscore.app)

    st_mock.sidebar.selectbox.assert_any_call("Genre", ["pop", "jazz", "edm"], index=0)
    st_mock.sidebar.selectbox.assert_any_call(
        "Suno Credit Mode",
        ["minimal", "full", "economy"],
        index=0,
    )

    expected_checkboxes = [
        mock.call("lead_vocal", value=True),
        mock.call("backing_vocal", value=True),
        mock.call("bass", value=True),
        mock.call("drums", value=True),
        mock.call("backing_harmony", value=True),
        mock.call("chords", value=True),
    ]
    st_mock.sidebar.checkbox.assert_has_calls(expected_checkboxes, any_order=False)
