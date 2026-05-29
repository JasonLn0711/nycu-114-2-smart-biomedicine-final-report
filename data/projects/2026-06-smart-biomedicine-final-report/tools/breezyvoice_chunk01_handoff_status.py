#!/usr/bin/env python3
"""Print the chunk 01 source, handoff, and gate status before RTX 5080 work."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
PREFLIGHT = PROJECT / "tools/breezyvoice_chunk01_preflight.py"
HANDOFF = PROJECT / "tools/print_breezyvoice_chunk01_handoff.py"
SEMANTIC_COMMAND = PROJECT / "tools/print_breezyvoice_chunk01_semantic_command.py"
STATUS = PROJECT / "tools/breezyvoice_audio_gate_status.py"


def run_section(title: str, cmd: list[str]) -> int:
    print(f"## {title}", flush=True)
    print(" ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    print(result.stdout.strip())
    print()
    return result.returncode


def main() -> int:
    failures = 0
    failures += int(run_section("Chunk 01 Source-Only Preflight", ["python3", str(PREFLIGHT), "--source-only"]) != 0)
    failures += int(run_section("Guarded RTX 5080 Handoff Command", ["python3", str(HANDOFF)]) != 0)
    failures += int(run_section("Post-ASR Semantic Review Command", ["python3", str(SEMANTIC_COMMAND)]) != 0)
    failures += int(run_section("BreezyVoice Gate Status", ["python3", str(STATUS)]) != 0)
    if failures:
        print("FAIL: chunk 01 handoff status has failing checks", file=sys.stderr)
        return 1
    print("PASS: chunk 01 source and handoff status are ready for the RTX 5080 route command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
