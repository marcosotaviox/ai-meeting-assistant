"""
utils/session.py
=================
Centralised Streamlit session state initialisation.
All keys typed and defaulted here — no KeyError surprises.
"""

import streamlit as st


def initialise_session_state() -> None:
    """Initialise all session state keys with safe defaults."""
    defaults = {
        "transcript": None,      # str | None
        "insights": None,        # MeetingInsights | None
        "audio_path": None,      # str | None
        "processing": False,     # bool
        "error": None,           # str | None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_state() -> None:
    """Clear all results, keeping the app clean for a new meeting."""
    st.session_state["transcript"] = None
    st.session_state["insights"] = None
    st.session_state["audio_path"] = None
    st.session_state["processing"] = False
    st.session_state["error"] = None