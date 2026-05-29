#!/usr/bin/env python3
"""Record the manual semantic sweep for BreezyVoice chunk 01."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
GENERIC = ROOT / "data/projects/2026-06-smart-biomedicine-final-report/tools/mark_breezyvoice_chunk_semantic_sweep.py"
CHUNK_ID = "sbm_tts_01_opening"
REQUIRED_PHRASES = [
    "artificial intelligence to act like a doctor",
    "the draft is not final",
    "the draft is checked before any care decision",
    "human staff check the draft",
    "human staff can correct it",
    "human staff can reject it",
    "human staff check the screen",
    "the doctor keeps the final authority",
    "the doctor makes the medical decision",
    "not asking the system to make a diagnosis",
    "not proposing automatic scoring",
    "not deciding patient priority",
    "not proposing a treatment recommendation",
]


def main() -> int:
    cmd = [
        "python3",
        str(GENERIC),
        "--chunk-id",
        CHUNK_ID,
    ]
    for phrase in REQUIRED_PHRASES:
        cmd.extend(["--required-phrase", phrase])
    cmd.extend(sys.argv[1:])
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    print(result.stdout.strip())
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
