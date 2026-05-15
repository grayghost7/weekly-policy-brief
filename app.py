"""
Tech Policy Weekly Brief — Streamlit Reader
Displays pre-generated weekly briefs from brief-*.md files in the repo.
"""

import glob
import os
from datetime import datetime

import streamlit as st

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_briefs() -> list[dict]:
    pattern = os.path.join(PROJECT_DIR, "brief-*.md")
    files = glob.glob(pattern)
    briefs = []
    for f in files:
        name = os.path.basename(f)
        try:
            date_str = name.replace("brief-", "").replace(".md", "")
            date = datetime.strptime(date_str, "%Y-%m-%d")
            with open(f) as fh:
                content = fh.read()
            briefs.append({"date": date, "date_str": date_str, "content": content})
        except ValueError:
            continue
    return sorted(briefs, key=lambda x: x["date"], reverse=True)


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Tech Policy Weekly Brief",
    page_icon="⚖️",
    layout="wide",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap');

  .stMarkdown h1 {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    color: #1a3a5c;
  }
  .stMarkdown h2 {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #1a3a5c;
    border-bottom: 1px solid #e5e2db;
    padding-bottom: 0.3rem;
    margin-top: 2rem;
  }
  .stMarkdown a { color: #1a3a5c; }
  .stMarkdown ul li { margin-bottom: 0.4rem; line-height: 1.7; }
  [data-testid="stSidebar"] { background-color: #f8f7f4; }
  [data-testid="stSidebar"] .stRadio label { font-size: 0.85rem; }
  footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load briefs ───────────────────────────────────────────────────────────────

briefs = load_briefs()

if not briefs:
    st.error("No briefs found. Run the generator script to create one.")
    st.stop()

# ── Sidebar navigation ────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <p style="font-size:0.6rem;letter-spacing:0.14em;text-transform:uppercase;
    color:#6b7280;margin-bottom:0.2rem;">Harvard University · Independent Research</p>
    <p style="font-family:'Playfair Display',serif;font-size:1.1rem;
    color:#1a3a5c;margin-bottom:1.2rem;">Tech Policy<br>Weekly Brief</p>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("ARCHIVES")

    date_options = [b["date_str"] for b in briefs]

    def format_date(d: str) -> str:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%B %d, %Y")

    selected_date = st.radio(
        label="Select week",
        options=date_options,
        format_func=format_date,
        index=0,
        label_visibility="collapsed",
    )

# ── Display selected brief ────────────────────────────────────────────────────

brief = next(b for b in briefs if b["date_str"] == selected_date)

st.markdown(brief["content"])
st.divider()

st.download_button(
    label="Download as Markdown",
    data=brief["content"],
    file_name=f"brief-{brief['date_str']}.md",
    mime="text/markdown",
)
