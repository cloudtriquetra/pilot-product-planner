import streamlit as st


def apply_compact_styles(
    base_font_px: int = 14,
    h1_px: int = 22,
    h2_px: int = 18,
    h3_px: int = 16,
    h4_px: int = 15,
    h5_px: int = 14,
    h6_px: int = 13
):
    """Inject compact CSS to reduce heading sizes and spacing across the app.

    Parameters
    ----------
    base_font_px: int
        Base font size for the document body in pixels.
    h1_px..h6_px: int
        Heading sizes in pixels for h1 through h6.
    """
    st.markdown(
        f"""
        <style>
        html, body {{
            font-size: {base_font_px}px;
        }}

        h1 {{
            font-size: {h1_px}px !important;
            line-height: 1.25 !important;
            margin: 0.25rem 0 0.75rem !important;
        }}
        h2 {{
            font-size: {h2_px}px !important;
            line-height: 1.3 !important;
            margin: 0.25rem 0 0.6rem !important;
        }}
        h3 {{
            font-size: {h3_px}px !important;
            line-height: 1.35 !important;
            margin: 0.2rem 0 0.5rem !important;
        }}
        h4 {{
            font-size: {h4_px}px !important;
            line-height: 1.35 !important;
            margin: 0.2rem 0 0.4rem !important;
        }}
        h5 {{
            font-size: {h5_px}px !important;
            line-height: 1.4 !important;
            margin: 0.15rem 0 0.3rem !important;
        }}
        h6 {{
            font-size: {h6_px}px !important;
            line-height: 1.4 !important;
            margin: 0.15rem 0 0.3rem !important;
        }}

        /* Compact captions and small text */
        .stCaption, .st-emotion-cache-70qvj9 p, footer p {{
            font-size: {max(base_font_px-2, 10)}px !important;
        }}

        /* Reduce padding in containers a bit for tighter layout */
        .stContainer, .st-emotion-cache-1jicfl2, .st-emotion-cache-1r6slb0 {{
            padding-top: 0.25rem !important;
            padding-bottom: 0.25rem !important;
        }}

        /* Compact buttons inside the Actions cards only */
        .actions-grid .stButton > button {{
            padding: 2px 6px !important;
            height: 28px !important;
            min-height: 28px !important;
            font-size: {max(base_font_px-2, 10)}px !important;
            line-height: 1 !important;
            border-radius: 6px !important;
        }}
        .actions-grid .stButton {{
            margin-top: 0.25rem !important;
            margin-bottom: 0 !important;
        }}
        .actions-grid .stMarkdown p {{
            margin: 0 0 0.25rem 0 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


