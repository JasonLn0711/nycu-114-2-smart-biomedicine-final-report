#!/usr/bin/env python3
"""Safely write an exact transcript file after Breeze-ASR-25 verification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/reference"
BLOCKED = ["draft", "asr", "pending", "todo", "template", "<write exact transcript here>"]


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, help="Prompt reference stem, for example prompt_ref_candidate_04_000381_8p00s.")
    parser.add_argument("--text", default="", help="Exact transcript text. If omitted, use --from-file.")
    parser.add_argument("--from-file", default="", help="Path to a plain text exact transcript.")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--ack-human-listened", action="store_true")
    parser.add_argument("--ack-breeze-asr-25-cuda", action="store_true")
    parser.add_argument("--ack-breeze-asr-25-transcript-pass", action="store_true")
    parser.add_argument("--ack-transcript-exact", action="store_true")
    args = parser.parse_args()

    asr_ok = args.ack_breeze_asr_25_cuda and args.ack_breeze_asr_25_transcript_pass
    if not (args.ack_human_listened or asr_ok) or not args.ack_transcript_exact:
        return fail("writing an exact transcript requires Breeze-ASR-25 transcript pass or human exception review, plus --ack-transcript-exact")

    wav = REFERENCE_DIR / f"{args.candidate}.wav"
    if not wav.exists() or not wav.name.startswith("prompt_ref_candidate_"):
        return fail(f"prompt reference WAV missing or invalid: {wav}")

    if args.from_file:
        source = Path(args.from_file)
        if not source.exists():
            return fail(f"transcript source file missing: {source}")
        text = source.read_text(encoding="utf-8").strip()
    else:
        text = args.text.strip()
    if not text:
        return fail("exact transcript text is empty")

    lowered = text.lower()
    for marker in BLOCKED:
        if marker in lowered:
            return fail("transcript still looks provisional", f"blocked marker: {marker}")

    out = REFERENCE_DIR / f"{args.candidate}.exact-transcript.txt"
    if out.exists() and not args.overwrite:
        return fail(f"exact transcript already exists; use --overwrite only after intentional re-review: {out}")
    out.write_text(text + "\n", encoding="utf-8")
    print(f"PASS: wrote exact transcript for {args.candidate}")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
