#!/usr/bin/env python3
"""Generate the next BreezyVoice chunk only after the previous chunk is accepted."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
GENERATOR = PROJECT / "tools/generate_breezyvoice_chunk.py"
SOURCE = PROJECT / "breezyvoice-narration-chunks-v1.md"
CHUNKS_DIR = ROOT / "exports/smart-biomedicine-breezyvoice/chunks"
DECISIONS_DIR = ROOT / "exports/smart-biomedicine-breezyvoice/qa/chunk-decisions"
SEMANTIC_SWEEP_DIR = ROOT / "exports/smart-biomedicine-breezyvoice/qa/semantic-sweeps"
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


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def source_has_chunk(chunk_id: str) -> bool:
    if not SOURCE.exists():
        return False
    text = SOURCE.read_text(encoding="utf-8")
    return bool(re.search(rf"^###\s+{re.escape(chunk_id)}\n", text, flags=re.MULTILINE))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-id", required=True, choices=CHUNK_IDS[1:])
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--required-gpu-name", default="RTX 5080")
    args = parser.parse_args()

    idx = CHUNK_IDS.index(args.chunk_id)
    previous = CHUNK_IDS[idx - 1]
    previous_wav = CHUNKS_DIR / f"{previous}.wav"
    previous_accepted = DECISIONS_DIR / f"{previous}.accepted.md"
    previous_sweep = SEMANTIC_SWEEP_DIR / f"{previous}.semantic-sweep.md"
    current_wav = CHUNKS_DIR / f"{args.chunk_id}.wav"

    if not previous_wav.exists():
        return fail(f"previous BreezyVoice chunk WAV missing: {previous_wav}")
    if not previous_accepted.exists():
        return fail(
            f"previous BreezyVoice chunk is not accepted: {previous}",
            f"expected marker: {previous_accepted}",
        )
    if not previous_sweep.exists():
        return fail(
            f"previous BreezyVoice chunk lacks semantic sweep: {previous}",
            f"expected marker: {previous_sweep}",
        )
    if not source_has_chunk(args.chunk_id):
        return fail(
            f"BreezyVoice source text missing for {args.chunk_id}",
            f"add a repaired source section to {SOURCE} after {previous} is accepted",
        )
    if current_wav.exists() and not args.overwrite:
        return fail(f"target chunk already exists; use --overwrite only after intentional rejection: {current_wav}")

    cmd = [
        "python3",
        str(GENERATOR),
        "--chunk-id",
        args.chunk_id,
        "--required-gpu-name",
        args.required_gpu_name,
    ]
    if args.overwrite:
        cmd.append("--overwrite")
    gen = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if gen.returncode != 0:
        return fail("next BreezyVoice chunk generation failed", gen.stdout)
    print(gen.stdout.strip())
    print(f"Next gate: run Breeze-ASR-25 transcript gate for {current_wav}, then semantic sweep before advancing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
