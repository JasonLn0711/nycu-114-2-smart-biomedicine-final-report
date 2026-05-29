#!/usr/bin/env python3
"""Print the post-ASR semantic review command for BreezyVoice chunk 01."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
ASR_REPORT = ROOT / "exports/smart-biomedicine-breezyvoice/qa/chunk-asr/sbm_tts_01_opening.asr-qa.md"
SEMANTIC_SWEEP = PROJECT / "tools/mark_breezyvoice_chunk01_semantic_sweep.py"
SEMANTIC_WRAPPER = PROJECT / "tools/mark_breezyvoice_chunk01_semantic_sweep.py"


def semantic_required_phrases() -> list[str]:
    spec = importlib.util.spec_from_file_location("breezyvoice_chunk01_semantic_wrapper", SEMANTIC_WRAPPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load semantic wrapper: {SEMANTIC_WRAPPER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["breezyvoice_chunk01_semantic_wrapper"] = module
    spec.loader.exec_module(module)
    return list(module.REQUIRED_PHRASES)


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fenced_section(text: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\n\n```text\n(.*?)\n```"
    match = re.search(pattern, text, flags=re.DOTALL | re.MULTILINE)
    return match.group(1).strip() if match else ""


def report_field(text: str, field: str) -> str:
    match = re.search(rf"^-\s+{re.escape(field)}:\s+`([^`]*)`", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def asr_status(required_phrases: list[str]) -> tuple[str, list[str], list[str]]:
    if not ASR_REPORT.exists():
        return "TODO", [f"ASR report missing: {ASR_REPORT}"], []

    report = ASR_REPORT.read_text(encoding="utf-8")
    gate_status = report_field(report, "gate_status") or "unknown"
    missing_critical = report_field(report, "missing_critical") or "unknown"
    observed_ratio = report_field(report, "observed_ratio") or "unknown"
    transcript = fenced_section(report, "Normalized ASR Transcript")
    normalized = normalize(transcript)
    missing_required = [
        phrase for phrase in required_phrases if normalize(phrase) not in normalized
    ]
    status = (
        "PASS"
        if gate_status == "pass" and missing_critical == "none" and not missing_required
        else "HOLD"
    )
    return status, [
        f"gate_status: {gate_status}",
        f"missing_critical: {missing_critical}",
        f"observed_ratio: {observed_ratio}",
        f"semantic_required_missing: {', '.join(missing_required) or 'none'}",
    ], missing_required


def main() -> int:
    required_phrases = semantic_required_phrases()
    status, details, missing_required = asr_status(required_phrases)
    print("# BreezyVoice chunk 01 semantic review command")
    print()
    print(f"- asr_report: `{ASR_REPORT}`")
    print(f"- asr_status: `{status}`")
    for detail in details:
        print(f"- {detail}")
    print()
    if status != "PASS":
        print("Do not run the semantic-sweep command yet. Run it only after the ASR report exists, passes, and contains all required semantic phrases.")
        print()
    print("## Required Semantic Phrases")
    print()
    for phrase in required_phrases:
        marker = "WAIT" if status == "TODO" else "TODO" if phrase in missing_required else "CHECK"
        print(f"- `{marker}` {phrase}")
    print()
    print("## Manual Review Checklist")
    print()
    print("- Clinical boundary is preserved.")
    print("- Human staff check / correction / rejection meaning is preserved.")
    print("- Clinician final authority is preserved.")
    print("- No autonomous diagnosis, priority scoring, or treatment recommendation is introduced.")
    print("- No meaning-changing medical wording error is present.")
    print()
    print("## Command")
    print()
    print("```bash")
    print(f"python3 {SEMANTIC_SWEEP.relative_to(ROOT)} \\")
    print("  --ack-clinical-boundary \\")
    print("  --ack-human-staff-check \\")
    print("  --ack-final-authority \\")
    print("  --ack-no-autonomous-medical-action \\")
    print("  --ack-no-meaning-changing-medical-error")
    print("```")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
