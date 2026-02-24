from __future__ import annotations

from pathlib import Path

import pytest

from stemscore.suno.importer import import_suno


def test_import_suno_maps_filenames(tmp_path: Path) -> None:
    stems_dir = tmp_path / "stems"
    stems_dir.mkdir()
    (stems_dir / "vocals.wav").touch()
    (stems_dir / "backing_vox.wav").touch()
    (stems_dir / "bass.wav").touch()
    (stems_dir / "drums.wav").touch()
    (stems_dir / "keys.wav").touch()

    stems = import_suno(tmp_path)

    assert stems["lead_vocal"] == stems_dir / "vocals.wav"
    assert stems["backing_vocal"] == stems_dir / "backing_vox.wav"
    assert stems["bass"] == stems_dir / "bass.wav"
    assert stems["drums"] == stems_dir / "drums.wav"
    assert stems["backing_harmony"] == stems_dir / "keys.wav"


def test_import_suno_missing_stems_dir(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        import_suno(tmp_path)
