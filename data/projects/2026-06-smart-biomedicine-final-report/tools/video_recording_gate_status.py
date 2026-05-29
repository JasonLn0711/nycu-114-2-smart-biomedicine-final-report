#!/usr/bin/env python3
"""Check video-recording readiness for the Smart Biomedicine final report."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
REPORT = PROJECT / "markdown-report-v1.md"
CUE = PROJECT / "video-recording-cue-sheet-v1.md"
QA = PROJECT / "video-recording-qa-sheet-v1.md"
DEFAULT_EXPORT_ROOT = ROOT / "exports/smart-biomedicine-gpt-sovits"

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


def report_image_links() -> list[str]:
    if not REPORT.exists():
        return []
    text = REPORT.read_text(encoding="utf-8")
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)


def mermaid_count() -> int:
    if not REPORT.exists():
        return 0
    return REPORT.read_text(encoding="utf-8").count("```mermaid")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--export-root",
        type=Path,
        default=DEFAULT_EXPORT_ROOT,
        help="Generated artifact root for the active audio/video route.",
    )
    parser.add_argument("--engine-label", default="GPT-SoVITS")
    args = parser.parse_args()

    decisions = args.export_root / "qa/chunk-decisions"
    audio = args.export_root / "stitching/smart-biomedicine-final-report-narration-v1.wav"
    recording_html = args.export_root / "recording/markdown-report-recording.html"
    recording_screenshot = args.export_root / "recording/qa/recording-html-top.png"
    accepted = sum((decisions / f"{chunk_id}.accepted.md").exists() for chunk_id in CHUNK_IDS)
    links = report_image_links()
    missing_images = [
        link for link in links if not (REPORT.parent / link).exists()
    ]

    print("# Video Recording Gate Status")
    print()
    print(f"- Engine route: `{args.engine_label}`")
    print(f"- Export root: `{args.export_root}`")
    print(f"- Markdown report: {mark(REPORT.exists())} `{REPORT}`")
    print(f"- Recording cue sheet: {mark(CUE.exists())} `{CUE}`")
    print(f"- Video QA sheet: {mark(QA.exists())} `{QA}`")
    print(f"- Recording HTML: {mark(recording_html.exists())} `{recording_html}`")
    print(f"- Recording HTML screenshot: {mark(recording_screenshot.exists())} `{recording_screenshot}`")
    print(f"- Accepted audio chunks: `{accepted}/14`")
    print(f"- Stitched audio master: {mark(audio.exists())} `{audio}`")
    print(f"- Mermaid blocks in report: `{mermaid_count()}`")
    print(f"- Image links in report: `{len(links)}`")
    print(f"- Missing image assets: `{len(missing_images)}`")
    for link in missing_images:
        print(f"  - `{link}`")
    print()
    if accepted < 14:
        print(f"Next action: finish {args.engine_label} chunk acceptance before opening video recording.")
    elif not audio.exists():
        print("Next action: stitch accepted chunks before recording.")
    elif missing_images:
        print("Next action: repair missing image assets before recording.")
    else:
        print("Next action: record the Markdown screen video using the cue sheet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
