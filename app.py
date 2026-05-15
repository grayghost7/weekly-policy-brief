"""
Tech Policy Weekly Brief — Streamlit App
AI × Law × Politics weekly digest powered by Reddit + Claude
"""

import json
import os
import ssl
import urllib.request
from datetime import datetime

import anthropic
import certifi
import streamlit as st

SUBREDDITS = ["law", "privacy", "MachineLearning", "technology"]
POSTS_PER_SUB = 15
HEADERS = {"User-Agent": "weekly-brief-bot/1.0"}
SECRETS_KEY_PATH = os.path.expanduser("~/Desktop/GroundZero/.secrets/anthropic_key.txt")


def load_api_key() -> str:
    key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    if os.path.exists(SECRETS_KEY_PATH):
        with open(SECRETS_KEY_PATH) as f:
            key = f.read().strip()
        if key:
            return key
    raise RuntimeError("No API key found. Add ANTHROPIC_API_KEY to Streamlit secrets.")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_subreddit(sub: str) -> list[dict]:
    url = f"https://www.reddit.com/r/{sub}/top.json?limit={POSTS_PER_SUB}&t=week"
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        data = json.loads(resp.read())
    return [
        {
            "subreddit": sub,
            "title": p["data"]["title"],
            "score": p["data"]["score"],
            "url": p["data"]["url"],
            "selftext": p["data"].get("selftext", "")[:300],
        }
        for p in data["data"]["children"]
    ]


def build_prompt(all_posts: list[dict]) -> str:
    lines = []
    for p in all_posts:
        lines.append(f"[r/{p['subreddit']}] {p['title']} (score: {p['score']}) | URL: {p['url']}")
        if p["selftext"]:
            lines.append(f"  > {p['selftext']}")
    post_block = "\n".join(lines)

    return f"""You are a research analyst for a Harvard student focused on AI, law, politics, and technology policy.

Below are the top Reddit posts from r/law, r/privacy, r/MachineLearning, and r/technology. Each post includes its URL.

Produce a structured weekly brief with ALL of the following sections. Do not stop early — every section must be complete.

LINKING RULE: Every bullet point in sections 1, 2, and 3 must include at least one inline markdown hyperlink to its source, embedded naturally in the text. Use the format [anchor text](URL) where the anchor text is a short descriptive phrase. Do not collect links at the end — embed them inline only.

1. **Top Themes** — 3–5 recurring topics or debates across all posts. One sentence each, with an inline link to the most relevant source post.
2. **Key Discussions by Community** — For each subreddit, 2–3 bullet points summarizing what that community is focused on. Each bullet links to its source post.
3. **AI & Law Intersections** — Any posts that touch on AI regulation, algorithmic accountability, data privacy law, platform liability, or tech policy. Summarize each briefly with an inline link. Include every relevant post — do not cut this section short.
4. **Emerging Questions** — 2–3 open legal or policy questions surfaced by this week's discourse that are not yet settled. Frame each as a research question.
5. **Recommended Follow-Up** — 1–2 specific next steps for a student who wants to go deeper on the most important thread this week.

Be concise but complete. Each section must be fully written out before moving to the next.

---

POSTS:
{post_block}
"""


def generate_brief(all_posts: list[dict]) -> str:
    client = anthropic.Anthropic(api_key=load_api_key())
    prompt = build_prompt(all_posts)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Tech Policy Weekly Brief",
    page_icon="⚖️",
    layout="centered",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap');

  .brief-header { font-family: 'Inter', sans-serif; }
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
  footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="brief-header">
  <p style="font-size:0.65rem;letter-spacing:0.14em;text-transform:uppercase;color:#6b7280;margin-bottom:0.3rem;">
    Harvard University · Independent Research
  </p>
</div>
""", unsafe_allow_html=True)

st.title("Tech Policy Weekly Brief")
st.caption("AI × Law × Politics — sourced from r/law · r/privacy · r/MachineLearning · r/technology")
st.divider()

# ── Generate ──────────────────────────────────────────────────────────────────

if st.button("Generate This Week's Brief", type="primary", use_container_width=True):
    all_posts = []

    with st.status("Fetching posts from Reddit...", expanded=False) as status:
        for sub in SUBREDDITS:
            try:
                posts = fetch_subreddit(sub)
                all_posts.extend(posts)
                status.update(label=f"Fetched r/{sub} ({len(posts)} posts)")
            except Exception as e:
                st.warning(f"r/{sub} failed: {e}")

        if not all_posts:
            st.error("No posts fetched. Try again in a moment.")
            st.stop()

        status.update(label=f"Generating brief from {len(all_posts)} posts with Claude...", state="running")
        brief = generate_brief(all_posts)
        status.update(label="Done.", state="complete")

    st.markdown(brief)
    st.divider()

    date_str = datetime.now().strftime("%Y-%m-%d")
    st.download_button(
        label="Download as Markdown",
        data=f"# Tech Policy Weekly Brief — {date_str}\n\n{brief}",
        file_name=f"brief-{date_str}.md",
        mime="text/markdown",
        use_container_width=True,
    )

else:
    st.info("Click **Generate This Week's Brief** to pull the latest posts and produce a structured research digest.")
