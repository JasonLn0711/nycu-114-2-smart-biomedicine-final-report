#!/usr/bin/env python3
"""Build a browser-friendly recording HTML from the Markdown report.

The output is a local recording surface, not the canonical report source.
It copies image assets into the ignored export workspace and preserves Mermaid
blocks for browser-side rendering.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
SOURCE = PROJECT / "markdown-report-v1.md"
DEFAULT_EXPORT_ROOT = ROOT / "exports/smart-biomedicine-gpt-sovits"


def inline_format(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def parse_table(lines: list[str], start: int) -> tuple[str, int]:
    table_lines = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
        table_lines.append(lines[i].strip())
        i += 1
    rows = [[cell.strip() for cell in row.strip("|").split("|")] for row in table_lines]
    if len(rows) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in rows[1]):
        header = rows[0]
        body = rows[2:]
    else:
        header = []
        body = rows
    out = ["<table>"]
    if header:
        out.append("<thead><tr>")
        out.extend(f"<th>{inline_format(cell)}</th>" for cell in header)
        out.append("</tr></thead>")
    out.append("<tbody>")
    for row in body:
        out.append("<tr>")
        out.extend(f"<td>{inline_format(cell)}</td>" for cell in row)
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out), i


def copy_image(src: str, source_file: Path, asset_out: Path) -> str:
    source_path = (source_file.parent / src).resolve()
    if not source_path.exists():
        return src
    asset_out.mkdir(parents=True, exist_ok=True)
    dest = asset_out / source_path.name
    shutil.copy2(source_path, dest)
    return f"assets/{dest.name}"


def markdown_to_html(markdown: str, source_file: Path, asset_out: Path) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    i = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline_format(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            out.append("<ul>")
            out.extend(f"<li>{inline_format(item)}</li>" for item in list_items)
            out.append("</ul>")
            list_items = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped == "":
            flush_paragraph()
            flush_list()
            i += 1
            continue

        if stripped.startswith("```mermaid"):
            flush_paragraph()
            flush_list()
            i += 1
            block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            out.append(f"<pre class=\"mermaid\">{html.escape(chr(10).join(block))}</pre>")
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            i += 1
            block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(block))}</code></pre>")
            continue

        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            flush_paragraph()
            flush_list()
            alt, src = image_match.groups()
            out_src = copy_image(src, source_file, asset_out)
            out.append(
                f"<figure><img src=\"{html.escape(out_src)}\" alt=\"{html.escape(alt)}\">"
                f"<figcaption>{html.escape(alt)}</figcaption></figure>"
            )
            i += 1
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            flush_list()
            table_html, i = parse_table(lines, i)
            out.append(table_html)
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            text = heading.group(2)
            out.append(f"<h{level}>{inline_format(text)}</h{level}>")
            i += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            flush_list()
            quote = stripped.lstrip(">").strip()
            out.append(f"<blockquote>{inline_format(quote)}</blockquote>")
            i += 1
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            list_items.append(stripped[2:].strip())
            i += 1
            continue

        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    flush_list()
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument(
        "--export-root",
        type=Path,
        default=DEFAULT_EXPORT_ROOT,
        help="Generated artifact root that should receive recording/ outputs.",
    )
    args = parser.parse_args()

    out_dir = args.export_root / "recording"
    asset_out = out_dir / "assets"
    out_html = out_dir / "markdown-report-recording.html"
    out_dir.mkdir(parents=True, exist_ok=True)
    body = markdown_to_html(args.source.read_text(encoding="utf-8"), args.source, asset_out)
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Biomedicine Final Report Recording Surface</title>
  <style>
    :root {{
      color-scheme: light;
      --text: #111827;
      --muted: #4b5563;
      --line: #d1d5db;
      --paper: #ffffff;
      --bg: #f3f4f6;
      --accent: #0f766e;
    }}
    html {{
      scroll-behavior: smooth;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.58;
      font-size: 20px;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 48px 54px 80px;
      background: var(--paper);
      min-height: 100vh;
      box-shadow: 0 0 0 1px rgba(17, 24, 39, 0.08);
    }}
    h1 {{
      font-size: 54px;
      margin: 0 0 12px;
      line-height: 1.06;
    }}
    h2 {{
      font-size: 34px;
      margin: 48px 0 16px;
      padding-top: 16px;
      border-top: 2px solid var(--line);
      line-height: 1.16;
    }}
    h3 {{
      font-size: 26px;
      margin-top: 34px;
    }}
    p, li {{
      color: var(--text);
    }}
    code {{
      font-size: 0.9em;
      background: #eef2f7;
      padding: 0.08em 0.28em;
      border-radius: 4px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 22px 0 30px;
      font-size: 18px;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 11px 12px;
      vertical-align: top;
      text-align: left;
    }}
    th {{
      background: #ecfdf5;
      color: #064e3b;
    }}
    blockquote {{
      margin: 26px 0;
      border-left: 6px solid var(--accent);
      padding: 12px 18px;
      background: #f0fdfa;
      font-size: 1.08em;
    }}
    figure {{
      margin: 30px 0 36px;
      padding: 16px;
      border: 1px solid var(--line);
      background: #ffffff;
    }}
    img {{
      display: block;
      max-width: 100%;
      max-height: 78vh;
      object-fit: contain;
      margin: 0 auto;
    }}
    figcaption {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 15px;
      text-align: center;
    }}
    pre {{
      white-space: pre-wrap;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 18px;
      background: #f8fafc;
      font-size: 16px;
    }}
    pre.mermaid {{
      background: #ffffff;
      text-align: center;
      font-size: 18px;
    }}
    .recording-banner {{
      position: sticky;
      top: 0;
      z-index: 20;
      margin: -48px -54px 36px;
      padding: 12px 54px;
      background: #0f172a;
      color: white;
      font-size: 15px;
      display: flex;
      justify-content: space-between;
      gap: 18px;
    }}
    .recording-banner span {{
      color: #cbd5e1;
    }}
    @media (max-width: 760px) {{
      body {{ font-size: 17px; }}
      main {{ padding: 28px 18px 52px; }}
      h1 {{ font-size: 38px; }}
      h2 {{ font-size: 26px; }}
      table {{ font-size: 15px; }}
      .recording-banner {{
        margin: -28px -18px 28px;
        padding: 10px 18px;
        display: block;
      }}
    }}
  </style>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{ startOnLoad: true, theme: 'default', securityLevel: 'loose' }});
  </script>
</head>
<body>
<main>
  <div class="recording-banner">
    <strong>Recording surface</strong>
    <span>Scroll slowly. Hold diagrams and paper figures for narration.</span>
  </div>
{body}
</main>
</body>
</html>
"""
    out_html.write_text(html_doc, encoding="utf-8")
    print(out_html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
