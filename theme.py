"""
theme.py — dark/light theming + Times New Roman font for Task AI
"""

import streamlit as st  # type: ignore[import-not-found]


DARK = {
    "bg": "#1B2430",          # deep charcoal/navy (not pure black)
    "card_bg": "#4C76FF",
    "text": "#EDEDED",
    "accent": "#7C9CFF",      # brighter accent for contrast on dark bg
    "accent_soft": "#334066",
    "sidebar_bg": "#689EE9",
}


def get_palette() -> dict:
    return DARK


def apply_theme() -> dict:
    """Inject CSS for the app's permanent dark theme and return the palette dict."""
    p = get_palette()

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tinos&display=swap');

        html, body, [class*="css"]  {{
            font-family: 'Times New Roman', Times, serif !important;
        }}

        .stApp {{
            background-color: {p['bg']};
            color: {p['text']};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {p['sidebar_bg']};
        }}

        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: {p['text']};
        }}

        div.stButton > button {{
            background-color: {p['accent']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5em 1.2em;
            font-family: 'Times New Roman', Times, serif;
        }}

        div.stButton > button:hover {{
            background-color: {p['accent_soft']};
            color: {p['text']};
        }}

        .task-card {{
            background-color: {p['card_bg']};
            border-radius: 10px;
            padding: 1em;
            margin-bottom: 0.6em;
            border-left: 6px solid {p['accent']};
        }}

        .badge-card {{
            background-color: {p['card_bg']};
            border-radius: 10px;
            padding: 1em;
            text-align: center;
            margin-bottom: 0.8em;
        }}

        .badge-locked {{
            opacity: 0.35;
            filter: grayscale(100%);
        }}

        .avatar-corner {{
            position: fixed;
            top: 70px;
            right: 30px;
            font-size: 2.5em;
            z-index: 999;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    return p