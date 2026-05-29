#!/usr/bin/env python3
"""Audit the GPT-SoVITS production plan against the explicit 8-part objective."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from accepted_reference import resolve_accepted_reference


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
EXPORT = ROOT / "exports/smart-biomedicine-gpt-sovits"
OUT = EXPORT / "qa/production-objective-audit.md"

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


@dataclass(frozen=True)
class Check:
    item: str
    ok: bool
    evidence: str


def status(ok: bool) -> str:
    return "PASS" if ok else "TODO"


def count(paths: list[Path]) -> int:
    return sum(path.exists() for path in paths)


def source_chunk_count() -> int:
    path = PROJECT / "gpt-sovits-narration-chunks-v1.md"
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    return sum(1 for chunk_id in CHUNK_IDS if chunk_id in text)


def reference_checks() -> list[Check]:
    refs = sorted((EXPORT / "reference").glob("prompt_ref_candidate_*.wav"))
    long_review_refs = sorted((EXPORT / "reference").glob("ref_candidate_*_12s.wav"))
    whole_source_not_used = not (EXPORT / "reference/260528_0839_record.wav").exists()
    return [
        Check(
            "1. Reference audio selection - prompt references",
            len(refs) >= 3,
            f"{len(refs)} prompt-ready references under exports/.../reference/",
        ),
        Check(
            "1. Reference audio selection - 11:42 source not used blindly",
            whole_source_not_used and len(long_review_refs) >= 3,
            f"whole-source prompt copy absent={whole_source_not_used}; review refs={len(long_review_refs)}",
        ),
        Check(
            "1. Reference audio selection - quality screens",
            (EXPORT / "qa/reference-quality/reference-quality-manifest.md").exists()
            and (EXPORT / "qa/reference-visual-qc/reference-visual-qc.md").exists(),
            "machine quality manifest and visual QC report",
        ),
        Check(
            "1. Reference audio selection - ASR-led accept/reject decision routing",
            (EXPORT / "qa/reference-decisions/reference-decision-status.md").exists(),
            "reference decision status recommends the next pending candidate and records ASR-led rejections",
        ),
    ]


def transcript_checks() -> list[Check]:
    refs = sorted((EXPORT / "reference").glob("prompt_ref_candidate_*.wav"))
    exact = [path.with_suffix(".exact-transcript.txt") for path in refs]
    exact_count = count(exact)
    try:
        accepted = resolve_accepted_reference()
        accepted_ok = True
        accepted_evidence = f"{accepted.stem}; marker={accepted.marker}"
        accepted_exact_ok = accepted.exact_transcript.exists()
    except RuntimeError as exc:
        accepted_ok = False
        accepted_exact_ok = False
        accepted_evidence = str(exc)
    return [
        Check(
            "2. Reference transcript - accepted reference exact transcript",
            accepted_ok and accepted_exact_ok,
            f"{exact_count}/{len(refs)} exact transcript files; accepted reference must have exact transcript",
        ),
        Check(
            "2. Reference transcript - accepted prompt marker",
            accepted_ok,
            accepted_evidence,
        ),
        Check(
            "2. Reference transcript - fallback adaptation review set",
            (EXPORT / "reference/adaptation-clean-set-v1/adaptation_clean_set_v1_review_only.wav").exists(),
            "45-90s fallback review set prepared as review-only evidence",
        ),
    ]


def narration_checks() -> list[Check]:
    chunk_wavs = [EXPORT / f"chunks/{chunk_id}.wav" for chunk_id in CHUNK_IDS]
    chunk01_wav = EXPORT / "chunks/sbm_tts_01_opening.wav"
    chunk01_marker = EXPORT / "qa/chunk-decisions/sbm_tts_01_opening.accepted.md"
    return [
        Check(
            "3. Narration generation - 14 chunk source",
            source_chunk_count() == 14,
            f"{source_chunk_count()}/14 chunk IDs in gpt-sovits-narration-chunks-v1.md",
        ),
        Check(
            "3. Narration generation - first formal chunk generated",
            chunk01_wav.exists(),
            str(chunk01_wav),
        ),
        Check(
            "3. Narration generation - chunk 01 ASR-accepted before continuing",
            chunk01_marker.exists(),
            str(chunk01_marker),
        ),
        Check(
            "3. Narration generation - formal WAVs one per chunk",
            count(chunk_wavs) == 14,
            f"{count(chunk_wavs)}/14 formal chunk WAVs",
        ),
        Check(
            "3. Narration generation - guarded generation helpers",
            (PROJECT / "tools/generate_next_chunk_after_acceptance.py").exists()
            and (PROJECT / "tools/generate_gptsovits_chunk.py").exists(),
            "one-chunk generation helpers exist",
        ),
    ]


def audio_qa_checks() -> list[Check]:
    markers = [EXPORT / f"qa/chunk-decisions/{chunk_id}.accepted.md" for chunk_id in CHUNK_IDS]
    return [
        Check(
            "4. Audio QA - tracked QA sheet",
            (PROJECT / "gpt-sovits-audio-qa-sheet-v1.md").exists()
            and (EXPORT / "review-packet/chunk-qa-workbook/index.html").exists(),
            "tracked audio QA sheet and chunk QA workbook exist",
        ),
        Check(
            "4. Audio QA - Breeze-ASR-25 accepted chunk decisions",
            count(markers) == 14,
            f"{count(markers)}/14 accepted chunk markers",
        ),
        Check(
            "4. Audio QA - pronunciation and loudness gates",
            (EXPORT / "qa/term-consistency-gate.md").exists()
            and (EXPORT / "qa/audio-loudness-report.md").exists(),
            "term consistency and loudness reports exist",
        ),
    ]


def stitching_checks() -> list[Check]:
    stitched = EXPORT / "stitching/smart-biomedicine-final-report-narration-v1.wav"
    return [
        Check(
            "5. Stitching - guarded stitch helper",
            (PROJECT / "tools/stitch_accepted_chunks.py").exists(),
            "stitch helper requires formal WAVs and Breeze-ASR-25 accepted markers",
        ),
        Check(
            "5. Stitching - WAV master",
            stitched.exists(),
            str(stitched),
        ),
    ]


def recording_checks() -> list[Check]:
    return [
        Check(
            "6. Video recording - Markdown report surface",
            (PROJECT / "markdown-report-v1.md").exists(),
            str(PROJECT / "markdown-report-v1.md"),
        ),
        Check(
            "6. Video recording - recording surface and cue sheets",
            (EXPORT / "recording/markdown-report-recording.html").exists()
            and (PROJECT / "video-recording-cue-sheet-v1.md").exists()
            and (PROJECT / "video-recording-qa-sheet-v1.md").exists(),
            "recording HTML, cue sheet, and QA sheet",
        ),
        Check(
            "6. Video recording - final video candidate",
            bool(list((EXPORT / "video").glob("*"))) if (EXPORT / "video").exists() else False,
            "video candidate under exports/.../video/",
        ),
    ]


def fallback_checks() -> list[Check]:
    fallback_markers = list((EXPORT / "qa/fallback-chunks").glob("*.md")) if (EXPORT / "qa/fallback-chunks").exists() else []
    return [
        Check(
            "7. Fallback - opening/closing registration helper",
            (PROJECT / "tools/register_human_fallback_chunk.py").exists(),
            "helper supports sbm_tts_01_opening and sbm_tts_14_closing",
        ),
        Check(
            "7. Fallback - fallback only when needed",
            True,
            f"{len(fallback_markers)} fallback markers; zero is acceptable while GPT-SoVITS path is still under review",
        ),
    ]


def submission_checks() -> list[Check]:
    return [
        Check(
            "8. Submission - proof templates",
            all(
                path.exists()
                for path in [
                    EXPORT / "submission/youtube-url.txt.TEMPLATE",
                    EXPORT / "submission/padlet-post-proof.md.TEMPLATE",
                    EXPORT / "submission/peer-engagement-proof.md.TEMPLATE",
                    EXPORT / "submission/presenter-response-proof.md.TEMPLATE",
                ]
            ),
            "YouTube, Padlet, peer engagement, and presenter response templates",
        ),
        Check(
            "8. Submission - YouTube proof",
            (EXPORT / "submission/youtube-url.txt").exists(),
            str(EXPORT / "submission/youtube-url.txt"),
        ),
        Check(
            "8. Submission - Padlet proof before 2026-06-13 23:00",
            (EXPORT / "submission/padlet-post-proof.md").exists(),
            str(EXPORT / "submission/padlet-post-proof.md"),
        ),
        Check(
            "8. Submission - peer engagement proof before 2026-06-17",
            (EXPORT / "submission/peer-engagement-proof.md").exists(),
            str(EXPORT / "submission/peer-engagement-proof.md"),
        ),
        Check(
            "8. Submission - presenter response proof before 2026-06-20",
            (EXPORT / "submission/presenter-response-proof.md").exists(),
            str(EXPORT / "submission/presenter-response-proof.md"),
        ),
    ]


def main() -> int:
    checks = (
        reference_checks()
        + transcript_checks()
        + narration_checks()
        + audio_qa_checks()
        + stitching_checks()
        + recording_checks()
        + fallback_checks()
        + submission_checks()
    )
    passed = sum(check.ok for check in checks)
    next_todo = next((check.item for check in checks if not check.ok), "complete")

    lines = [
        "# GPT-SoVITS Production Objective Audit",
        "",
        "This audit maps the current production state to the explicit eight-part plan for the Smart Biomedicine final report.",
        "",
        f"- passed_checks: `{passed}/{len(checks)}`",
        f"- next_required_gate: `{next_todo}`",
        "",
        "| Requirement | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        lines.append(f"| {check.item} | `{status(check.ok)}` | {check.evidence} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `PASS` means current local evidence proves that requirement or guardrail is in place.",
            "- `TODO` means the requirement is not complete yet, even if supporting tools already exist.",
            "- Breeze-ASR-25 transcript gates now own chunk acceptance; human listening is an exception path for ambiguous or repeatedly unstable output.",
            "- Fallback markers are not required unless GPT-SoVITS output fails identity or stability review.",
            "",
        ]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)
    print(f"passed_checks={passed}/{len(checks)}")
    print(f"next_required_gate={next_todo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
