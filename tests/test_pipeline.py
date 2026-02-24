from __future__ import annotations

from pathlib import Path

from stemscore import analyzer, assembler, pipeline, transcriber


def test_run_pipeline_route_b(monkeypatch, tmp_path: Path) -> None:
    input_path = tmp_path / "mix.wav"
    input_path.touch()

    analysis_result = analyzer.AnalysisResult(tempo=120.0, key="C", time_signature=4)
    monkeypatch.setattr(pipeline.router.InputRouter, "route", lambda self, path: "route_b")
    monkeypatch.setattr(pipeline.analyzer, "analyze", lambda path: analysis_result)
    monkeypatch.setattr(
        pipeline.separator,
        "separate",
        lambda path, output_dir, model: {"vocals": tmp_path / "vocals.wav"},
    )
    monkeypatch.setattr(
        pipeline.transcriber,
        "transcribe_part",
        lambda path, part, config: transcriber.TranscriptionResult(
            notes=[{"start": 0.0, "end": 1.0, "pitch": 60}],
            part_name=part,
            method="mock",
        ),
    )
    monkeypatch.setattr(
        pipeline.assembler,
        "assemble",
        lambda parts, tempo, key, time_signature, output_dir, formats, level, swing: assembler.AssemblyResult(
            output_files={"midi": tmp_path / "score.mid"},
            num_parts=len(parts),
            total_notes=1,
        ),
    )

    result = pipeline.run_pipeline(
        input_path=input_path,
        output_dir=tmp_path,
        parts=["lead_vocal"],
        genre="pop",
        formats=["midi"],
    )

    assert result["route"] == "route_b"
    assert result["tempo"] == 120.0
    assert result["output_files"]["midi"] == tmp_path / "score.mid"


def test_run_pipeline_route_a(monkeypatch, tmp_path: Path) -> None:
    analysis_result = analyzer.AnalysisResult(tempo=98.0, key="G", time_signature=3)
    monkeypatch.setattr(pipeline.router.InputRouter, "route", lambda self, path: "route_a")
    monkeypatch.setattr(pipeline.analyzer, "analyze", lambda path: analysis_result)
    monkeypatch.setattr(
        pipeline,
        "import_suno",
        lambda input_dir: {"lead_vocal": tmp_path / "lead.wav"},
    )
    monkeypatch.setattr(
        pipeline.transcriber,
        "transcribe_part",
        lambda path, part, config: transcriber.TranscriptionResult(
            notes=[{"start": 0.0, "end": 1.0, "pitch": 60}],
            part_name=part,
            method="mock",
        ),
    )
    monkeypatch.setattr(
        pipeline.assembler,
        "assemble",
        lambda parts, tempo, key, time_signature, output_dir, formats, level, swing: assembler.AssemblyResult(
            output_files={"midi": tmp_path / "score.mid"},
            num_parts=len(parts),
            total_notes=1,
        ),
    )

    result = pipeline.run_pipeline(
        input_path=tmp_path,
        output_dir=tmp_path,
        parts=["lead_vocal"],
        genre="pop",
        formats=["midi"],
    )

    assert result["route"] == "route_a"
    assert result["tempo"] == 98.0
    assert result["output_files"]["midi"] == tmp_path / "score.mid"
