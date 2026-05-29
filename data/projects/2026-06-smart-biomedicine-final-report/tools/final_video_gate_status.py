#!/usr/bin/env python3
"""Check final video candidate runtime and basic media properties."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_EXPORT_ROOT = ROOT / "exports/smart-biomedicine-gpt-sovits"
EXTS = {".mp4", ".mov", ".mkv", ".webm"}


def probe(path: Path) -> dict:
    run = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size",
            "-show_streams",
            "-of",
            "json",
            str(path),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if run.returncode != 0:
        return {"error": run.stdout.strip()}
    return json.loads(run.stdout)


def media_summary(path: Path) -> tuple[bool, str]:
    data = probe(path)
    if "error" in data:
        return False, data["error"]
    duration = float(data.get("format", {}).get("duration", 0.0))
    streams = data.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    width = int(video_streams[0].get("width", 0)) if video_streams else 0
    height = int(video_streams[0].get("height", 0)) if video_streams else 0
    duration_ok = 19 * 60 <= duration <= 20 * 60
    resolution_ok = width >= 1920 and height >= 1080
    ok = duration_ok and resolution_ok and bool(audio_streams)
    summary = (
        f"duration={duration:.2f}s; resolution={width}x{height}; "
        f"audio_streams={len(audio_streams)}; duration_19_20m={duration_ok}; "
        f"resolution_1080p={resolution_ok}"
    )
    return ok, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--export-root",
        type=Path,
        default=DEFAULT_EXPORT_ROOT,
        help="Generated artifact root that contains video/ and qa/ directories.",
    )
    args = parser.parse_args()

    video_dir = args.export_root / "video"
    out = args.export_root / "qa/final-video-gate-status.md"
    candidates = sorted(path for path in video_dir.glob("*") if path.suffix.lower() in EXTS) if video_dir.exists() else []
    lines = [
        "# Final Video Gate Status",
        "",
        "Expected output: local final video candidate, `19-20` minutes, at least `1080p` if possible, with audio present.",
        "",
        "| Candidate | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    passing = 0
    if not candidates:
        lines.append(f"| `(none)` | `TODO` | Put final video under `{video_dir}/` before upload. |")
    for path in candidates:
        ok, summary = media_summary(path)
        passing += int(ok)
        lines.append(f"| `{path}` | `{'PASS' if ok else 'TODO'}` | {summary} |")
    lines.extend(["", f"Passing candidates: `{passing}/{len(candidates)}`", ""])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)
    print(f"passing={passing}/{len(candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
