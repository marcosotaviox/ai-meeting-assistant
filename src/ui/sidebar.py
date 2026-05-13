"""
ui/sidebar.py
==============
Renders the sidebar: file uploader, process trigger, reset button.
API key is loaded from .env — not exposed in the UI.
"""

import os
import tempfile
import streamlit as st
from src.utils.session import reset_state


def render_sidebar() -> str | None:
    """
    Render sidebar controls.

    Returns:
        audio_path: Path to temp audio file, or None if not uploaded.
    """
    with st.sidebar:
        st.markdown("## 🎙 MeetingMind AI")
        st.caption("AI Meeting Intelligence")
        st.divider()

        # File uploader
        uploaded = st.file_uploader(
            "Upload Audio File",
            type=["mp3", "mp4", "wav", "m4a", "webm"],
            help="Transcribed locally with Whisper — free.",
        )

        audio_path = None

        if uploaded:
            size_mb = len(uploaded.getvalue()) / (1024 * 1024)
            st.caption(f"📎 {uploaded.name}  ·  {size_mb:.1f} MB")

            suffix = os.path.splitext(uploaded.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded.getvalue())
                audio_path = tmp.name

        st.divider()

        if st.button("↺ New Meeting", use_container_width=True):
            reset_state()
            st.rerun()

    return audio_path