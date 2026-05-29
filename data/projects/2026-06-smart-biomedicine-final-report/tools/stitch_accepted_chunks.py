#!/usr/bin/env python3
"""Stitch accepted narration WAV chunks with silence between chunks.

The script refuses to run unless all expected chunk WAVs exist. It keeps WAV as
the master output and uses ffmpeg for deterministic stitching.
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CHUNKS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks"
DECISIONS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/chunk-decisions"
OUT = ROOT / "exports/smart-biomedicine-gpt-sovits/stitching/smart-biomedicine-final-report-narration-v1.wav"
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


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def wav_params(path: Path) -> tuple[int, int, int]:
    with wave.open(str(path), "rb") as wav:
        return wav.getframerate(), wav.getnchannels(), wav.getsampwidth()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks-dir", default=str(CHUNKS_DIR))
    parser.add_argument("--decisions-dir", default=str(DECISIONS_DIR))
    parser.add_argument("--semantic-sweep-dir", default="")
    parser.add_argument("--output", default=str(OUT))
    parser.add_argument("--silence", type=float, default=0.5, help="Silence between chunks in seconds.")
    parser.add_argument("--require-semantic-sweep", action="store_true")
    args = parser.parse_args()

    if not 0.35 <= args.silence <= 0.7:
        raise SystemExit("--silence must be between 0.35 and 0.7 seconds")

    chunks_dir = Path(args.chunks_dir)
    decisions_dir = Path(args.decisions_dir)
    semantic_sweep_dir = Path(args.semantic_sweep_dir) if args.semantic_sweep_dir else None
    output = Path(args.output)
    paths = [chunks_dir / f"{chunk_id}.wav" for chunk_id in CHUNK_IDS]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise SystemExit("missing chunk WAVs; refusing stitch before all chunks are accepted:\n" + "\n".join(missing))
    missing_acceptance = [
        str(decisions_dir / f"{chunk_id}.accepted.md")
        for chunk_id in CHUNK_IDS
        if not (decisions_dir / f"{chunk_id}.accepted.md").exists()
    ]
    if missing_acceptance:
        raise SystemExit(
            "missing accepted QA markers; refusing stitch before Breeze-ASR-25 transcript acceptance:\n"
            + "\n".join(missing_acceptance)
        )
    if args.require_semantic_sweep:
        if semantic_sweep_dir is None:
            raise SystemExit("--require-semantic-sweep requires --semantic-sweep-dir")
        missing_sweeps = [
            str(semantic_sweep_dir / f"{chunk_id}.semantic-sweep.md")
            for chunk_id in CHUNK_IDS
            if not (semantic_sweep_dir / f"{chunk_id}.semantic-sweep.md").exists()
        ]
        if missing_sweeps:
            raise SystemExit(
                "missing semantic-sweep markers; refusing stitch before manual semantic acceptance:\n"
                + "\n".join(missing_sweeps)
            )
    sample_rates = {wav_params(path)[0] for path in paths}
    channels = {wav_params(path)[1] for path in paths}
    sample_widths = {wav_params(path)[2] for path in paths}
    if len(sample_rates) != 1 or len(channels) != 1 or len(sample_widths) != 1:
        raise SystemExit("chunk WAV formats are inconsistent; normalize or re-render before stitching")
    sample_rate = sample_rates.pop()
    channel_layout = "mono" if channels.pop() == 1 else "stereo"

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        silence = tmpdir / "silence.wav"
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"anullsrc=r={sample_rate}:cl={channel_layout}",
                "-t",
                str(args.silence),
                "-sample_fmt",
                "s16",
                str(silence),
            ],
            check=True,
        )
        concat = tmpdir / "concat.txt"
        lines = []
        for idx, path in enumerate(paths):
            lines.append(f"file '{path.resolve()}'")
            if idx != len(paths) - 1:
                lines.append(f"file '{silence.resolve()}'")
        concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat),
                "-c",
                "copy",
                str(output),
            ],
            check=True,
        )

    total = sum(wav_duration(p) for p in paths) + args.silence * (len(paths) - 1)
    print(f"stitched {len(paths)} chunks -> {output}")
    print(f"estimated duration: {total:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
