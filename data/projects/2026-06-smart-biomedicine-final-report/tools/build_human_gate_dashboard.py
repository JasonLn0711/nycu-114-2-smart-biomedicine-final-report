#!/usr/bin/env python3
"""Build a browser dashboard for the current human review gate."""

from __future__ import annotations

import csv
import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EXPORT = ROOT / "exports/smart-biomedicine-gpt-sovits"
REFERENCE = EXPORT / "reference"
QUALITY_CSV = EXPORT / "qa/reference-quality/reference-quality-manifest.csv"
TRANSCRIPT_GATE = EXPORT / "qa/reference-transcript-gate.md"
DELIVERY_GATE = EXPORT / "qa/delivery-gate-status.md"
REFERENCE_DECISION_STATUS = EXPORT / "qa/reference-decisions/reference-decision-status.md"
VISUAL_QC = EXPORT / "qa/reference-visual-qc"
OUT_DIR = EXPORT / "review-packet/human-gate-dashboard"
OUT = OUT_DIR / "index.html"


def read_quality() -> list[dict[str, str]]:
    if not QUALITY_CSV.exists():
        return []
    with QUALITY_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else "Not generated yet."


def command_block(candidate: str) -> str:
    return f"""python3 data/projects/2026-06-smart-biomedicine-final-report/tools/create_exact_transcript.py \\
  --candidate {candidate} \\
  --text "<exact transcript text>" \\
  --ack-human-listened \\
  --ack-transcript-exact

python3 data/projects/2026-06-smart-biomedicine-final-report/tools/advance_after_reference_review.py \\
  --candidate {candidate} \\
  --accept-reference \\
  --ack-human-listened \\
  --ack-own-voice-authorized \\
  --ack-3-to-10s \\
  --ack-clean-audio \\
  --ack-no-heavy-filler \\
  --ack-no-clipping \\
  --ack-transcript-exact"""


def reject_command(candidate: str) -> str:
    return f"""python3 data/projects/2026-06-smart-biomedicine-final-report/tools/mark_reference_review_decision.py \\
  --candidate {candidate} \\
  --decision rejected \\
  --notes "<why rejected after human listening>" \\
  --ack-human-listened"""


def card(row: dict[str, str]) -> str:
    path = Path(row["file"])
    name = path.name
    stem = path.stem
    if not name.startswith("prompt_ref_candidate_"):
        return ""
    audio_src = f"../../reference/{html.escape(name)}"
    exact_target = REFERENCE / f"{stem}.exact-transcript.txt"
    template = EXPORT / f"review-packet/reference-transcript-review/{stem}.exact-transcript.TEMPLATE.txt"
    exact_display = exact_target.relative_to(ROOT)
    template_display = template.relative_to(ROOT)
    waveform = VISUAL_QC / f"{stem}.waveform.png"
    spectrogram = VISUAL_QC / f"{stem}.spectrogram.png"
    visual_html = ""
    if waveform.exists() and spectrogram.exists():
        waveform_src = f"../../qa/reference-visual-qc/{html.escape(waveform.name)}"
        spectrogram_src = f"../../qa/reference-visual-qc/{html.escape(spectrogram.name)}"
        visual_html = f"""
        <figure>
          <img src="{waveform_src}" alt="Waveform for {html.escape(stem)}">
          <figcaption>Waveform</figcaption>
        </figure>
        <figure>
          <img src="{spectrogram_src}" alt="Spectrogram for {html.escape(stem)}">
          <figcaption>Spectrogram</figcaption>
        </figure>
"""
    return f"""
      <section class="card">
        <div class="card-head">
          <h2>{html.escape(stem)}</h2>
          <span class="score">score {html.escape(row['machine_score'])}</span>
        </div>
        <audio controls src="{audio_src}"></audio>
        {visual_html}
        <table>
          <tr><th>Duration</th><td>{html.escape(row['duration_seconds'])}s</td></tr>
          <tr><th>RMS</th><td>{html.escape(row['rms'])}</td></tr>
          <tr><th>Peak</th><td>{html.escape(row['peak'])}</td></tr>
          <tr><th>Near-clip ratio</th><td>{html.escape(row['near_clip_ratio'])}</td></tr>
          <tr><th>Silence ratio</th><td>{html.escape(row['silence_ratio'])}</td></tr>
          <tr><th>Machine note</th><td>{html.escape(row['recommendation'])}</td></tr>
          <tr><th>Exact transcript target</th><td><code>{html.escape(str(exact_display))}</code></td></tr>
          <tr><th>Template</th><td><code>{html.escape(str(template_display))}</code></td></tr>
        </table>
        <details>
          <summary>Commands after human listening accepts this candidate</summary>
          <pre>{html.escape(command_block(stem))}</pre>
        </details>
        <details>
          <summary>Command if human listening rejects this candidate</summary>
          <pre>{html.escape(reject_command(stem))}</pre>
        </details>
      </section>
"""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_quality()
    prompt_cards = "\n".join(card(row) for row in rows)
    delivery = html.escape(read_text(DELIVERY_GATE))
    transcript = html.escape(read_text(TRANSCRIPT_GATE))
    decision_status = html.escape(read_text(REFERENCE_DECISION_STATUS))
    workbook = EXPORT / "review-packet/reference-listening-workbook/index.html"
    workbook_link = ""
    if workbook.exists():
        workbook_link = """
  <div class="notice">
    Low-friction exact-transcript workbook is available at
    <a href="../reference-listening-workbook/index.html">reference-listening-workbook/index.html</a>.
    Use it for slowed review audio, ASR draft comparison, and command generation.
  </div>
"""

    OUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Biomedicine Human Gate Dashboard</title>
  <style>
    :root {{
      --text: #111827;
      --muted: #4b5563;
      --line: #d1d5db;
      --paper: #ffffff;
      --bg: #f3f4f6;
      --accent: #2563eb;
      --warn: #b45309;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{
      max-width: 1160px;
      margin: 0 auto;
      padding: 40px 24px 72px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 38px;
    }}
    .lead {{
      margin: 0 0 26px;
      color: var(--muted);
      font-size: 18px;
    }}
    .notice {{
      background: #fffbeb;
      border: 1px solid #f59e0b;
      border-radius: 8px;
      padding: 14px 16px;
      margin: 18px 0 26px;
      color: #78350f;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 18px;
    }}
    .card, .panel {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }}
    .card-head {{
      display: block;
      margin-bottom: 12px;
    }}
    h2 {{
      font-size: 20px;
      margin: 0 0 4px;
      overflow-wrap: anywhere;
    }}
    .score {{
      color: var(--accent);
      font-weight: 700;
      display: inline-block;
      font-size: 14px;
    }}
    audio {{
      width: 100%;
      margin: 6px 0 12px;
    }}
    figure {{
      margin: 10px 0 12px;
    }}
    img {{
      display: block;
      max-width: 100%;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
      background: #ffffff;
    }}
    figcaption {{
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
      text-align: center;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      border-top: 1px solid #e5e7eb;
      padding: 7px 6px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      width: 132px;
      color: var(--muted);
      font-weight: 650;
    }}
    code, pre {{
      background: #f8fafc;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
    }}
    code {{
      padding: 0.06em 0.28em;
      word-break: break-all;
    }}
    pre {{
      overflow-x: auto;
      white-space: pre-wrap;
      padding: 12px;
      font-size: 13px;
    }}
    details {{
      margin-top: 12px;
    }}
    summary {{
      cursor: pointer;
      color: var(--accent);
      font-weight: 650;
    }}
    .panels {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      margin-top: 24px;
    }}
    @media (max-width: 760px) {{
      .panels {{ grid-template-columns: 1fr; }}
      main {{ padding: 26px 16px 50px; }}
      h1 {{ font-size: 30px; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>Human Gate Dashboard</h1>
  <p class="lead">Current gate: listen to prompt references, write exact transcript text, and accept exactly one reference before formal GPT-SoVITS generation.</p>
  {workbook_link}
  <div class="notice">
    Machine QA shows every current candidate reaches digital full scale. Listen specifically for clipping, harsh consonants, tail residue, room noise, long pauses, and transcript mismatch.
  </div>
  <div class="grid">
    {prompt_cards}
  </div>
  <div class="panels">
    <section class="panel">
      <h2>Reference Transcript Gate</h2>
      <pre>{transcript}</pre>
    </section>
    <section class="panel">
      <h2>Delivery Gate</h2>
      <pre>{delivery}</pre>
    </section>
    <section class="panel">
      <h2>Reference Decision Status</h2>
      <pre>{decision_status}</pre>
    </section>
  </div>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(OUT)
    print(f"prompt_references={sum(1 for row in rows if Path(row['file']).name.startswith('prompt_ref_candidate_'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
