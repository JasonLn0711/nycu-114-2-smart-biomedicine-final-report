#!/usr/bin/env python3
"""Build a per-chunk ASR QA workbook for formal GPT-SoVITS WAVs."""

from __future__ import annotations

import html
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
CHUNK_SOURCE = PROJECT / "gpt-sovits-narration-chunks-v1.md"
EXPORT = ROOT / "exports/smart-biomedicine-gpt-sovits"
CHUNKS = EXPORT / "chunks"
DECISIONS = EXPORT / "qa/chunk-decisions"
CHUNK_ASR = EXPORT / "qa/chunk-asr"
OUT_DIR = EXPORT / "review-packet/chunk-qa-workbook"
OUT = OUT_DIR / "index.html"

CHUNK_IDS = [
    "sbm_tts_01_opening",
    "sbm_tts_02_markdown_format",
    "sbm_tts_03_definitions",
    "sbm_tts_04_workflow_problem",
    "sbm_tts_05_speech_to_summary",
    "sbm_tts_06_evidence_landscape",
    "sbm_tts_07_hager_boundary",
    "sbm_tts_08_lang1_overview",
    "sbm_tts_09_lang1_results",
    "sbm_tts_10_architecture",
    "sbm_tts_11_scope_controls",
    "sbm_tts_12_synthetic_example",
    "sbm_tts_13_validation_risk",
    "sbm_tts_14_closing",
]


@dataclass
class Chunk:
    chunk_id: str
    markdown_position: str = ""
    target_visual_hold: str = ""
    planned_wav: str = ""
    pronunciation_notes: str = ""
    text: str = ""


def ffprobe_summary(path: Path) -> str:
    run = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_name,sample_rate,channels",
            "-show_entries",
            "format=duration,size",
            "-of",
            "default=nw=1:nk=0",
            str(path),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return run.stdout.strip() if run.returncode == 0 else run.stdout.strip()


def parse_chunks() -> list[Chunk]:
    text = CHUNK_SOURCE.read_text(encoding="utf-8")
    pieces = re.split(r"^###\s+", text, flags=re.MULTILINE)
    chunks: list[Chunk] = []
    for piece in pieces[1:]:
        header, _, body = piece.partition("\n")
        chunk_id = header.strip()
        if chunk_id not in CHUNK_IDS:
            continue
        chunk = Chunk(chunk_id=chunk_id)
        for line in body.splitlines():
            if line.startswith("- Markdown position:"):
                chunk.markdown_position = line.split(":", 1)[1].strip().replace("`", "").rstrip(".")
            elif line.startswith("- Target visual hold:"):
                chunk.target_visual_hold = line.split(":", 1)[1].strip().replace("`", "").rstrip(".")
            elif line.startswith("- Planned WAV:"):
                chunk.planned_wav = line.split(":", 1)[1].strip().replace("`", "").rstrip(".")
            elif line.startswith("- Pronunciation notes:"):
                chunk.pronunciation_notes = line.split(":", 1)[1].strip().replace("`", "").rstrip(".")
        match = re.search(r"```text\n(.*?)\n```", body, flags=re.DOTALL)
        if match:
            chunk.text = match.group(1).strip()
        chunks.append(chunk)
    by_id = {chunk.chunk_id: chunk for chunk in chunks}
    return [by_id[chunk_id] for chunk_id in CHUNK_IDS if chunk_id in by_id]


def decision(chunk_id: str) -> tuple[str, Path | None]:
    accepted = DECISIONS / f"{chunk_id}.accepted.md"
    rejected = DECISIONS / f"{chunk_id}.rejected.md"
    if accepted.exists():
        return "accepted", accepted
    if rejected.exists():
        return "rejected", rejected
    return "pending", None


def accept_command(chunk_id: str) -> str:
    return f"""python3 data/projects/2026-06-smart-biomedicine-final-report/tools/chunk_asr_qa.py \\
  --chunk-id {chunk_id} \\
  --language en \\
  --gate \\
  --auto-decision"""


def reject_command(chunk_id: str) -> str:
    return f"""python3 data/projects/2026-06-smart-biomedicine-final-report/tools/chunk_asr_qa.py \\
  --chunk-id {chunk_id} \\
  --language en \\
  --gate \\
  --auto-decision"""


def generate_next_command(chunk_id: str) -> str:
    if chunk_id == CHUNK_IDS[0]:
        return "python3 data/projects/2026-06-smart-biomedicine-final-report/tools/run_formal_chunk01_after_transcript.py"
    return (
        "python3 data/projects/2026-06-smart-biomedicine-final-report/tools/"
        f"generate_next_chunk_after_acceptance.py --chunk-id {chunk_id}"
    )


def card(chunk: Chunk) -> str:
    wav = CHUNKS / f"{chunk.chunk_id}.wav"
    state, marker = decision(chunk.chunk_id)
    audio = (
        f'<audio controls src="../../chunks/{html.escape(wav.name)}"></audio>'
        if wav.exists()
        else '<div class="missing">Formal WAV not generated yet.</div>'
    )
    facts = ffprobe_summary(wav) if wav.exists() else ""
    marker_text = str(marker.relative_to(ROOT)) if marker else ""
    asr_path = CHUNK_ASR / f"{chunk.chunk_id}.asr-qa.md"
    asr_html = ""
    if asr_path.exists():
        asr_html = f"""
      <details open>
        <summary>Breeze-ASR-25 transcript gate report</summary>
        <pre>{html.escape(asr_path.read_text(encoding="utf-8"))}</pre>
      </details>
"""
    return f"""
    <section class="card" id="{html.escape(chunk.chunk_id)}">
      <header>
        <h2>{html.escape(chunk.chunk_id)}</h2>
        <span class="status {html.escape(state)}">{html.escape(state)}</span>
      </header>
      <dl>
        <dt>Markdown position</dt><dd>{html.escape(chunk.markdown_position)}</dd>
        <dt>Target visual hold</dt><dd>{html.escape(chunk.target_visual_hold)}</dd>
        <dt>Pronunciation notes</dt><dd>{html.escape(chunk.pronunciation_notes)}</dd>
        <dt>Decision marker</dt><dd><code>{html.escape(marker_text or 'none')}</code></dd>
      </dl>
      {audio}
      <h3>Chunk text to verify</h3>
      <pre>{html.escape(chunk.text)}</pre>
      <h3>ASR transcript checklist</h3>
      <ul class="checks">
        <li>Breeze-ASR-25 runs on RTX 4090 CUDA, with no CPU fallback.</li>
        <li>Normalized transcript matches the source text above.</li>
        <li>No missing words, repeated words, or swallowed final words appear in the ASR output.</li>
        <li>Technical terms match pronunciation notes.</li>
        <li>If the gate fails, use the generated repair plan and regenerate only this chunk.</li>
      </ul>
      <details>
        <summary>Generate this chunk when gated</summary>
        <pre>{html.escape(generate_next_command(chunk.chunk_id))}</pre>
      </details>
      <details>
        <summary>Run ASR gate and auto-decision command</summary>
        <pre>{html.escape(accept_command(chunk.chunk_id))}</pre>
      </details>
      <details>
        <summary>Same command writes rejected marker and repair plan if transcript fails</summary>
        <pre>{html.escape(reject_command(chunk.chunk_id))}</pre>
      </details>
      {asr_html}
      <details>
        <summary>WAV facts</summary>
        <pre>{html.escape(facts or 'Not generated yet.')}</pre>
      </details>
    </section>
"""


def main() -> int:
    chunks = parse_chunks()
    generated = sum((CHUNKS / f"{chunk.chunk_id}.wav").exists() for chunk in chunks)
    accepted = sum((DECISIONS / f"{chunk.chunk_id}.accepted.md").exists() for chunk in chunks)
    rejected = sum((DECISIONS / f"{chunk.chunk_id}.rejected.md").exists() for chunk in chunks)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cards = "\n".join(card(chunk) for chunk in chunks)
    OUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Chunk QA Workbook</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --paper: #ffffff;
      --text: #111827;
      --muted: #4b5563;
      --line: #d1d5db;
      --accent: #2563eb;
      --ok: #047857;
      --bad: #b91c1c;
      --pending: #92400e;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 40px 24px 72px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 38px; }}
    .lead {{ margin: 0 0 22px; color: var(--muted); font-size: 18px; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 24px;
    }}
    .summary div, .card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .summary strong {{ display: block; font-size: 26px; }}
    .card {{ margin: 16px 0; }}
    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid #e5e7eb;
      padding-bottom: 10px;
      margin-bottom: 12px;
    }}
    h2 {{ margin: 0; font-size: 22px; overflow-wrap: anywhere; }}
    h3 {{ margin: 14px 0 6px; font-size: 15px; color: var(--muted); }}
    .status {{
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 13px;
      font-weight: 800;
      background: #fffbeb;
      color: var(--pending);
    }}
    .status.accepted {{ background: #ecfdf5; color: var(--ok); }}
    .status.rejected {{ background: #fef2f2; color: var(--bad); }}
    dl {{
      display: grid;
      grid-template-columns: 170px 1fr;
      gap: 6px 12px;
      margin: 0 0 12px;
    }}
    dt {{ color: var(--muted); font-weight: 700; }}
    dd {{ margin: 0; }}
    audio {{ width: 100%; margin: 8px 0; }}
    .missing {{
      border: 1px dashed var(--line);
      border-radius: 8px;
      padding: 14px;
      color: var(--muted);
      background: #f9fafb;
    }}
    pre, code {{
      background: #f8fafc;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
    }}
    pre {{
      white-space: pre-wrap;
      overflow-x: auto;
      padding: 12px;
      font-size: 13px;
    }}
    code {{ padding: 0.06em 0.28em; word-break: break-all; }}
    .checks {{ margin: 8px 0 10px 18px; padding: 0; }}
    details {{ margin: 8px 0; }}
    summary {{ cursor: pointer; color: var(--accent); font-weight: 700; }}
    @media (max-width: 780px) {{
      main {{ padding: 28px 16px 48px; }}
      h1 {{ font-size: 30px; }}
      .summary {{ grid-template-columns: 1fr; }}
      dl {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>Chunk QA Workbook</h1>
  <p class="lead">Use this page after each formal GPT-SoVITS chunk is generated. Run Breeze-ASR-25 on RTX 4090, compare the transcript against the source text, then accept or repair before generating the next chunk.</p>
  <section class="summary">
    <div><strong>{generated}/14</strong> generated WAVs</div>
    <div><strong>{accepted}/14</strong> accepted markers</div>
    <div><strong>{rejected}</strong> rejected markers</div>
  </section>
  {cards}
</main>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(OUT)
    print(f"chunks={len(chunks)} generated={generated} accepted={accepted} rejected={rejected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
