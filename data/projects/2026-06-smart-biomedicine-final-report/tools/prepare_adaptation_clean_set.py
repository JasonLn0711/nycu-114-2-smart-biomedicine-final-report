#!/usr/bin/env python3
"""Prepare a 45-90s fallback reference review set for GPT-SoVITS adaptation.

The output is intentionally marked as a review candidate. It is not accepted
production material until the included segments have been human-listened and
transcribed exactly.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/reference"
OUT_DIR = REFERENCE_DIR / "adaptation-clean-set-v1"
OUT_WAV = OUT_DIR / "adaptation_clean_set_v1_review_only.wav"
OUT_MANIFEST = OUT_DIR / "adaptation_clean_set_v1_review_only.md"
SEGMENTS = [
    REFERENCE_DIR / "ref_candidate_01_000009_12s.wav",
    REFERENCE_DIR / "ref_candidate_02_000036_12s.wav",
    REFERENCE_DIR / "ref_candidate_03_000072_12s.wav",
    REFERENCE_DIR / "ref_candidate_04_000381_12s.wav",
]


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def duration(path: Path) -> float:
    probe = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)])
    if probe.returncode != 0:
        raise RuntimeError(probe.stdout)
    return float(probe.stdout.strip())


def main() -> int:
    missing = [str(path) for path in SEGMENTS if not path.exists()]
    if missing:
        raise SystemExit("missing source segments:\n" + "\n".join(missing))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        concat = Path(tmp) / "concat.txt"
        lines = []
        for segment in SEGMENTS:
            lines.append(f"file '{segment.resolve()}'")
        concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
        ffmpeg = run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat),
                "-ac",
                "1",
                "-ar",
                "16000",
                "-sample_fmt",
                "s16",
                str(OUT_WAV),
            ]
        )
        if ffmpeg.returncode != 0:
            raise SystemExit(ffmpeg.stdout)

    total = duration(OUT_WAV)
    if not 45.0 <= total <= 90.0:
        raise SystemExit(f"fallback review set must be 45-90s; got {total:.2f}s")

    OUT_MANIFEST.write_text(
        "\n".join(
            [
                "# Adaptation Clean Set v1 - Review Only",
                "",
                f"- wav: `{OUT_WAV}`",
                f"- duration_seconds: `{total:.2f}`",
                "- status: `review_only_pending_human_listening_and_exact_transcript`",
                "- purpose: fallback material if zero-shot prompt-mode voice identity is unstable.",
                "",
                "## Included Segments",
                "",
                *[f"- `{segment}`" for segment in SEGMENTS],
                "",
                "## Production Gate",
                "",
                "- Do not use this set for production until every included segment is human-listened.",
                "- Do not use this set if any included segment has clipping, laughter, long pauses, unstable mic distance, or transcript mismatch.",
                "- Create an exact transcript bundle before adaptation use.",
                "- Keep this as fallback only; prompt-mode chunk 01 acceptance remains the primary path.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(OUT_WAV)
    print(OUT_MANIFEST)
    print(f"duration={total:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
