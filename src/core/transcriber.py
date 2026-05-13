"""
core/transcriber.py
====================
Audio transcription using OpenAI Whisper API.
Used for cloud deployment — no local GPU required.
Supports mp3, mp4, wav, m4a, webm, ogg up to 25MB.
"""

import os
from pathlib import Path
from openai import OpenAI

SUPPORTED_FORMATS = {".mp3", ".mp4", ".wav", ".m4a", ".webm", ".ogg"}
MAX_FILE_SIZE_MB  = 25


def transcribe_audio(file_path: str, model_size: str = "base") -> dict:
    """
    Transcribe audio using OpenAI Whisper API.

    Args:
        file_path:   Path to the audio file.
        model_size:  Ignored — kept for API compatibility with local version.

    Returns:
        dict with keys: text, language, duration, segments.

    Raises:
        FileNotFoundError: Audio file does not exist.
        ValueError:        Unsupported format or file too large.
        RuntimeError:      Whisper API failure.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{ext}'. Use: {', '.join(SUPPORTED_FORMATS)}")

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File too large ({size_mb:.1f} MB). Maximum is {MAX_FILE_SIZE_MB} MB.")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment.")

    client = OpenAI(api_key=api_key)

    try:
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )
        return {
            "text":     response.text,
            "language": getattr(response, "language", "en"),
            "duration": getattr(response, "duration", 0.0),
            "segments": getattr(response, "segments", []),
        }
    except Exception as exc:
        raise RuntimeError(f"Transcription failed: {exc}") from exc


def get_device() -> str:
    """Kept for compatibility — not used with API transcription."""
    return "api"