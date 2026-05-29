#!/usr/bin/env python3
"""Register Jason-recorded opening/closing fallback audio as a formal chunk WAV.

This is only for the planned fallback path: real voice for chunk 01 and/or
chunk 14 when GPT-SoVITS sounds unstable. The script converts the source to a
WAV master and writes a fallback manifest, but it does not mark the chunk as
accepted. Human chunk QA is still required through mark_chunk_review_decision.py.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CHUNKS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks"
FALLBACK_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/fallback-chunks"
ALLOWED = {
    "sbm_tts_01_opening": "opening",
    "sbm_tts_14_closing": "closing",
}


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def ffprobe_facts(path: Path) -> str:
    probe = run(
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
        ]
    )
    if probe.returncode != 0:
        raise RuntimeError(probe.stdout)
    return probe.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-id", required=True, choices=sorted(ALLOWED))
    parser.add_argument("--source-audio", required=True, help="Jason-recorded fallback audio file.")
    parser.add_argument("--notes", default="")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--ack-own-voice", action="store_true")
    parser.add_argument("--ack-recorded-for-this-report", action="store_true")
    parser.add_argument("--ack-content-matches-chunk", action="store_true")
    parser.add_argument("--ack-no-private-content", action="store_true")
    args = parser.parse_args()

    required = [
        ("own_voice", args.ack_own_voice),
        ("recorded_for_this_report", args.ack_recorded_for_this_report),
        ("content_matches_chunk", args.ack_content_matches_chunk),
        ("no_private_content", args.ack_no_private_content),
    ]
    missing = [name for name, ok in required if not ok]
    if missing:
        return fail("fallback registration requires all acknowledgement flags", "missing: " + ", ".join(missing))

    source = Path(args.source_audio).expanduser().resolve()
    if not source.exists():
        return fail(f"source audio missing: {source}")

    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    FALLBACK_DIR.mkdir(parents=True, exist_ok=True)
    out = CHUNKS_DIR / f"{args.chunk_id}.wav"
    manifest = FALLBACK_DIR / f"{args.chunk_id}.fallback.md"
    if out.exists() and not args.overwrite:
        return fail(f"target chunk already exists; use --overwrite only after intentional replacement: {out}")

    convert = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-ac",
            "1",
            "-ar",
            "32000",
            "-sample_fmt",
            "s16",
            str(out),
        ]
    )
    if convert.returncode != 0:
        return fail("ffmpeg conversion failed", convert.stdout)

    try:
        facts = ffprobe_facts(out)
    except RuntimeError as exc:
        return fail("could not inspect fallback WAV", str(exc))

    manifest.write_text(
        "\n".join(
            [
                f"# Human Fallback Chunk - {args.chunk_id}",
                "",
                f"- created_at: `{datetime.now().isoformat(timespec='seconds')}`",
                f"- chunk_id: `{args.chunk_id}`",
                f"- fallback_role: `{ALLOWED[args.chunk_id]}`",
                f"- source_audio: `{source}`",
                f"- output_wav: `{out}`",
                f"- notes: `{args.notes}`",
                "- status: `registered_pending_human_chunk_QA`",
                "",
                "## Acknowledgements",
                "",
                *[f"- {name}: `{str(ok).lower()}`" for name, ok in required],
                "",
                "## WAV Facts",
                "",
                "```text",
                facts,
                "```",
                "",
                "## Next Gate",
                "",
                "Run `mark_chunk_review_decision.py` after listening. Registration is not acceptance.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"PASS: registered human fallback chunk {args.chunk_id}")
    print(out)
    print(manifest)
    print("Next gate: human-listen the fallback chunk and record accepted/rejected chunk decision.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
