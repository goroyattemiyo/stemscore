from __future__ import annotations


class StemScoreError(Exception):
    """Base exception for StemScore."""


class AudioLoadError(StemScoreError):
    """Raised when audio loading or saving fails."""


class AnalysisError(StemScoreError):
    """Raised when analysis fails."""


class SeparationError(StemScoreError):
    """Raised when separation fails."""


class TranscriptionError(StemScoreError):
    """Raised when transcription fails."""


class AssemblyError(StemScoreError):
    """Raised when assembly fails."""
