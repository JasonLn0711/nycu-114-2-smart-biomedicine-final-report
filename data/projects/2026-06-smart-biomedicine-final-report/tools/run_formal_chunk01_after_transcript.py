#!/usr/bin/env python3
"""Generate formal chunk 01 after the prompt transcript is human verified."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from accepted_reference import resolve_accepted_reference


ROOT = Path(__file__).resolve().parents[4]
CHUNK_ID = "sbm_tts_01_opening"
OUT_WAV = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_01_opening.wav"
GENERATOR = ROOT / "data/projects/2026-06-smart-biomedicine-final-report/tools/generate_gptsovits_chunk.py"


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def main() -> int:
    try:
        accepted = resolve_accepted_reference()
    except RuntimeError as exc:
        return fail(
            "accepted reference is not ready",
            str(exc),
        )

    text = accepted.exact_transcript.read_text(encoding="utf-8").strip()
    if not text:
        return fail(f"exact transcript file is empty: {accepted.exact_transcript}")
    lowered = accepted.exact_transcript.name.lower() + "\n" + text.lower()
    blocked_markers = ["draft", "asr", "pending", "todo", "template"]
    for marker in blocked_markers:
        if marker in lowered:
            return fail(
                "exact transcript still looks provisional",
                f"Remove marker `{marker}` after human verification before production.",
            )

    cmd = [
        "python3",
        str(GENERATOR),
        "--chunk-id",
        CHUNK_ID,
        "--ref-audio",
        str(accepted.wav),
        "--ref-text",
        str(accepted.exact_transcript),
    ]
    gen = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if gen.returncode != 0:
        return fail("formal chunk 01 generation failed", gen.stdout)
    if not OUT_WAV.exists():
        return fail("formal chunk 01 command finished without output WAV", gen.stdout)

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
            str(OUT_WAV),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if probe.returncode != 0:
        return fail("ffprobe failed for formal chunk 01", probe.stdout)

    print("PASS: formal chunk 01 generated")
    print(f"accepted_reference={accepted.stem}")
    print(gen.stdout.strip())
    print(probe.stdout.strip())
    print("Next gate: listen to chunk 01 and update gpt-sovits-audio-qa-sheet-v1.md before generating chunks 02-14.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
