"""
Converts all brief-*.md files into a single styled index.html.
Most recent brief shown by default. Client-side JS handles navigation.
"""

import glob
import os
import webbrowser
import markdown
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Tech Policy Weekly Brief</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg: #faf9f7;
      --surface: #fff;
      --ink: #141414;
      --muted: #6b7280;
      --rule: #e5e2db;
      --accent: #1a3a5c;
      --accent-light: #e8eef5;
      --nav-width: 220px;
      --serif: Georgia, 'Times New Roman', serif;
      --sans: 'Helvetica Neue', Arial, sans-serif;
    }}

    html, body {{
      height: 100%;
      background: var(--bg);
      color: var(--ink);
    }}

    /* ── Layout ── */
    .shell {{
      display: flex;
      min-height: 100vh;
    }}

    /* ── Sidebar ── */
    nav {{
      width: var(--nav-width);
      min-width: var(--nav-width);
      background: var(--accent);
      display: flex;
      flex-direction: column;
      padding: 2rem 0 2rem;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
    }}

    .nav-brand {{
      padding: 0 1.4rem 1.8rem;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      margin-bottom: 1.4rem;
    }}

    .nav-brand .label {{
      font-family: var(--sans);
      font-size: 0.6rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: rgba(255,255,255,0.45);
      margin-bottom: 0.35rem;
    }}

    .nav-brand h1 {{
      font-family: var(--sans);
      font-size: 0.82rem;
      font-weight: 700;
      color: #fff;
      line-height: 1.3;
    }}

    .nav-list {{
      list-style: none;
      flex: 1;
    }}

    .nav-list li {{
      padding: 0;
    }}

    .nav-list button {{
      width: 100%;
      text-align: left;
      background: none;
      border: none;
      cursor: pointer;
      padding: 0.65rem 1.4rem;
      font-family: var(--sans);
      font-size: 0.76rem;
      color: rgba(255,255,255,0.6);
      transition: background 0.15s, color 0.15s;
      line-height: 1.4;
    }}

    .nav-list button:hover {{
      background: rgba(255,255,255,0.06);
      color: #fff;
    }}

    .nav-list button.active {{
      background: rgba(255,255,255,0.12);
      color: #fff;
      font-weight: 600;
      border-left: 3px solid rgba(255,255,255,0.7);
    }}

    .nav-footer {{
      padding: 1.4rem 1.4rem 0;
      border-top: 1px solid rgba(255,255,255,0.1);
      font-family: var(--sans);
      font-size: 0.6rem;
      color: rgba(255,255,255,0.3);
      letter-spacing: 0.05em;
    }}

    /* ── Main content ── */
    .content-area {{
      flex: 1;
      overflow-y: auto;
    }}

    .brief-panel {{
      display: none;
      max-width: 720px;
      margin: 0 auto;
      padding: 3.5rem 3rem 6rem;
    }}

    .brief-panel.active {{
      display: block;
    }}

    /* ── Brief header ── */
    .brief-header {{
      border-bottom: 2px solid var(--ink);
      padding-bottom: 1.2rem;
      margin-bottom: 2.4rem;
    }}

    .brief-header .eyebrow {{
      font-family: var(--sans);
      font-size: 0.62rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 0.5rem;
    }}

    .brief-header h2 {{
      font-family: var(--serif);
      font-size: 1.75rem;
      font-weight: 700;
      line-height: 1.2;
      color: var(--ink);
    }}

    .brief-header .dateline {{
      font-family: var(--sans);
      font-size: 0.72rem;
      color: var(--muted);
      margin-top: 0.5rem;
    }}

    /* ── Brief body ── */
    .brief-body h1 {{
      display: none;
    }}

    .brief-body h2 {{
      font-family: var(--sans);
      font-size: 0.6rem;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--accent);
      margin: 2.8rem 0 1rem;
      padding-bottom: 0.4rem;
      border-bottom: 1px solid var(--rule);
    }}

    .brief-body h3 {{
      font-family: var(--sans);
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--ink);
      margin: 1.4rem 0 0.4rem;
    }}

    .brief-body p {{
      font-family: var(--serif);
      font-size: 1rem;
      line-height: 1.78;
      color: #1e1e1e;
      margin-bottom: 0.9rem;
    }}

    .brief-body em {{
      font-style: italic;
      color: var(--muted);
    }}

    .brief-body ul {{
      list-style: none;
      padding: 0;
      margin: 0 0 0.8rem;
    }}

    .brief-body ul li {{
      font-family: var(--serif);
      font-size: 0.97rem;
      line-height: 1.72;
      padding: 0.5rem 0 0.5rem 1.2rem;
      border-bottom: 1px solid var(--rule);
      position: relative;
      color: #1e1e1e;
    }}

    .brief-body ul li:last-child {{
      border-bottom: none;
    }}

    .brief-body ul li::before {{
      content: '';
      position: absolute;
      left: 0;
      top: 1.1em;
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: var(--accent);
      opacity: 0.5;
    }}

    .brief-body strong {{
      font-weight: 700;
      color: var(--ink);
    }}

    .brief-body a {{
      color: var(--accent);
      text-decoration: underline;
      text-underline-offset: 2px;
    }}

    .brief-body a:hover {{
      opacity: 0.7;
    }}

    .brief-body hr {{
      display: none;
    }}

    /* ── Sources strip ── */
    .sources-strip {{
      font-family: var(--sans);
      font-size: 0.65rem;
      letter-spacing: 0.08em;
      color: var(--muted);
      text-transform: uppercase;
      margin-top: 3rem;
      padding-top: 1rem;
      border-top: 1px solid var(--rule);
    }}

    /* ── Empty state ── */
    .empty {{
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      font-family: var(--sans);
      font-size: 0.85rem;
      color: var(--muted);
    }}
  </style>
</head>
<body>
<div class="shell">

  <nav>
    <div class="nav-brand">
      <div class="label">Harvard · Independent Research</div>
      <h1>Tech Policy<br>Weekly Brief</h1>
    </div>

    <ul class="nav-list" id="navList">
      {nav_items}
    </ul>

    <div class="nav-footer">AI &times; Law &times; Politics</div>
  </nav>

  <div class="content-area" id="contentArea">
    {panels}
  </div>

</div>

<script>
  const buttons = document.querySelectorAll('#navList button');
  const panels  = document.querySelectorAll('.brief-panel');

  function showBrief(id) {{
    panels.forEach(p  => p.classList.remove('active'));
    buttons.forEach(b => b.classList.remove('active'));
    const panel = document.getElementById(id);
    const btn   = document.querySelector(`[data-id="${{id}}"]`);
    if (panel) panel.classList.add('active');
    if (btn)   btn.classList.add('active');
  }}

  // Activate most recent on load
  if (buttons.length) {{
    showBrief(buttons[0].dataset.id);
  }}

  buttons.forEach(btn => {{
    btn.addEventListener('click', () => showBrief(btn.dataset.id));
  }});
</script>
</body>
</html>
"""


def parse_date(filepath: str) -> datetime:
    basename = os.path.basename(filepath)
    date_str = basename.replace("brief-", "").replace(".md", "")
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return datetime.min


def fmt_display(dt: datetime) -> str:
    return dt.strftime("%B %d, %Y")


def fmt_id(dt: datetime) -> str:
    return f"brief-{dt.strftime('%Y-%m-%d')}"


def clean_md(text: str) -> str:
    lines = text.splitlines()
    return "\n".join(
        line for line in lines if not line.startswith("**Track:**")
    )


def build(open_browser: bool = True):
    pattern = os.path.join(PROJECT_DIR, "brief-*.md")
    files = sorted(glob.glob(pattern), key=parse_date, reverse=True)

    if not files:
        raise FileNotFoundError("No brief-*.md files found. Run research-project-weekly-brief.py first.")

    nav_items_html = []
    panels_html = []

    for filepath in files:
        dt = parse_date(filepath)
        panel_id = fmt_id(dt)
        label = fmt_display(dt)

        with open(filepath, encoding="utf-8") as f:
            raw = f.read()

        body_html = markdown.markdown(clean_md(raw), extensions=["extra"])
        body_html = body_html.replace(
            '<a href=', '<a target="_blank" rel="noopener noreferrer" href='
        )

        nav_items_html.append(
            f'<li><button data-id="{panel_id}">{label}</button></li>'
        )

        panels_html.append(f"""
<div class="brief-panel" id="{panel_id}">
  <div class="brief-header">
    <div class="eyebrow">Weekly Brief</div>
    <h2>AI &times; Law &times; Politics</h2>
    <div class="dateline">{label}</div>
  </div>
  <div class="brief-body">
    {body_html}
  </div>
  <div class="sources-strip">
    Sources &mdash; r/law &middot; r/privacy &middot; r/MachineLearning &middot; r/technology
  </div>
</div>""")

    page = HTML_TEMPLATE.format(
        nav_items="\n".join(nav_items_html),
        panels="\n".join(panels_html),
    )

    out_path = os.path.join(PROJECT_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"Built: {out_path}  ({len(files)} brief(s))")
    if open_browser:
        webbrowser.open(f"file://{out_path}")
        print("Opened in browser.")


if __name__ == "__main__":
    import argparse as _argparse
    _p = _argparse.ArgumentParser()
    _p.add_argument("--no-open", action="store_true", help="Skip opening browser (for automation)")
    _args = _p.parse_args()
    build(open_browser=not _args.no_open)
