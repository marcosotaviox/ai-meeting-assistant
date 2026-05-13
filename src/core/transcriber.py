"""
core/transcriber.py
====================
Handles audio transcription using local Whisper model.
Runs on GPU if available, falls back to CPU automatically.
"""

import whisper
import torch


def get_device() -> str:
    """Return 'cuda' if GPU is available, else 'cpu'."""
    return "cuda" if torch.cuda.is_available() else "cpu"


def transcribe_audio(file_path: str, model_size: str = "base") -> dict:
    """
    Transcribe an audio file using local Whisper model.

    Args:
        file_path:  Path to the audio file.
        model_size: Whisper model size — tiny, base, small, medium, large.
                    Larger = more accurate, slower.

    Returns:
        dict with keys:
            text     — full transcript string
            language — detected language code (e.g. 'en', 'pt')
            segments — list of timed segments

    Raises:
        FileNotFoundError: Audio file does not exist.
        RuntimeError:      Whisper transcription failure.
    """
    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    device = get_device()

    try:
        model = whisper.load_model(model_size, device=device)
        result = model.transcribe(file_path)
        return {
            "text": result["text"].strip(),
            "language": result["language"],
            "segments": result["segments"],
        }
    except Exception as exc:
        raise RuntimeError(f"Transcription failed: {exc}") from exc