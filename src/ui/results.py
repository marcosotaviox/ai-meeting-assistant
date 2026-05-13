"""
ui/results.py
==============
Renders MeetingInsights with glassmorphic cards.
Adapts layout based on content_type: Meeting vs Class/Webinar/Presentation.
"""

import streamlit as st
from src.core.analyser import MeetingInsights


def render_results(insights: MeetingInsights, transcript: str) -> None:
    """Render insights report with glassmorphic tech aesthetic."""

    # ── Header ────────────────────────────────────────────────────────────────
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown(f"### {insights.title}")
    with col_badge:
        type_colors = {
            "Meeting": "#00E5FF",
            "Class": "#A78BFA",
            "Webinar": "#34D399",
            "Presentation": "#F59E0B",
        }
        color = type_colors.get(insights.content_type, "#00E5FF")
        st.markdown(
            f"<div style='text-align:right;margin-top:0.5rem'>"
            f"<span style='border:1px solid {color};color:{color};"
            f"padding:3px 12px;border-radius:4px;font-size:0.75rem;"
            f"letter-spacing:0.1em;text-transform:uppercase'>"
            f"{insights.content_type}</span></div>",
            unsafe_allow_html=True,
        )

    # ── Metrics ───────────────────────────────────────────────────────────────
    if insights.content_type == "Meeting":
        m1, m2, m3 = st.columns(3)
        m1.metric("Action Items", len(insights.action_items))
        m2.metric("Key Decisions", len(insights.key_decisions))
        m3.metric("Open Questions", len(insights.open_questions))
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Key Points", len(insights.key_points))
        m2.metric("Concepts", len(insights.key_concepts))
        m3.metric("Examples", len(insights.examples))

    st.divider()

    # ── Summary ───────────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>Executive Summary</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='summary-box'>{insights.summary}</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── MEETING layout ────────────────────────────────────────────────────────
    if insights.content_type == "Meeting":
        _render_meeting(insights)
    else:
        _render_learning(insights)

    # ── Export ────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("<div class='section-header'>Export</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊  Generate Slides", type="primary", use_container_width=True):
            with st.spinner("Generating slides..."):
                try:
                    from src.utils.slides_generator import generate_slides
                    pptx_bytes = generate_slides(insights, include_youtube=False)
                    safe_title = insights.title.replace(" ", "_")[:40]
                    st.download_button(
                        label="⬇  Download (.pptx)",
                        data=pptx_bytes,
                        file_name=f"meetingmind_{safe_title}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True,
                    )
                except Exception as exc:
                    st.error(f"Failed: {exc}")

    with col2:
        if st.button("▶  Generate Slides + YouTube", use_container_width=True):
            with st.spinner("Fetching YouTube videos and generating slides..."):
                try:
                    from src.utils.slides_generator import generate_slides
                    pptx_bytes = generate_slides(insights, include_youtube=True)
                    safe_title = insights.title.replace(" ", "_")[:40]
                    st.download_button(
                        label="⬇  Download + YouTube (.pptx)",
                        data=pptx_bytes,
                        file_name=f"meetingmind_{safe_title}_youtube.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True,
                    )
                except Exception as exc:
                    st.error(f"Failed: {exc}")

    st.divider()

    # ── Transcript ────────────────────────────────────────────────────────────
    with st.expander("Full Transcript", expanded=False):
        st.markdown(
            f"<div class='transcript-box'>{transcript}</div>",
            unsafe_allow_html=True,
        )


def _render_meeting(insights: MeetingInsights) -> None:
    """Render Meeting-specific cards."""

    st.markdown("<div class='section-header'>Action Items</div>", unsafe_allow_html=True)
    if insights.action_items:
        for item in insights.action_items:
            st.markdown(
                f"<div class='action-card'>"
                f"<span class='action-owner'>{item.owner}</span>"
                f"<span class='action-deadline'>Due: {item.deadline}</span>"
                f"<div class='action-task'>{item.task}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No action items identified.")

    st.divider()

    col_dec, col_q = st.columns(2)
    with col_dec:
        st.markdown("<div class='section-header'>Key Decisions</div>", unsafe_allow_html=True)
        for d in insights.key_decisions:
            st.markdown(f"<div class='pill-decision'>✓ {d}</div>", unsafe_allow_html=True)

    with col_q:
        st.markdown("<div class='section-header'>Open Questions</div>", unsafe_allow_html=True)
        for q in insights.open_questions:
            st.markdown(f"<div class='pill-question'>? {q}</div>", unsafe_allow_html=True)


def _render_learning(insights: MeetingInsights) -> None:
    """Render Class/Webinar/Presentation cards."""

    st.markdown("<div class='section-header'>Key Points Learned</div>", unsafe_allow_html=True)
    for i, point in enumerate(insights.key_points, 1):
        st.markdown(
            f"<div class='action-card'>"
            f"<span class='action-owner'>Point {i:02d}</span>"
            f"<div class='action-task'>{point}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    col_concepts, col_examples = st.columns(2)

    with col_concepts:
        st.markdown("<div class='section-header'>Key Concepts</div>", unsafe_allow_html=True)
        for concept in insights.key_concepts:
            st.markdown(
                f"<div class='pill-decision'>"
                f"<strong>{concept.concept}</strong><br>"
                f"<span style='font-size:0.80rem;opacity:0.85'>{concept.explanation}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    with col_examples:
        st.markdown("<div class='section-header'>Examples Mentioned</div>", unsafe_allow_html=True)
        for example in insights.examples:
            st.markdown(
                f"<div class='pill-question'>"
                f"<strong>{example.context}</strong><br>"
                f"<span style='font-size:0.80rem;opacity:0.85'>{example.description}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )