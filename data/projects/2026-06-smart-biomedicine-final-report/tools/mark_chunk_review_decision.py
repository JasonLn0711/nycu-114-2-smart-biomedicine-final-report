#!/usr/bin/env python3
"""Record an ASR-led review decision for one generated narration chunk."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CHUNKS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks"
DECISIONS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/chunk-decisions"


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


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
        raise RuntimeError(probe.stdout)
    return probe.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-id", required=True)
    parser.add_argument("--decision", required=True, choices=["accepted", "rejected"])
    parser.add_argument("--chunks-dir", type=Path, default=CHUNKS_DIR)
    parser.add_argument("--decisions-dir", type=Path, default=DECISIONS_DIR)
    parser.add_argument("--engine-label", default="GPT-SoVITS")
    parser.add_argument("--notes", default="")
    parser.add_argument("--ack-human-listened", action="store_true")
    parser.add_argument("--ack-breeze-asr-25-cuda", action="store_true")
    parser.add_argument("--ack-breeze-asr-25-transcript-pass", action="store_true")
    parser.add_argument("--ack-transcript-matches-source", action="store_true")
    parser.add_argument("--require-semantic-sweep", action="store_true")
    parser.add_argument("--ack-semantic-sweep", action="store_true")
    parser.add_argument("--ack-repair-plan-created", action="store_true")
    parser.add_argument("--ack-no-missing-words", action="store_true")
    parser.add_argument("--ack-no-repeats", action="store_true")
    parser.add_argument("--ack-pronunciation-ok", action="store_true")
    parser.add_argument("--ack-no-artifacts", action="store_true")
    parser.add_argument("--ack-volume-ok", action="store_true")
    parser.add_argument("--ack-stitch-ok", action="store_true")
    args = parser.parse_args()

    chunks_dir = args.chunks_dir
    decisions_dir = args.decisions_dir
    wav = chunks_dir / f"{args.chunk_id}.wav"
    if not wav.exists():
        return fail(f"formal chunk WAV missing: {wav}")

    human_accept_flags = [
        ("human_listened", args.ack_human_listened),
        ("no_missing_words", args.ack_no_missing_words),
        ("no_repeats", args.ack_no_repeats),
        ("pronunciation_ok", args.ack_pronunciation_ok),
        ("no_artifacts", args.ack_no_artifacts),
        ("volume_ok", args.ack_volume_ok),
        ("stitch_ok", args.ack_stitch_ok),
    ]
    asr_accept_flags = [
        ("breeze_asr_25_cuda", args.ack_breeze_asr_25_cuda),
        ("breeze_asr_25_transcript_pass", args.ack_breeze_asr_25_transcript_pass),
        ("transcript_matches_source", args.ack_transcript_matches_source),
    ]
    if args.decision == "accepted":
        human_accept_ok = all(ok for _, ok in human_accept_flags)
        asr_accept_ok = all(ok for _, ok in asr_accept_flags)
        if not (asr_accept_ok or human_accept_ok):
            missing = [name for name, ok in asr_accept_flags if not ok]
            return fail(
                "accepted decision requires Breeze-ASR-25 transcript gate acknowledgements",
                "missing: " + ", ".join(missing),
            )
        if args.require_semantic_sweep and not args.ack_semantic_sweep:
            return fail("accepted decision requires semantic sweep acknowledgement")
    if args.decision == "rejected" and not (args.ack_breeze_asr_25_cuda or args.ack_human_listened):
        return fail("rejected decision requires evidence source acknowledgement: Breeze-ASR-25 CUDA or human listening")

    try:
        facts = ffprobe_facts(wav)
    except RuntimeError as exc:
        return fail("could not inspect chunk WAV", str(exc))

    decisions_dir.mkdir(parents=True, exist_ok=True)
    suffix = "accepted" if args.decision == "accepted" else "rejected"
    out = decisions_dir / f"{args.chunk_id}.{suffix}.md"

    if args.decision == "accepted":
        rejected = decisions_dir / f"{args.chunk_id}.rejected.md"
        if rejected.exists():
            rejected.unlink()
    else:
        accepted = decisions_dir / f"{args.chunk_id}.accepted.md"
        if accepted.exists():
            accepted.unlink()

    out.write_text(
        "\n".join(
            [
                f"# {args.engine_label} Chunk Review Decision - {args.chunk_id}",
                "",
                f"- created_at: `{datetime.now().isoformat(timespec='seconds')}`",
                f"- chunk_id: `{args.chunk_id}`",
                f"- decision: `{args.decision}`",
                f"- wav: `{wav}`",
                f"- notes: `{args.notes}`",
                "",
                "## QA Acknowledgements",
                "",
                *[f"- {name}: `{str(ok).lower()}`" for name, ok in asr_accept_flags],
                f"- semantic_sweep_required: `{str(args.require_semantic_sweep).lower()}`",
                f"- semantic_sweep: `{str(args.ack_semantic_sweep).lower()}`",
                f"- repair_plan_created: `{str(args.ack_repair_plan_created).lower()}`",
                *[f"- {name}: `{str(ok).lower()}`" for name, ok in human_accept_flags],
                "",
                "## WAV Facts",
                "",
                "```text",
                facts,
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"PASS: recorded {args.decision} decision for {args.chunk_id}")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
