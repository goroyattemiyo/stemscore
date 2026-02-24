from __future__ import annotations

from pathlib import Path

from stemscore.assembler.exporter import export_score


def test_export_score_writes_paths(tmp_path: Path) -> None:
    calls: list[tuple[str, str]] = []

    class FakeScore:
        def write(self, fmt: str, fp: str) -> None:
            calls.append((fmt, fp))

    score = FakeScore()
    output = export_score(score, tmp_path, ["midi", "musicxml", "pdf"])

    assert output["midi"] == tmp_path / "score.mid"
    assert output["musicxml"] == tmp_path / "score.musicxml"
    assert output["pdf"] == tmp_path / "score.pdf"

    assert ("midi", str(tmp_path / "score.mid")) in calls
    assert ("musicxml", str(tmp_path / "score.musicxml")) in calls
    assert ("musicxml.pdf", str(tmp_path / "score.pdf")) in calls
