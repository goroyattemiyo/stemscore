from __future__ import annotations

import importlib
import sys
from unittest import mock


def _make_streamlit_mock() -> mock.MagicMock:
    st = mock.MagicMock()
    st.sidebar = mock.MagicMock()
    st.session_state = {}

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
    preview_mock = mock.MagicMock()
    with mock.patch.dict(
        sys.modules,
        {
            "streamlit": st_mock,
            "stemscore.pipeline": pipeline_mock,
            "stemscore.preview": preview_mock,
        },
    ):
        import stemscore.app

        importlib.reload(stemscore.app)


def test_app_main_exists() -> None:
    st_mock = _make_streamlit_mock()
    pipeline_mock = mock.MagicMock()
    preview_mock = mock.MagicMock()
    with mock.patch.dict(
        sys.modules,
        {
            "streamlit": st_mock,
            "stemscore.pipeline": pipeline_mock,
            "stemscore.preview": preview_mock,
        },
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
    preview_mock = mock.MagicMock()
    with mock.patch.dict(
        sys.modules,
        {
            "streamlit": st_mock,
            "stemscore.pipeline": pipeline_mock,
            "stemscore.preview": preview_mock,
        },
    ):
        import stemscore.app

        importlib.reload(stemscore.app)

    st_mock.sidebar.selectbox.assert_any_call("言語 / Language", ["日本語", "English"], index=0)
    st_mock.sidebar.selectbox.assert_any_call("ジャンル", ["pop", "jazz", "edm"], index=0)
    st_mock.sidebar.selectbox.assert_any_call(
        "Sunoクレジットモード",
        ["minimal", "full", "economy"],
        index=0,
    )

    expected_checkboxes = [
        mock.call("リードボーカル", value=True),
        mock.call("バッキングボーカル", value=True),
        mock.call("ベース", value=True),
        mock.call("ドラム", value=True),
        mock.call("バッキングハーモニー", value=True),
        mock.call("コード", value=True),
    ]
    st_mock.sidebar.checkbox.assert_has_calls(expected_checkboxes, any_order=False)
