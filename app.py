"""
app.py
=======
MeetingMind AI — Entry Point
Transcribes meeting audio with Whisper, extracts insights with Claude.

Usage:
    streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

from src.utils.session import initialise_session_state
from src.ui.styles import inject_custom_css
from src.ui.sidebar import render_sidebar
from src.ui.results import render_results
from src.core.transcriber import transcribe_audio
from src.core.analyser import analyse_transcript

load_dotenv()


def main() -> None:
    st.set_page_config(
        page_title="MeetingMind AI",
        page_icon="🎙",
        layout="wide",
    )

    inject_custom_css()
    initialise_session_state()

    audio_path = render_sidebar()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("<div class='meetingmind-title'>🎙 Meeting<span>Mind</span> AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='meetingmind-subtitle'>AI Meeting Intelligence</div>", unsafe_allow_html=True)
    st.divider()

    # ── Error banner ──────────────────────────────────────────────────────────
    if st.session_state.get("error"):
        st.error(st.session_state["error"])
        st.session_state["error"] = None

    # ── Show results if already processed ────────────────────────────────────
    if st.session_state["insights"] and st.session_state["transcript"]:
        render_results(st.session_state["insights"], st.session_state["transcript"])
        return

    # ── Upload prompt ─────────────────────────────────────────────────────────
    if not audio_path:
        st.markdown(
            "<div style='text-align:center;padding:3rem 0;"
            "color:rgba(0,229,255,0.3);font-size:0.88rem;letter-spacing:0.1em'>"
            "← UPLOAD AN AUDIO FILE IN THE SIDEBAR TO BEGIN"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Process button ────────────────────────────────────────────────────────
    if st.button("▶  TRANSCRIBE & ANALYSE", type="primary", use_container_width=True):
        _run_pipeline(audio_path)


def _run_pipeline(audio_path: str) -> None:
    """Run transcription → analysis pipeline with progress feedback."""

    with st.status("Processing your meeting...", expanded=True) as status:

        # Step 1 — Transcription
        st.write("🎙 Transcribing audio with Whisper...")
        try:
            result = transcribe_audio(audio_path)
            transcript = result["text"]
            st.session_state["transcript"] = transcript
            st.write(f"✅ Transcribed — Language: {result['language'].upper()}")
        except Exception as exc:
            st.session_state["error"] = str(exc)
            status.update(label="Transcription failed", state="error")
            st.rerun()
            return

        # Step 2 — Analysis
        st.write("🤖 Analysing with Claude...")
        try:
            insights = analyse_transcript(transcript)
            st.session_state["insights"] = insights
            st.write(f"✅ Found {len(insights.action_items)} action items")
        except Exception as exc:
            st.session_state["error"] = str(exc)
            status.update(label="Analysis failed", state="error")
            st.rerun()
            return

        status.update(label="Done!", state="complete")

    st.rerun()


if __name__ == "__main__":
    main()