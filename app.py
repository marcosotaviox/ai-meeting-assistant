"""
app.py
=======
MeetingMind AI — Entry Point
Supports audio (Whisper) and documents (PDF, TXT, DOCX, PPTX).

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
from src.core.analyser import analyse_transcript, analyse_document
from src.core.document_reader import extract_text

load_dotenv()


def main() -> None:
    st.set_page_config(
        page_title="MeetingMind AI",
        page_icon="🎙",
        layout="wide",
    )

    inject_custom_css()
    initialise_session_state()

    audio_path, doc_bytes, filename = render_sidebar()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='meetingmind-title'>🎙 Meeting<span>Mind</span> AI</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='meetingmind-subtitle'>AI Meeting & Document Intelligence</div>",
        unsafe_allow_html=True,
    )
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
    if not audio_path and not doc_bytes:
        st.markdown(
            """
            <div style='display:flex;flex-direction:column;align-items:center;
                        justify-content:center;padding:3rem 0;gap:1.5rem'>
                <div style='font-size:3rem'>🎙</div>
                <div style='font-family:Rajdhani,sans-serif;font-size:1.4rem;
                            font-weight:700;color:#E2E8F0;letter-spacing:0.05em;
                            text-align:center'>
                    Drop your file to get started
                </div>
                <div style='color:#475569;font-size:0.85rem;text-align:center;
                            max-width:420px;line-height:1.7'>
                    Upload an <span style='color:#00E5FF'>audio recording</span> to transcribe
                    with Whisper, or a <span style='color:#00E5FF'>document</span> to analyse
                    directly with Claude.
                </div>
                <div style='display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;
                            margin-top:0.5rem'>
                    <span style='border:1px solid rgba(0,229,255,0.2);color:#00E5FF;
                                 padding:4px 14px;border-radius:4px;font-size:0.75rem;
                                 letter-spacing:0.08em'>MP3</span>
                    <span style='border:1px solid rgba(0,229,255,0.2);color:#00E5FF;
                                 padding:4px 14px;border-radius:4px;font-size:0.75rem;
                                 letter-spacing:0.08em'>WAV</span>
                    <span style='border:1px solid rgba(0,229,255,0.2);color:#00E5FF;
                                 padding:4px 14px;border-radius:4px;font-size:0.75rem;
                                 letter-spacing:0.08em'>MP4</span>
                    <span style='border:1px solid rgba(0,229,255,0.2);color:#00E5FF;
                                 padding:4px 14px;border-radius:4px;font-size:0.75rem;
                                 letter-spacing:0.08em'>M4A</span>
                    <span style='border:1px solid rgba(0,229,255,0.2);color:#94A3B8;
                                 padding:4px 14px;border-radius:4px;font-size:0.75rem;
                                 letter-spacing:0.08em'>PDF</span>
                    <span style='border:1px solid rgba(0,229,255,0.2);color:#94A3B8;
                                 padding:4px 14px;border-radius:4px;font-size:0.75rem;
                                 letter-spacing:0.08em'>DOCX</span>
                    <span style='border:1px solid rgba(0,229,255,0.2);color:#94A3B8;
                                 padding:4px 14px;border-radius:4px;font-size:0.75rem;
                                 letter-spacing:0.08em'>TXT</span>
                    <span style='border:1px solid rgba(0,229,255,0.2);color:#94A3B8;
                                 padding:4px 14px;border-radius:4px;font-size:0.75rem;
                                 letter-spacing:0.08em'>PPTX</span>
                </div>
                <div style='color:rgba(0,229,255,0.25);font-size:0.78rem;
                            letter-spacing:0.1em;margin-top:1rem'>
                    ← USE THE SIDEBAR TO UPLOAD
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Process button ────────────────────────────────────────────────────────
    label = "▶  Transcribe & Analyse" if audio_path else "▶  Analyse Document"
    if st.button(label, type="primary", use_container_width=True):
        if audio_path:
            _run_audio_pipeline(audio_path)
        else:
            _run_document_pipeline(doc_bytes, filename)


def _run_audio_pipeline(audio_path: str) -> None:
    """Transcribe audio then analyse."""
    with st.status("Processing your meeting...", expanded=True) as status:

        st.write("🎙 Transcribing audio with Whisper...")
        try:
            result     = transcribe_audio(audio_path)
            transcript = result["text"]
            st.session_state["transcript"] = transcript
            st.write(f"✅ Transcribed — Language: {result['language'].upper()}")
        except Exception as exc:
            st.session_state["error"] = str(exc)
            status.update(label="Transcription failed", state="error")
            st.rerun()
            return

        st.write("🤖 Analysing with Claude...")
        try:
            insights = analyse_transcript(transcript)
            st.session_state["insights"] = insights
            st.write(f"✅ Done — {len(insights.key_points)} key points extracted")
        except Exception as exc:
            st.session_state["error"] = str(exc)
            status.update(label="Analysis failed", state="error")
            st.rerun()
            return

        status.update(label="Done!", state="complete")
    st.rerun()


def _run_document_pipeline(doc_bytes: bytes, filename: str) -> None:
    """Extract text from document then analyse."""
    with st.status("Processing your document...", expanded=True) as status:

        st.write(f"📄 Extracting text from {filename}...")
        try:
            text = extract_text(doc_bytes, filename)
            st.session_state["transcript"] = text
            words = len(text.split())
            st.write(f"✅ Extracted {words:,} words")
        except Exception as exc:
            st.session_state["error"] = str(exc)
            status.update(label="Extraction failed", state="error")
            st.rerun()
            return

        st.write("🤖 Analysing document with Claude...")
        try:
            insights = analyse_document(text)
            st.session_state["insights"] = insights
            st.write(f"✅ Done — {len(insights.key_points)} key points extracted")
        except Exception as exc:
            st.session_state["error"] = str(exc)
            status.update(label="Analysis failed", state="error")
            st.rerun()
            return

        status.update(label="Done!", state="complete")
    st.rerun()


if __name__ == "__main__":
    main()