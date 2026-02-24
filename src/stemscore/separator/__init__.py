from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from stemscore.separator.demucs_wrapper import separate


@dataclass(frozen=True)
class SeparationResult:
    """Output from the separation stage."""

    stems: dict[str, Path]
    model_used: str
    duration_seconds: float


__all__ = ["SeparationResult", "separate"]
