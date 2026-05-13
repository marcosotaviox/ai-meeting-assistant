"""
ui/sidebar.py
==============
Renders the sidebar with expandable tool information sections.
Upload section at the top for quick access.
API key loaded from .env — not exposed in the UI.
"""

import os
import tempfile
import streamlit as st
from src.utils.session import reset_state

AUDIO_FORMATS = ["mp3", "mp4", "wav", "m4a", "webm", "ogg"]
DOC_FORMATS   = ["pdf", "txt", "docx", "pptx"]
ALL_FORMATS   = AUDIO_FORMATS + DOC_FORMATS


def render_sidebar() -> tuple[str | None, bytes | None, str | None]:
    with st.sidebar:

        # ── Brand ─────────────────────────────────────────────────────────────
        st.markdown(
            "<div style='font-family:Rajdhani,sans-serif;font-size:1.2rem;"
            "color:#00E5FF;font-weight:700;letter-spacing:0.08em;margin-bottom:2px'>"
            "▸ MEETINGMIND AI</div>"
            "<div style='font-size:0.72rem;color:#334155;margin-bottom:0.5rem'>"
            "AI Meeting & Document Intelligence</div>",
            unsafe_allow_html=True,
        )
        st.divider()

        # ── Upload ─────────────────────────────────────────────────────────────
        st.markdown(
            "<div style='font-size:0.7rem;color:#00E5FF;letter-spacing:0.12em;"
            "font-weight:600;margin-bottom:0.4rem'>UPLOAD</div>",
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Audio or Document",
            type=ALL_FORMATS,
            help="Audio: mp3, mp4, wav, m4a — transcribed with Whisper\nDocs: pdf, txt, docx, pptx — analysed directly",
            label_visibility="collapsed",
        )

        audio_path = None
        doc_bytes  = None
        filename   = None

        if uploaded:
            ext     = os.path.splitext(uploaded.name)[1].lower().strip(".")
            size_mb = len(uploaded.getvalue()) / (1024 * 1024)
            filename = uploaded.name

            if ext in AUDIO_FORMATS:
                st.caption(f"🎙 {uploaded.name}  ·  {size_mb:.1f} MB  ·  Audio")
                suffix = f".{ext}"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded.getvalue())
                    audio_path = tmp.name
            elif ext in DOC_FORMATS:
                st.caption(f"📄 {uploaded.name}  ·  {size_mb:.1f} MB  ·  Document")
                doc_bytes = uploaded.getvalue()

            st.session_state["audio_filename"] = filename

        st.divider()

        # ── Input Tools ───────────────────────────────────────────────────────
        st.markdown(
            "<div style='font-size:0.7rem;color:#00E5FF;letter-spacing:0.12em;"
            "font-weight:600;margin-bottom:0.4rem'>INPUT TOOLS</div>",
            unsafe_allow_html=True,
        )

        with st.expander("🎙  Audio Transcription"):
            st.markdown("""
**What it does**
Converts audio recordings into text using OpenAI Whisper running locally on your GPU.

**Supported formats**
MP3 · MP4 · WAV · M4A · WEBM · OGG

**Model**
`whisper-base` — auto-detects language, supports 99 languages

**Performance**
Runs on your RTX 3070 — approx. 5× faster than CPU

**Cost**
Free — runs entirely on your machine, no API calls
            """)

        with st.expander("📄  Document Analysis"):
            st.markdown("""
**What it does**
Extracts and analyses text from documents — articles, reports, study materials, slide decks.

**Supported formats**
PDF · TXT · DOCX · PPTX

**How it works**
Text is extracted locally, then sent to Claude for structured analysis

**Best for**
Research papers, business reports, lecture slides, study notes

**Cost**
Claude API — approx. $0.01–0.03 per document depending on length
            """)

        st.divider()

        # ── Analysis Tools ────────────────────────────────────────────────────
        st.markdown(
            "<div style='font-size:0.7rem;color:#00E5FF;letter-spacing:0.12em;"
            "font-weight:600;margin-bottom:0.4rem'>ANALYSIS TOOLS</div>",
            unsafe_allow_html=True,
        )

        with st.expander("🤖  Claude — Content Analyser"):
            st.markdown("""
**What it does**
Analyses transcripts and documents to extract structured insights: summaries, key points, concepts, examples, action items.

**Model**
`claude-sonnet-4-5` via Anthropic API

**Auto-detects content type**
Meeting → action items, decisions, open questions
Class / Webinar → key points, concepts, examples
Document / Report → insights, key arguments, examples

**Output language**
Always matches the input language automatically

**Cost**
~$0.01–0.03 per analysis
            """)

        with st.expander("🎨  Slide Planner — AI Designer"):
            st.markdown("""
**What it does**
Uses Claude to plan a professional presentation before rendering — decides layouts, bullet structure, image queries, and speaker notes.

**Design rules applied**
- 10/20/30 rule — max 10 slides, 20 min, 30pt font
- 6×6 rule — max 6 bullets, max 6 words per bullet
- One key message per slide
- Visual storytelling over text walls

**Layouts available**
Cover · Summary · Bullets · Cards · Image Left · Action Items · YouTube

**Model**
`claude-sonnet-4-5`
            """)

        with st.expander("▶  YouTube Integration"):
            st.markdown("""
**What it does**
Searches YouTube for relevant educational videos based on the key concepts extracted from your content.

**How it works**
1. Claude extracts key concepts
2. YouTube Data API v3 searches for related videos
3. Thumbnails + clickable links added to a dedicated slide

**Available on**
Class · Webinar · Presentation content types only
Meetings never include YouTube links

**API**
YouTube Data API v3 — free tier (10,000 units/day)
            """)

        with st.expander("🖼  Unsplash — Image Search"):
            st.markdown("""
**What it does**
Fetches high-quality professional photos to illustrate slides when Claude decides an image adds visual value.

**How it works**
Claude generates a search query per slide → Unsplash returns a relevant photo → added to the slide automatically

**Frequency**
Only ~40% of slides get images — when it genuinely adds context

**Cost**
Free — Unsplash free tier (50 requests/hour)
            """)

        st.divider()

        if st.button("↺  New Session", use_container_width=True):
            reset_state()
            st.rerun()

    return audio_path, doc_bytes, filename