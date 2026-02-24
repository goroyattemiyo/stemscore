"""Input routing: Suno stems (Route A) vs full mix (Route B)."""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class InputRouter:
    """Detect input type and select processing route."""

    def route(self, input_path: Path) -> str:
        if input_path.is_dir():
            stems_dir = input_path / "stems"
            if stems_dir.exists() and len(list(stems_dir.glob("*.wav"))) >= 3:
                logger.info("Route A: Suno stems detected")
                return "route_a"
        if input_path.is_file() and input_path.suffix in (".mp3", ".wav", ".flac", ".ogg", ".m4a"):
            logger.info("Route B: Full mix")
            return "route_b"
        raise FileNotFoundError(f"No valid input at {input_path}")
