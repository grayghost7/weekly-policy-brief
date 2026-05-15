"""
Tech Policy Weekly Brief Generator
Fetches top posts from policy/law/tech subreddits and produces a structured brief via Claude API.

Usage:
  python3 research-project-weekly-brief.py
  python3 research-project-weekly-brief.py --date 2026-04-16 --timeframe month
"""

import argparse
import json
import os
import ssl
import urllib.request
import anthropic
import certifi
from datetime import datetime

SUBREDDITS = ["law", "privacy", "MachineLearning", "technology"]
POSTS_PER_SUB = 15
HEADERS = {"User-Agent": "weekly-brief-bot/1.0"}
SECRETS_KEY_PATH = os.path.expanduser(
    "~/Desktop/GroundZero/.secrets/anthropic_key.txt"
)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_api_key() -> str:
    if os.path.exists(SECRETS_KEY_PATH):
        with open(SECRETS_KEY_PATH) as f:
            key = f.read().strip()
        if key:
            return key
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError(
            "No API key found. Add it to .secrets/anthropic_key.txt or set ANTHROPIC_API_KEY."
        )
    return key


def fetch_subreddit(sub: str, timeframe: str = "week") -> list[dict]:
    url = f"https://www.reddit.com/r/{sub}/top.json?limit={POSTS_PER_SUB}&t={timeframe}"
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        data = json.loads(resp.read())
    posts = data["data"]["children"]
    return [
        {
            "subreddit": sub,
            "title": p["data"]["title"],
            "score": p["data"]["score"],
            "url": p["data"]["url"],
            "selftext": p["data"].get("selftext", "")[:300],
        }
        for p in posts
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

LINKING RULE: Every bullet point in sections 1, 2, and 3 must include at least one inline markdown hyperlink to its source, embedded naturally in the text. Use the format [anchor text](URL) where the anchor text is a short descriptive phrase, not the full post title. Do not collect links at the end — embed them inline only.

1. **Top Themes** — 3–5 recurring topics or debates across all posts. One sentence each, with an inline link to the most relevant source post.
2. **Key Discussions by Community** — For each subreddit, 2–3 bullet points summarizing what that community is focused on. Each bullet links to its source post.
3. **AI & Law Intersections** — Any posts that touch on AI regulation, algorithmic accountability, data privacy law, platform liability, or tech policy. Summarize each briefly with an inline link. Include every relevant post — do not cut this section short.
4. **Emerging Questions** — 2–3 open legal or policy questions surfaced by this week's discourse that are not yet settled. Frame each as a research question. No links required.
5. **Recommended Follow-Up** — 1–2 specific next steps for a student who wants to go deeper on the most important thread this week. Link to the relevant source where applicable.

Be concise but complete. Each section must be fully written out before moving to the next.

---

POSTS:
{post_block}
"""


def generate_brief(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=load_api_key())
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def save_brief(brief: str, date_str: str, all_posts: list[dict]) -> str:
    filename = f"brief-{date_str}.md"
    filepath = os.path.join(PROJECT_DIR, filename)
    header = f"# Tech Policy Weekly Brief — {date_str}\n**Track:** Independent Research\n\n---\n\n"
    with open(filepath, "w") as f:
        f.write(header + brief)
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Generate a Tech Policy Weekly Brief")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Output date label for the brief filename (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--timeframe",
        default="week",
        choices=["day", "week", "month", "year", "all"],
        help="Reddit top posts timeframe (default: week).",
    )
    args = parser.parse_args()

    print(f"Fetching top posts (timeframe: {args.timeframe})...")
    all_posts = []
    for sub in SUBREDDITS:
        try:
            posts = fetch_subreddit(sub, args.timeframe)
            all_posts.extend(posts)
            print(f"  r/{sub}: {len(posts)} posts")
        except Exception as e:
            print(f"  r/{sub}: failed ({e})")

    if not all_posts:
        print("No posts fetched. Exiting.")
        return

    print(f"\nGenerating brief from {len(all_posts)} posts...")
    prompt = build_prompt(all_posts)
    brief = generate_brief(prompt)

    filepath = save_brief(brief, args.date, all_posts)
    print(f"\nBrief saved to: {filepath}")
    print("\n--- PREVIEW ---")
    print(brief[:800])
    print("...")


if __name__ == "__main__":
    main()
