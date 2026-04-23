"""
Tech Policy Weekly Brief Generator
Fetches top posts from policy/law/tech subreddits and produces a structured brief via Claude API.
"""

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


def fetch_subreddit(sub: str) -> list[dict]:
    url = f"https://www.reddit.com/r/{sub}/top.json?limit={POSTS_PER_SUB}&t=week"
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
        lines.append(f"[r/{p['subreddit']}] {p['title']} (score: {p['score']})")
        if p["selftext"]:
            lines.append(f"  > {p['selftext']}")
    post_block = "\n".join(lines)

    return f"""You are a research analyst for a Harvard student focused on AI, law, politics, and technology policy.

Below are the top Reddit posts from r/law, r/privacy, r/MachineLearning, and r/technology from this past week.

Your job is to produce a structured weekly brief with the following sections:

1. **Top Themes** — 3–5 recurring topics or debates across all posts. One sentence each.
2. **Key Discussions by Community** — For each subreddit, 2–3 bullet points summarizing what that community is focused on this week.
3. **AI & Law Intersections** — Any posts that touch on AI regulation, algorithmic accountability, data privacy law, platform liability, or tech policy. Summarize each briefly.
4. **Emerging Questions** — 2–3 open legal or policy questions surfaced by this week's discourse that are not yet settled. Frame each as a research question.
5. **Recommended Follow-Up** — 1–2 specific next steps for a student who wants to go deeper on the most important thread this week.

Be concise. Each section should be scannable. Do not editorialize — stay close to what the posts actually show.

---

POSTS:
{post_block}
"""


def generate_brief(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=load_api_key())
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def save_brief(brief: str) -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"brief-{date}.md"
    filepath = f"/Users/grayj/Desktop/GroundZero/project1-weekly-brief/{filename}"
    header = f"# Tech Policy Weekly Brief — {date}\n**Track:** Independent Research\n\n---\n\n"
    with open(filepath, "w") as f:
        f.write(header + brief)
    return filepath


def main():
    print("Fetching posts...")
    all_posts = []
    for sub in SUBREDDITS:
        try:
            posts = fetch_subreddit(sub)
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

    filepath = save_brief(brief)
    print(f"\nBrief saved to: {filepath}")
    print("\n--- PREVIEW ---")
    print(brief[:800])
    print("...")


if __name__ == "__main__":
    main()
