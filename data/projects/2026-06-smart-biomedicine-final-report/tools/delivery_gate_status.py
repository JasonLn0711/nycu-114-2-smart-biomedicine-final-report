#!/usr/bin/env python3
"""Report end-to-end delivery status for the Smart Biomedicine final report."""

from __future__ import annotations

from pathlib import Path

from accepted_reference import resolve_accepted_reference


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
EXPORT = ROOT / "exports/smart-biomedicine-gpt-sovits"
OUT = EXPORT / "qa/delivery-gate-status.md"
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


def mark(ok: bool) -> str:
    return "PASS" if ok else "TODO"


def count_existing(paths: list[Path]) -> int:
    return sum(path.exists() for path in paths)


def chunk_source_count() -> int:
    path = PROJECT / "gpt-sovits-narration-chunks-v1.md"
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    return sum(1 for chunk_id in CHUNK_IDS if chunk_id in text)


def main() -> int:
    prompt_refs = sorted((EXPORT / "reference").glob("prompt_ref_candidate_*.wav"))
    exact_transcripts = [path.with_suffix(".exact-transcript.txt") for path in prompt_refs]
    exact_count = count_existing(exact_transcripts)
    try:
        accepted_reference = resolve_accepted_reference()
        accepted_reference_ok = True
        accepted_reference_evidence = f"{accepted_reference.stem} {accepted_reference.marker}"
        accepted_exact_ok = accepted_reference.exact_transcript.exists()
    except RuntimeError as exc:
        accepted_reference_ok = False
        accepted_exact_ok = False
        accepted_reference_evidence = str(exc)
    chunk_wavs = [EXPORT / f"chunks/{chunk_id}.wav" for chunk_id in CHUNK_IDS]
    accepted_chunks = [EXPORT / f"qa/chunk-decisions/{chunk_id}.accepted.md" for chunk_id in CHUNK_IDS]
    stitched = EXPORT / "stitching/smart-biomedicine-final-report-narration-v1.wav"
    final_video_candidates = sorted((EXPORT / "video").glob("*")) if (EXPORT / "video").exists() else []
    term_gate = EXPORT / "qa/term-consistency-gate.md"
    final_video_gate = EXPORT / "qa/final-video-gate-status.md"
    human_dashboard = EXPORT / "review-packet/human-gate-dashboard/index.html"
    reference_workbook = EXPORT / "review-packet/reference-listening-workbook/index.html"
    chunk_qa_workbook = EXPORT / "review-packet/chunk-qa-workbook/index.html"
    reference_decision_status = EXPORT / "qa/reference-decisions/reference-decision-status.md"
    objective_audit = EXPORT / "qa/production-objective-audit.md"
    visual_qc = EXPORT / "qa/reference-visual-qc/reference-visual-qc.md"
    advance_helper = PROJECT / "tools/advance_after_reference_review.py"
    fallback_helper = PROJECT / "tools/register_human_fallback_chunk.py"
    submission_templates = [
        EXPORT / "submission/youtube-url.txt.TEMPLATE",
        EXPORT / "submission/padlet-post-proof.md.TEMPLATE",
        EXPORT / "submission/peer-engagement-proof.md.TEMPLATE",
        EXPORT / "submission/presenter-response-proof.md.TEMPLATE",
    ]
    youtube_proof = EXPORT / "submission/youtube-url.txt"
    padlet_proof = EXPORT / "submission/padlet-post-proof.md"
    peer_proof = EXPORT / "submission/peer-engagement-proof.md"
    response_proof = EXPORT / "submission/presenter-response-proof.md"

    gates = [
        ("Reference audio selection", len(prompt_refs) >= 3, f"{len(prompt_refs)} prompt-ready references found"),
        ("Reference visual QC", visual_qc.exists(), str(visual_qc)),
        ("Reference gate dashboard", human_dashboard.exists(), str(human_dashboard)),
        ("Reference listening workbook", reference_workbook.exists(), str(reference_workbook)),
        ("Chunk QA workbook", chunk_qa_workbook.exists(), str(chunk_qa_workbook)),
        ("Reference decision status", reference_decision_status.exists(), str(reference_decision_status)),
        ("Production objective audit", objective_audit.exists(), str(objective_audit)),
        (
            "Accepted reference exact transcript",
            accepted_reference_ok and accepted_exact_ok,
            f"{exact_count}/{len(prompt_refs)} exact transcripts found; production requires the accepted reference transcript",
        ),
        ("Accepted reference marker", accepted_reference_ok, accepted_reference_evidence),
        ("Narration chunk source", chunk_source_count() == 14, f"{chunk_source_count()}/14 chunk IDs present in source"),
        ("Term consistency gate", term_gate.exists(), str(term_gate)),
        ("Post-reference advance helper", advance_helper.exists(), str(advance_helper)),
        ("Human fallback chunk helper", fallback_helper.exists(), str(fallback_helper)),
        ("Generated formal chunks", count_existing(chunk_wavs) == 14, f"{count_existing(chunk_wavs)}/14 WAVs"),
        ("Breeze-ASR-25 accepted chunks", count_existing(accepted_chunks) == 14, f"{count_existing(accepted_chunks)}/14 accepted markers"),
        ("Stitched WAV master", stitched.exists(), str(stitched)),
        ("Recording HTML surface", (EXPORT / "recording/markdown-report-recording.html").exists(), "browser recording surface exists"),
        ("Final video gate report", final_video_gate.exists(), str(final_video_gate)),
        ("Final video file", bool(final_video_candidates), f"{len(final_video_candidates)} candidate files under exports/.../video"),
        ("Submission proof templates", count_existing(submission_templates) == len(submission_templates), f"{count_existing(submission_templates)}/{len(submission_templates)} templates"),
        ("YouTube proof", youtube_proof.exists(), str(youtube_proof)),
        ("Padlet proof", padlet_proof.exists(), str(padlet_proof)),
        ("Peer engagement proof", peer_proof.exists(), str(peer_proof)),
        ("Presenter response proof", response_proof.exists(), str(response_proof)),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Smart Biomedicine Delivery Gate Status",
        "",
        "| Gate | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for name, ok, evidence in gates:
        lines.append(f"| {name} | `{mark(ok)}` | {evidence} |")

    generated_count = count_existing(chunk_wavs)
    accepted_count = count_existing(accepted_chunks)
    if generated_count > accepted_count:
        next_todo = "Breeze-ASR-25 accepted chunks"
    else:
        next_todo = next((name for name, ok, _ in gates if not ok), "complete")
    lines.extend(["", f"Next gate: `{next_todo}`", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8")

    print(OUT)
    for name, ok, evidence in gates:
        print(f"- {name}: {mark(ok)} ({evidence})")
    print(f"Next gate: {next_todo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
