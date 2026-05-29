#!/usr/bin/env python3
"""Record an ASR-led review decision for a GPT-SoVITS prompt reference."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/reference"
DECISIONS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-decisions"


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def wav_duration(path: Path) -> float:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if probe.returncode != 0:
        raise RuntimeError(probe.stdout)
    return float(probe.stdout.strip())


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
    parser.add_argument("--candidate", required=True, help="Prompt reference stem or WAV path.")
    parser.add_argument("--decision", required=True, choices=["accepted", "rejected"])
    parser.add_argument("--exact-transcript", default="", help="Exact transcript path for accepted references.")
    parser.add_argument("--notes", default="")
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

    candidate = Path(args.candidate)
    wav = candidate if candidate.suffix == ".wav" else REFERENCE_DIR / f"{args.candidate}.wav"
    wav = wav.resolve()
    if not wav.exists():
        return fail(f"reference WAV missing: {wav}")
    if not wav.name.startswith("prompt_ref_candidate_"):
        return fail("only prompt-ready 3-10s reference WAV files can be accepted for production")

    try:
        duration = wav_duration(wav)
        facts = ffprobe_facts(wav)
    except RuntimeError as exc:
        return fail("could not inspect reference WAV", str(exc))

    if args.decision == "rejected" and not (args.ack_human_listened or args.ack_breeze_asr_25_cuda):
        return fail("rejected reference requires Breeze-ASR-25 CUDA evidence or human exception review")

    human_accept_flags = [
        ("human_listened", args.ack_human_listened),
        ("own_voice_authorized", args.ack_own_voice_authorized),
        ("three_to_ten_seconds", args.ack_3_to_10s),
        ("clean_audio", args.ack_clean_audio),
        ("no_heavy_filler", args.ack_no_heavy_filler),
        ("no_clipping", args.ack_no_clipping),
        ("transcript_exact", args.ack_transcript_exact),
    ]
    asr_accept_flags = [
        ("breeze_asr_25_cuda", args.ack_breeze_asr_25_cuda),
        ("breeze_asr_25_transcript_pass", args.ack_breeze_asr_25_transcript_pass),
        ("transcript_matches_reference", args.ack_transcript_matches_reference),
        ("own_voice_authorized", args.ack_own_voice_authorized),
        ("three_to_ten_seconds", args.ack_3_to_10s),
        ("transcript_exact", args.ack_transcript_exact),
    ]

    exact_transcript = Path(args.exact_transcript).resolve() if args.exact_transcript else REFERENCE_DIR / f"{wav.stem}.exact-transcript.txt"
    transcript_text = ""
    if args.decision == "accepted":
        human_accept_ok = all(ok for _, ok in human_accept_flags)
        asr_accept_ok = all(ok for _, ok in asr_accept_flags)
        if not (asr_accept_ok or human_accept_ok):
            missing = [name for name, ok in asr_accept_flags if not ok]
            return fail("accepted reference requires Breeze-ASR-25 transcript gate acknowledgements", "missing: " + ", ".join(missing))
        if not 3.0 <= duration <= 10.0:
            return fail(f"accepted reference must be 3-10 seconds; got {duration:.2f}s")
        if not exact_transcript.exists():
            return fail(f"exact transcript missing: {exact_transcript}")
        transcript_text = exact_transcript.read_text(encoding="utf-8").strip()
        lowered = exact_transcript.name.lower() + "\n" + transcript_text.lower()
        for marker in ["draft", "asr", "pending", "todo", "template", "<write exact transcript here>"]:
            if marker in lowered:
                return fail("exact transcript still looks provisional", f"remove marker `{marker}` before acceptance")
        if not transcript_text:
            return fail(f"exact transcript is empty: {exact_transcript}")

    DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "accepted" if args.decision == "accepted" else "rejected"
    out = DECISIONS_DIR / f"{wav.stem}.{suffix}.md"
    opposite = DECISIONS_DIR / f"{wav.stem}.{'rejected' if args.decision == 'accepted' else 'accepted'}.md"
    if opposite.exists():
        opposite.unlink()

    out.write_text(
        "\n".join(
            [
                f"# Reference Review Decision - {wav.stem}",
                "",
                f"- created_at: `{datetime.now().isoformat(timespec='seconds')}`",
                f"- candidate: `{wav.stem}`",
                f"- decision: `{args.decision}`",
                f"- wav: `{wav}`",
                f"- duration_seconds: `{duration:.3f}`",
                f"- exact_transcript: `{exact_transcript if args.decision == 'accepted' else ''}`",
                f"- notes: `{args.notes}`",
                "",
                "## QA Acknowledgements",
                "",
                *[f"- {name}: `{str(ok).lower()}`" for name, ok in asr_accept_flags],
                *[f"- {name}: `{str(ok).lower()}`" for name, ok in human_accept_flags],
                "",
                "## Transcript",
                "",
                "```text",
                transcript_text,
                "```",
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
    print(f"PASS: recorded {args.decision} reference decision for {wav.stem}")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
