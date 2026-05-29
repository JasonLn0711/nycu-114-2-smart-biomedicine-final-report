#!/usr/bin/env python3
"""Self-check repaired BreezyVoice chunk 01 source and ASR gate rules.

This check is intentionally no-GPU. It verifies the local source and phrase
detectors before the real RTX 5080 synthesis and Breeze-ASR-25 CUDA run.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
PREFLIGHT_PATH = PROJECT / "tools/breezyvoice_chunk01_preflight.py"
ASR_GATE_PATH = PROJECT / "tools/chunk_asr_qa.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module spec: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    preflight = load_module(PREFLIGHT_PATH, "breezyvoice_chunk01_preflight_for_check")
    asr_gate = load_module(ASR_GATE_PATH, "chunk_asr_qa_for_check")

    source = preflight.source_text(preflight.SOURCE, preflight.CHUNK_ID)
    if not source:
        return fail(f"chunk source missing: {preflight.CHUNK_ID}")

    missing_required = [
        phrase
        for phrase in preflight.REQUIRED_PHRASES
        if phrase.lower() not in source.lower()
    ]
    present_unstable = [
        phrase
        for phrase in preflight.UNSTABLE_PHRASES
        if phrase.lower() in source.lower()
    ]
    if missing_required:
        return fail("chunk 01 source is missing required repaired phrases: " + ", ".join(missing_required))
    if present_unstable:
        return fail("chunk 01 source still contains unstable phrases: " + ", ".join(present_unstable))

    clean = asr_gate.token_comparison(source, source)
    if clean["missing_critical"]:
        return fail("clean source comparison unexpectedly misses critical phrases: " + ", ".join(clean["missing_critical"]))

    degraded = (
        source.replace("Human staff check the draft", "Human staff use the draft")
        .replace("The draft is checked before any care decision", "The draft is checked before any tear decision")
        .replace("I am not asking the system to make a diagnosis", "I am asking the system to make a diagnosis")
        .replace("The doctor makes the medical decision", "The doctor makes a simple decision")
    )
    degraded_result = asr_gate.token_comparison(source, degraded)
    expected_catches = {
        "human staff check the draft",
        "the draft is checked before any care decision",
        "not asking the system to make a diagnosis",
        "the doctor makes the medical decision",
    }
    missing_catches = expected_catches.difference(degraded_result["missing_critical"])
    if missing_catches:
        return fail("ASR critical detector missed degraded boundary phrases: " + ", ".join(sorted(missing_catches)))

    print("PASS: BreezyVoice chunk 01 source and ASR gate rules are self-consistent")
    print(f"source_text_characters={len(source)}")
    print("missing_required_phrases=none")
    print("present_unstable_phrases=none")
    print("degraded_boundary_phrases_caught=" + ", ".join(sorted(expected_catches)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
