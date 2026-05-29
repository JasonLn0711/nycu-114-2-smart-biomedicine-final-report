#!/usr/bin/env python3
"""Build a local review packet for prompt-reference transcript verification."""

from __future__ import annotations

import html
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/reference"
OUT_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/review-packet/reference-transcript-review"
INDEX = OUT_DIR / "index.html"


def ffprobe_facts(path: Path) -> str:
    probe = subprocess.run(
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
    if probe.returncode != 0:
        return probe.stdout.strip()
    return probe.stdout.strip()


def plain_draft(stem: str) -> str:
    draft = REFERENCE_DIR / f"{stem}.asr-draft.md"
    if not draft.exists():
        return ""
    text = draft.read_text(encoding="utf-8")
    match = re.search(r"## Plain draft\s+(.+?)\s*$", text, re.S)
    return match.group(1).strip() if match else ""


def prompt_refs() -> list[Path]:
    return sorted(REFERENCE_DIR.glob("prompt_ref_candidate_*.wav"))


def write_template(wav: Path, draft_text: str) -> Path:
    template = OUT_DIR / f"{wav.stem}.exact-transcript.TEMPLATE.txt"
    template.write_text(
        "\n".join(
            [
                "# Replace this template with the exact human-verified transcript only.",
                "# Do not copy this file into the reference directory until every spoken",
                "# syllable has been checked against the audio.",
                "#",
                f"# source_wav: {wav}",
                "# asr_draft_below_is_not_exact:",
                f"# {draft_text}",
                "",
                "<write exact transcript here>",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return template


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    refs = prompt_refs()
    cards = []
    for wav in refs:
        draft_text = plain_draft(wav.stem)
        template = write_template(wav, draft_text)
        exact_target = REFERENCE_DIR / f"{wav.stem}.exact-transcript.txt"
        facts = ffprobe_facts(wav)
        rel_audio = Path("../../reference") / wav.name
        cards.append(
            f"""
      <section class="card">
        <h2>{html.escape(wav.stem)}</h2>
        <audio controls src="{html.escape(str(rel_audio))}"></audio>
        <dl>
          <dt>Exact transcript target</dt>
          <dd><code>{html.escape(str(exact_target))}</code></dd>
          <dt>Template</dt>
          <dd><code>{html.escape(str(template))}</code></dd>
        </dl>
        <h3>ASR Draft Only</h3>
        <p>{html.escape(draft_text)}</p>
        <h3>Audio Facts</h3>
        <pre>{html.escape(facts)}</pre>
        <h3>Human Decision Checklist</h3>
        <ul>
          <li>Formal, report-usable tone.</li>
          <li>Stable volume and microphone distance.</li>
          <li>No laughter, long pause, room-noise burst, or heavy filler.</li>
          <li>No clipping, harsh consonant artifact, or tail residue.</li>
          <li>Exact transcript matches the audio syllable-by-syllable.</li>
        </ul>
      </section>
"""
        )

    INDEX.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Biomedicine Reference Transcript Review</title>
  <style>
    body {{
      margin: 0;
      background: #f5f5f4;
      color: #1c1917;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{
      max-width: 1050px;
      margin: 0 auto;
      padding: 42px 28px 72px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 36px;
    }}
    .lead {{
      margin: 0 0 28px;
      color: #57534e;
      font-size: 18px;
    }}
    .card {{
      background: white;
      border: 1px solid #d6d3d1;
      border-radius: 8px;
      padding: 22px;
      margin: 18px 0;
    }}
    audio {{
      width: 100%;
    }}
    code, pre {{
      background: #f5f5f4;
      border-radius: 5px;
    }}
    code {{
      padding: 0.08em 0.3em;
    }}
    pre {{
      white-space: pre-wrap;
      padding: 12px;
      border: 1px solid #e7e5e4;
    }}
    dt {{
      font-weight: 700;
      margin-top: 10px;
    }}
    dd {{
      margin-left: 0;
    }}
  </style>
</head>
<body>
<main>
  <h1>Reference Transcript Review</h1>
  <p class="lead">Use this packet to choose one clean prompt-mode reference. ASR text is only a draft. Production requires a human-verified exact transcript and an accepted reference marker.</p>
  {''.join(cards)}
</main>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(INDEX)
    print(f"templates: {len(refs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
