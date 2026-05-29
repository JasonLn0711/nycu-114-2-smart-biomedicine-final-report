#!/usr/bin/env python3
"""Report basic WAV loudness consistency for accepted GPT-SoVITS chunks."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CHUNKS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks"
REPORT = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/audio-loudness-report.md"
CHUNK_IDS = [
    "sbm_tts_01_opening",
    "sbm_tts_02_markdown_format",
    "sbm_tts_03_definitions",
    "sbm_tts_04_workflow_problem",
    "sbm_tts_05_speech_to_summary",
    "sbm_tts_06_evidence_landscape",
    "sbm_tts_07_hager_boundary",
    "sbm_tts_08_lang1_overview",
    "sbm_tts_09_lang1_results",
    "sbm_tts_10_architecture",
    "sbm_tts_11_scope_controls",
    "sbm_tts_12_synthetic_example",
    "sbm_tts_13_validation_risk",
    "sbm_tts_14_closing",
]


@dataclass
class Loudness:
    path: Path
    mean_db: float | None
    max_db: float | None


def volumedetect(path: Path) -> Loudness:
    run = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    text = run.stdout
    mean_match = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", text)
    max_match = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", text)
    return Loudness(
        path=path,
        mean_db=float(mean_match.group(1)) if mean_match else None,
        max_db=float(max_match.group(1)) if max_match else None,
    )


def mark(ok: bool) -> str:
    return "PASS" if ok else "TODO"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks-dir", default=str(CHUNKS_DIR))
    parser.add_argument("--output", default=str(REPORT))
    parser.add_argument("--max-mean-spread-db", type=float, default=4.0)
    args = parser.parse_args()

    chunks_dir = Path(args.chunks_dir)
    existing = [chunks_dir / f"{chunk_id}.wav" for chunk_id in CHUNK_IDS if (chunks_dir / f"{chunk_id}.wav").exists()]
    rows = [volumedetect(path) for path in existing]
    means = [row.mean_db for row in rows if row.mean_db is not None]
    spread = max(means) - min(means) if means else None
    ok = len(existing) == len(CHUNK_IDS) and spread is not None and spread <= args.max_mean_spread_db

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Audio Loudness Gate",
        "",
        f"- chunks_found: `{len(existing)}/14`",
        f"- max_allowed_mean_spread_db: `{args.max_mean_spread_db:.1f}`",
        f"- measured_mean_spread_db: `{spread:.2f}`" if spread is not None else "- measured_mean_spread_db: `TODO`",
        f"- status: `{mark(ok)}`",
        "",
        "| Chunk WAV | Mean volume | Max volume |",
        "| --- | ---: | ---: |",
    ]
    for row in rows:
        mean = f"{row.mean_db:.1f} dB" if row.mean_db is not None else "TODO"
        max_volume = f"{row.max_db:.1f} dB" if row.max_db is not None else "TODO"
        lines.append(f"| `{row.path.name}` | `{mean}` | `{max_volume}` |")
    lines.append("")
    if not existing:
        lines.append("Next action: generate and accept chunks before loudness balancing.")
    elif len(existing) < len(CHUNK_IDS):
        lines.append("Next action: continue one-chunk generation and review before final loudness gate.")
    elif not ok:
        lines.append("Next action: normalize or re-render outlier chunks before stitching.")
    else:
        lines.append("Next action: stitch accepted chunks and check boundaries.")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)
    print(f"status={mark(ok)} chunks={len(existing)}/14")
    return 0 if ok or len(existing) < len(CHUNK_IDS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
