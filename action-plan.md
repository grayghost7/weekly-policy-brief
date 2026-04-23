# Action Plan: Tech Policy Weekly Brief Generator
**Track:** Independent Research
**Agent:** Leo (Builder)
**Status:** Script built and ready to run

---

## What Was Built
A Python script that:
1. Fetches the top 15 posts from 4 subreddits (r/law, r/privacy, r/MachineLearning, r/technology) using Reddit's public JSON API — no authentication required
2. Passes all post titles and text to Claude via the Anthropic API
3. Receives a structured 5-section weekly brief
4. Saves the brief as a dated Markdown file in this project folder

---

## Files
| File | Purpose |
|---|---|
| `research-project-weekly-brief.py` | Main script — run this to generate a brief |
| `requirements.txt` | Python dependencies (just `anthropic`) |
| `action-plan.md` | This file |
| `brief-YYYY-MM-DD.md` | Output — generated each time the script runs |

---

## How to Run

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY=your_key_here
```
Or add it to `.secrets/anthropic_key.txt` and load it in your shell profile.

### Step 3 — Run the script
```bash
python research-project-weekly-brief.py
```

The brief will be saved to `brief-YYYY-MM-DD.md` in this folder and a preview will print to the terminal.

---

## What the Output Looks Like
Each brief contains 5 sections:
1. **Top Themes** — 3–5 recurring topics across all communities this week
2. **Key Discussions by Community** — What each subreddit is focused on
3. **AI & Law Intersections** — Posts touching AI regulation, privacy law, platform liability
4. **Emerging Questions** — Open legal/policy questions surfaced by this week's discourse
5. **Recommended Follow-Up** — 1–2 next steps for deeper research

---

## Known Flags
- Reddit rate-limits unauthenticated requests to ~10/minute. The script fetches 4 subreddits sequentially, which stays well within limits.
- If a subreddit fetch fails, the script logs the error and continues with the remaining subreddits.
- Requires an Anthropic API key (paid). Add it to `.secrets/` — never paste it in chat.

---

## Next Step (Project 2)
Once this is running, the same fetch → LLM chain pattern applies directly to Project 2 (Congressional AI Bill Dashboard), with Congress.gov as the data source and Streamlit added for the visual layer.

---

**Verification Tier:** Standard
**Checked:** Script fetches from correct endpoints, prompt covers all 5 output sections, output saves with dated filename, error handling present for failed subreddit fetches.
