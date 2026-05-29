#!/usr/bin/env python3
"""Print the current GPT-SoVITS audio-production gate status."""

from __future__ import annotations

from pathlib import Path

from accepted_reference import resolve_accepted_reference


ROOT = Path(__file__).resolve().parents[4]
REVIEW_HTML = ROOT / "exports/smart-biomedicine-gpt-sovits/review-packet/chunk01-reference-review/index.html"
REF_REVIEW_HTML = ROOT / "exports/smart-biomedicine-gpt-sovits/review-packet/reference-transcript-review/index.html"
HUMAN_GATE_DASHBOARD = ROOT / "exports/smart-biomedicine-gpt-sovits/review-packet/human-gate-dashboard/index.html"
REFERENCE_LISTENING_WORKBOOK = ROOT / "exports/smart-biomedicine-gpt-sovits/review-packet/reference-listening-workbook/index.html"
CHUNK_QA_WORKBOOK = ROOT / "exports/smart-biomedicine-gpt-sovits/review-packet/chunk-qa-workbook/index.html"
REFERENCE_DECISION_STATUS = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-decisions/reference-decision-status.md"
REF_QUALITY = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-quality/reference-quality-manifest.md"
REF_VISUAL_QC = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-visual-qc/reference-visual-qc.md"
ADAPTATION_SET = ROOT / "exports/smart-biomedicine-gpt-sovits/reference/adaptation-clean-set-v1/adaptation_clean_set_v1_review_only.wav"
REF_TRANSCRIPT_GATE = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-transcript-gate.md"
PROVENANCE = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/provenance/artifact-provenance-manifest.md"
DELIVERY = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/delivery-gate-status.md"
OBJECTIVE_AUDIT = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/production-objective-audit.md"
CHUNKS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks"
DECISIONS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/chunk-decisions"
REF_DECISIONS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-decisions"
STITCHED = ROOT / "exports/smart-biomedicine-gpt-sovits/stitching/smart-biomedicine-final-report-narration-v1.wav"
LOUDNESS = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/audio-loudness-report.md"
CHUNK_ASR_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/chunk-asr"

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


def mark(value: bool) -> str:
    return "PASS" if value else "TODO"


def main() -> int:
    try:
        accepted_ref = resolve_accepted_reference()
        accepted_ref_ok = True
        accepted_ref_text = f"{accepted_ref.stem} `{accepted_ref.marker}`"
    except RuntimeError as exc:
        accepted_ref = None
        accepted_ref_ok = False
        accepted_ref_text = str(exc)
    accepted_marker_count = len(list(REF_DECISIONS_DIR.glob("prompt_ref_candidate_*.accepted.md"))) if REF_DECISIONS_DIR.exists() else 0

    print("# GPT-SoVITS Audio Gate Status")
    print()
    print(f"- Review packet: {mark(REVIEW_HTML.exists())} `{REVIEW_HTML}`")
    print(f"- Reference transcript review packet: {mark(REF_REVIEW_HTML.exists())} `{REF_REVIEW_HTML}`")
    print(f"- Reference gate dashboard: {mark(HUMAN_GATE_DASHBOARD.exists())} `{HUMAN_GATE_DASHBOARD}`")
    print(f"- Reference listening workbook: {mark(REFERENCE_LISTENING_WORKBOOK.exists())} `{REFERENCE_LISTENING_WORKBOOK}`")
    print(f"- Chunk QA workbook: {mark(CHUNK_QA_WORKBOOK.exists())} `{CHUNK_QA_WORKBOOK}`")
    print(f"- Reference decision status: {mark(REFERENCE_DECISION_STATUS.exists())} `{REFERENCE_DECISION_STATUS}`")
    print(f"- Reference quality manifest: {mark(REF_QUALITY.exists())} `{REF_QUALITY}`")
    print(f"- Reference visual QC: {mark(REF_VISUAL_QC.exists())} `{REF_VISUAL_QC}`")
    print(f"- Reference transcript gate report: {mark(REF_TRANSCRIPT_GATE.exists())} `{REF_TRANSCRIPT_GATE}`")
    print(f"- Adaptation fallback review set: {mark(ADAPTATION_SET.exists())} `{ADAPTATION_SET}`")
    print(f"- Artifact provenance manifest: {mark(PROVENANCE.exists())} `{PROVENANCE}`")
    print(f"- Production objective audit: {mark(OBJECTIVE_AUDIT.exists())} `{OBJECTIVE_AUDIT}`")
    print(f"- Delivery gate report: {mark(DELIVERY.exists())} `{DELIVERY}`")
    print(f"- Accepted reference marker: {mark(accepted_ref_ok)} {accepted_ref_text}")
    print(f"- Accepted reference marker count: `{accepted_marker_count}`")
    print(f"- Stitched WAV master: {mark(STITCHED.exists())} `{STITCHED}`")
    print(f"- Audio loudness report: {mark(LOUDNESS.exists())} `{LOUDNESS}`")
    chunk_asr_count = len(list(CHUNK_ASR_DIR.glob("*.asr-qa.md"))) if CHUNK_ASR_DIR.exists() else 0
    print(f"- Breeze-ASR-25 chunk gate reports: `{chunk_asr_count}`")
    print()
    print("| Chunk | WAV | Accepted |")
    print("| --- | --- | --- |")
    generated = 0
    accepted = 0
    for chunk_id in CHUNK_IDS:
        wav = CHUNKS_DIR / f"{chunk_id}.wav"
        marker_path = DECISIONS_DIR / f"{chunk_id}.accepted.md"
        generated += int(wav.exists())
        accepted += int(marker_path.exists())
        print(f"| `{chunk_id}` | `{mark(wav.exists())}` | `{mark(marker_path.exists())}` |")
    print()
    print(f"Generated chunks: `{generated}/14`")
    print(f"Accepted chunks: `{accepted}/14`")
    if not REF_REVIEW_HTML.exists():
        print("Next action: build the reference transcript review packet.")
    elif not accepted_ref_ok:
        print("Next action: run Breeze-ASR-25 on a prompt reference, create its exact transcript, then record exactly one accepted reference marker.")
    elif generated == 0:
        print("Next action: run `run_formal_chunk01_after_transcript.py`.")
    elif accepted < generated:
        print("Next action: run `chunk_asr_qa.py --gate --auto-decision` for generated chunk(s); repair any transcript mismatch.")
    elif generated < 14:
        print("Next action: generate exactly one next chunk with `generate_next_chunk_after_acceptance.py`.")
    else:
        print("Next action: stitch accepted chunks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
