#!/usr/bin/env python3
"""Build a low-friction workbook for reference listening and exact transcript entry."""

from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EXPORT = ROOT / "exports/smart-biomedicine-gpt-sovits"
REFERENCE = EXPORT / "reference"
OUT_DIR = EXPORT / "review-packet/reference-listening-workbook"
AUDIO_DIR = OUT_DIR / "audio"
OUT = OUT_DIR / "index.html"


def prompt_references() -> list[Path]:
    return sorted(REFERENCE.glob("prompt_ref_candidate_*.wav"))


def plain_draft_text(stem: str) -> str:
    path = REFERENCE / f"{stem}.asr-draft.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    marker = "## Plain draft"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()


def timed_draft_text(stem: str) -> str:
    path = REFERENCE / f"{stem}.asr-draft.md"
    if not path.exists():
        return ""
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("[") and "]" in line:
            lines.append(line)
    return "\n".join(lines)


def build_review_audio(src: Path) -> Path:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    dst = AUDIO_DIR / f"{src.stem}.review_0p85x_minus3dB.wav"
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(src),
        "-filter:a",
        "atempo=0.85,volume=-3dB",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-sample_fmt",
        "s16",
        str(dst),
    ]
    subprocess.run(command, check=True)
    return dst


def copy_original(src: Path) -> Path:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    dst = AUDIO_DIR / src.name
    shutil.copy2(src, dst)
    return dst


def create_command(stem: str) -> str:
    return f"""python3 data/projects/2026-06-smart-biomedicine-final-report/tools/create_exact_transcript.py \\
  --candidate {stem} \\
  --text "<exact transcript text>" \\
  --ack-human-listened \\
  --ack-transcript-exact"""


def advance_command(stem: str) -> str:
    return f"""python3 data/projects/2026-06-smart-biomedicine-final-report/tools/advance_after_reference_review.py \\
  --candidate {stem} \\
  --accept-reference \\
  --ack-human-listened \\
  --ack-own-voice-authorized \\
  --ack-3-to-10s \\
  --ack-clean-audio \\
  --ack-no-heavy-filler \\
  --ack-no-clipping \\
  --ack-transcript-exact"""


def reject_command(stem: str) -> str:
    return f"""python3 data/projects/2026-06-smart-biomedicine-final-report/tools/mark_reference_review_decision.py \\
  --candidate {stem} \\
  --decision rejected \\
  --notes "<why rejected after human listening>" \\
  --ack-human-listened"""


def candidate_section(src: Path) -> str:
    stem = src.stem
    original = copy_original(src)
    review = build_review_audio(src)
    exact_target = REFERENCE / f"{stem}.exact-transcript.txt"
    timed = timed_draft_text(stem)
    plain = plain_draft_text(stem)
    return f"""
    <section class="candidate" id="{html.escape(stem)}">
      <header>
        <h2>{html.escape(stem)}</h2>
        <span>Exact transcript target: <code>{html.escape(str(exact_target.relative_to(ROOT)))}</code></span>
      </header>

      <div class="audio-grid">
        <div>
          <h3>Original prompt reference</h3>
          <audio controls src="audio/{html.escape(original.name)}"></audio>
        </div>
        <div>
          <h3>Transcript aid: 0.85x, -3 dB</h3>
          <audio controls src="audio/{html.escape(review.name)}"></audio>
        </div>
      </div>

      <div class="columns">
        <div>
          <h3>Timed ASR draft, not exact</h3>
          <pre>{html.escape(timed or "No timed draft found.")}</pre>
        </div>
        <div>
          <h3>Plain ASR draft, not exact</h3>
          <pre>{html.escape(plain or "No plain draft found.")}</pre>
        </div>
      </div>

      <label for="{html.escape(stem)}-text">Human exact transcript</label>
      <textarea id="{html.escape(stem)}-text" data-candidate="{html.escape(stem)}" spellcheck="false" placeholder="Type only the human-verified exact transcript here. Do not paste ASR draft unless you have listened and corrected it."></textarea>

      <div class="checks">
        <label><input type="checkbox"> I listened with headphones.</label>
        <label><input type="checkbox"> The transcript exactly matches the audio.</label>
        <label><input type="checkbox"> No obvious clipping, harsh consonants, laughter, long pause, or heavy filler.</label>
        <label><input type="checkbox"> This is Jason's own authorized voice for this course report.</label>
      </div>

      <button type="button" data-build="{html.escape(stem)}">Build commands from this transcript</button>

      <h3>Manual command template</h3>
      <pre># Accept path
{html.escape(create_command(stem))}

{html.escape(advance_command(stem))}</pre>

      <h3>Reject command template</h3>
      <pre>{html.escape(reject_command(stem))}</pre>

      <h3>Generated command</h3>
      <pre id="{html.escape(stem)}-command">Enter an exact transcript above, then press Build commands.</pre>
    </section>
"""


def main() -> int:
    refs = prompt_references()
    if not refs:
        raise SystemExit(f"No prompt_ref_candidate_*.wav files found under {REFERENCE}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sections = "\n".join(candidate_section(src) for src in refs)
    OUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Reference Listening Workbook</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --paper: #ffffff;
      --text: #111827;
      --muted: #4b5563;
      --line: #d1d5db;
      --accent: #2563eb;
      --warn: #92400e;
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
    h1 {{
      margin: 0 0 8px;
      font-size: 38px;
    }}
    .lead {{
      color: var(--muted);
      margin: 0 0 18px;
      font-size: 18px;
    }}
    .notice {{
      border: 1px solid #f59e0b;
      color: var(--warn);
      background: #fffbeb;
      border-radius: 8px;
      padding: 14px 16px;
      margin: 18px 0 26px;
    }}
    .candidate {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin: 18px 0;
    }}
    header {{
      display: flex;
      gap: 12px;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      border-bottom: 1px solid #e5e7eb;
      padding-bottom: 10px;
      margin-bottom: 14px;
    }}
    h2 {{
      margin: 0;
      font-size: 22px;
      overflow-wrap: anywhere;
    }}
    h3 {{
      margin: 12px 0 6px;
      font-size: 15px;
      color: var(--muted);
    }}
    .audio-grid, .columns {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}
    audio {{
      width: 100%;
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
      min-height: 42px;
      font-size: 13px;
    }}
    code {{
      padding: 0.06em 0.28em;
      word-break: break-all;
    }}
    label {{
      display: block;
      font-weight: 650;
      margin: 12px 0 6px;
    }}
    textarea {{
      width: 100%;
      min-height: 96px;
      box-sizing: border-box;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      font-size: 16px;
      line-height: 1.6;
    }}
    .checks {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px 12px;
      margin: 10px 0 14px;
    }}
    .checks label {{
      margin: 0;
      font-weight: 500;
      color: var(--muted);
    }}
    button {{
      border: 1px solid #1d4ed8;
      background: var(--accent);
      color: #ffffff;
      border-radius: 8px;
      padding: 10px 14px;
      font-weight: 700;
      cursor: pointer;
    }}
    @media (max-width: 780px) {{
      main {{ padding: 28px 16px 48px; }}
      h1 {{ font-size: 30px; }}
      .audio-grid, .columns, .checks {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>Reference Listening Workbook</h1>
  <p class="lead">Use this page to listen, slow down, write, and copy the exact transcript command for one GPT-SoVITS prompt reference.</p>
  <div class="notice">
    The slowed review audio is only for transcript verification. Production still uses the original prompt WAV plus a human-confirmed exact transcript. Do not accept an ASR draft without listening.
  </div>
  {sections}
</main>
<script>
function shellQuote(value) {{
  return "'" + value.replace(/'/g, "'\"'\"'") + "'";
}}

function createCommand(candidate, transcript) {{
  return `python3 data/projects/2026-06-smart-biomedicine-final-report/tools/create_exact_transcript.py \\
  --candidate ${{candidate}} \\
  --text ${{shellQuote(transcript)}} \\
  --ack-human-listened \\
  --ack-transcript-exact`;
}}

function advanceCommand(candidate) {{
  return `python3 data/projects/2026-06-smart-biomedicine-final-report/tools/advance_after_reference_review.py \\
  --candidate ${{candidate}} \\
  --accept-reference \\
  --ack-human-listened \\
  --ack-own-voice-authorized \\
  --ack-3-to-10s \\
  --ack-clean-audio \\
  --ack-no-heavy-filler \\
  --ack-no-clipping \\
  --ack-transcript-exact`;
}}

document.querySelectorAll("button[data-build]").forEach((button) => {{
  button.addEventListener("click", () => {{
    const candidate = button.dataset.build;
    const textarea = document.getElementById(candidate + "-text");
    const output = document.getElementById(candidate + "-command");
    const transcript = textarea.value.trim();
    if (!transcript) {{
      output.textContent = "Transcript is empty.";
      return;
    }}
    output.textContent = createCommand(candidate, transcript) + "\\n\\n" + advanceCommand(candidate);
  }});
}});
</script>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(OUT)
    print(f"prompt_references={len(refs)}")
    print(f"review_audio={len(list(AUDIO_DIR.glob('*.review_0p85x_minus3dB.wav')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
