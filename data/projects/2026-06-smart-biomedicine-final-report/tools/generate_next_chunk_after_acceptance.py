#!/usr/bin/env python3
"""Generate one next GPT-SoVITS chunk only after the previous ASR gate is accepted."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from accepted_reference import resolve_accepted_reference


ROOT = Path(__file__).resolve().parents[4]
GENERATOR = ROOT / "data/projects/2026-06-smart-biomedicine-final-report/tools/generate_gptsovits_chunk.py"
CHUNKS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks"
DECISIONS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/chunk-decisions"

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


def accepted_marker(chunk_id: str) -> Path:
    return DECISIONS_DIR / f"{chunk_id}.accepted.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-id", required=True, choices=CHUNK_IDS[1:])
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    idx = CHUNK_IDS.index(args.chunk_id)
    previous = CHUNK_IDS[idx - 1]
    previous_wav = CHUNKS_DIR / f"{previous}.wav"
    current_wav = CHUNKS_DIR / f"{args.chunk_id}.wav"

    if not previous_wav.exists():
        return fail(f"previous chunk WAV missing: {previous_wav}")
    if not accepted_marker(previous).exists():
        return fail(
            f"previous chunk is not accepted: {previous}",
            f"expected marker: {accepted_marker(previous)}",
        )
    if current_wav.exists() and not args.overwrite:
        return fail(f"target chunk already exists; use --overwrite only after intentional rejection: {current_wav}")
    try:
        accepted = resolve_accepted_reference()
    except RuntimeError as exc:
        return fail("accepted reference is not ready", str(exc))

    cmd = [
        "python3",
        str(GENERATOR),
        "--chunk-id",
        args.chunk_id,
        "--ref-audio",
        str(accepted.wav),
        "--ref-text",
        str(accepted.exact_transcript),
    ]
    gen = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if gen.returncode != 0:
        return fail("next chunk generation failed", gen.stdout)
    print(gen.stdout.strip())
    print(f"accepted_reference={accepted.stem}")
    print(f"Next gate: run Breeze-ASR-25 transcript gate for {current_wav}.")
    print(
        "python3 data/projects/2026-06-smart-biomedicine-final-report/tools/chunk_asr_qa.py "
        f"--chunk-id {args.chunk_id} --language en --gate --auto-decision"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
