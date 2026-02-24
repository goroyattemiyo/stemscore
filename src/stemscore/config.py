"""Genre presets and configuration."""
from pydantic import BaseModel


class AnalysisConfig(BaseModel):
    tempo_octave_correction: bool = True
    key_diatonic_bias: float = 0.8
    time_sig_candidates: list[int] = [4, 3]


class SeparationConfig(BaseModel):
    stage1_model: str = "htdemucs_ft"
    stage2_vocal: bool = True


class TranscriptionConfig(BaseModel):
    vocal_min_note_ms: int = 80
    melisma_mode: str = "grace_note"
    drum_classes: int = 9
    chord_model: str = "autochord"


class AssemblyConfig(BaseModel):
    quantize_level: int = 16
    swing_detection: bool = False
    triplet: bool = False


class GenrePreset(BaseModel):
    analysis: AnalysisConfig = AnalysisConfig()
    separation: SeparationConfig = SeparationConfig()
    transcription: TranscriptionConfig = TranscriptionConfig()
    assembly: AssemblyConfig = AssemblyConfig()


GENRE_PRESETS: dict[str, GenrePreset] = {
    "pop": GenrePreset(),
    "jazz": GenrePreset(
        analysis=AnalysisConfig(key_diatonic_bias=0.3, time_sig_candidates=[4, 3, 5, 7]),
        transcription=TranscriptionConfig(vocal_min_note_ms=60, melisma_mode="individual_notes", drum_classes=13, chord_model="btc"),
        assembly=AssemblyConfig(quantize_level=8, swing_detection=True, triplet=True),
    ),
    "edm": GenrePreset(
        analysis=AnalysisConfig(key_diatonic_bias=0.7),
        transcription=TranscriptionConfig(vocal_min_note_ms=60),
    ),
}
