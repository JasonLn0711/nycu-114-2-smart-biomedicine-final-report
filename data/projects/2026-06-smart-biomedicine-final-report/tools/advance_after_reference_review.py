#!/usr/bin/env python3
"""Advance from ASR-accepted reference review to formal chunk 01 generation.

This helper chains the guarded steps after the exact transcript exists and the
caller explicitly acknowledges the reference review conditions.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from accepted_reference import resolve_accepted_reference


ROOT = Path(__file__).resolve().parents[4]
TOOLS = ROOT / "data/projects/2026-06-smart-biomedicine-final-report/tools"
REFERENCE_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/reference"
CHUNK01 = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_01_opening.wav"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", default="prompt_ref_candidate_04_000381_8p00s")
    parser.add_argument("--accept-reference", action="store_true", help="Record accepted marker before generation.")
    parser.add_argument("--notes", default="")
    parser.add_argument("--overwrite-chunk01", action="store_true")
    parser.add_argument("--ack-human-listened", action="store_true")
    parser.add_argument("--ack-breeze-asr-25-cuda", action="store_true")
    parser.add_argument("--ack-breeze-asr-25-transcript-pass", action="store_true")
    parser.add_argument("--ack-transcript-matches-reference", action="store_true")
    parser.add_argument("--ack-own-voice-authorized", action="store_true")
    parser.add_argument("--ack-3-to-10s", action="store_true")
    parser.add_argument("--ack-clean-audio", action="store_true")
    parser.add_argument("--ack-no-heavy-filler", action="store_true")
    parser.add_argument("--ack-no-clipping", action="store_true")
    parser.add_argument("--ack-transcript-exact", action="store_true")
    args = parser.parse_args()

    ref_exact = REFERENCE_DIR / f"{args.candidate}.exact-transcript.txt"
    if not ref_exact.exists():
        return fail(
            "exact transcript is missing",
            f"Create this after human listening first:\n{ref_exact}",
        )

    if args.accept_reference:
        accept_cmd = [
            "python3",
            str(TOOLS / "mark_reference_review_decision.py"),
            "--candidate",
            args.candidate,
            "--decision",
            "accepted",
            "--exact-transcript",
            str(ref_exact),
            "--notes",
            args.notes,
        ]
        for flag in [
            "ack-human-listened",
            "ack-breeze-asr-25-cuda",
            "ack-breeze-asr-25-transcript-pass",
            "ack-transcript-matches-reference",
            "ack-own-voice-authorized",
            "ack-3-to-10s",
            "ack-clean-audio",
            "ack-no-heavy-filler",
            "ack-no-clipping",
            "ack-transcript-exact",
        ]:
            if getattr(args, flag.replace("-", "_")):
                accept_cmd.append(f"--{flag}")
        accept = run(accept_cmd)
        if accept.returncode != 0:
            return fail("reference acceptance failed", accept.stdout)
        print(accept.stdout.strip())

    try:
        accepted = resolve_accepted_reference()
    except RuntimeError as exc:
        return fail("accepted reference marker is missing or ambiguous", str(exc))
    if accepted.stem != args.candidate:
        return fail("accepted reference does not match requested candidate", f"accepted={accepted.stem}; requested={args.candidate}")

    if CHUNK01.exists() and not args.overwrite_chunk01:
        return fail(f"formal chunk 01 already exists; use --overwrite-chunk01 only after intentional rejection: {CHUNK01}")

    for tool in [
        "reference_transcript_gate_status.py",
        "term_consistency_gate.py",
        "gptsovits_gpu_asr_preflight.py",
        "run_formal_chunk01_after_transcript.py",
        "gptsovits_audio_gate_status.py",
    ]:
        step = run(["python3", str(TOOLS / tool)])
        if step.returncode != 0:
            return fail(f"{tool} failed", step.stdout)
        print(f"\n## {tool}")
        print(step.stdout.strip())

    print("\nPASS: reference accepted and formal chunk 01 generation path completed")
    print(CHUNK01)
    print("Next gate: run Breeze-ASR-25 transcript gate for chunk 01, then accept or repair the chunk.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
