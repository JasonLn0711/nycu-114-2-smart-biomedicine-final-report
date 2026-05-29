#!/usr/bin/env python3
"""Audit the BreezyVoice final-report route against the full delivery objective."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
EXPORT = ROOT / "exports/smart-biomedicine-breezyvoice"
OUT = EXPORT / "qa/breezyvoice-objective-audit.md"
SOURCE = PROJECT / "breezyvoice-narration-chunks-v1.md"
REPORT = PROJECT / "markdown-report-v1.md"
SCRIPT = PROJECT / "markdown-report-20min-script-v2.md"
STITCHED = EXPORT / "stitching/smart-biomedicine-final-report-narration-v1.wav"

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


def mark(ok: bool) -> str:
    return "PASS" if ok else "TODO"


def count(paths: list[Path]) -> int:
    return sum(path.exists() for path in paths)


def run_capture(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return result.returncode, result.stdout.strip()


def report_field(text: str, field: str) -> str:
    match = re.search(rf"^-\s+{re.escape(field)}:\s+`([^`]*)`", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def source_text(chunk_id: str) -> str:
    if not SOURCE.exists():
        return ""
    text = SOURCE.read_text(encoding="utf-8")
    match = re.search(rf"^###\s+{re.escape(chunk_id)}\n(.*?)(?=^###\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    text_match = re.search(r"```text\n(.*?)\n```", match.group(1), flags=re.DOTALL)
    return text_match.group(1).strip() if text_match else ""


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_chunk_count() -> int:
    return sum(1 for chunk_id in CHUNK_IDS if source_text(chunk_id))


def matching_generation(chunk_id: str) -> bool:
    wav = EXPORT / f"chunks/{chunk_id}.wav"
    log = EXPORT / "qa/experiment-logs/breezyvoice-chunk-generations.jsonl"
    text = source_text(chunk_id)
    if not wav.exists() or not log.exists() or not text:
        return False
    expected_wav = str(wav.resolve())
    expected_hash = source_hash(text)
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        output_wav = event.get("output_wav")
        event_wav = str(Path(str(output_wav)).resolve()) if output_wav else ""
        if (
            event.get("event") == "breezyvoice_chunk_generation"
            and event.get("chunk_id") == chunk_id
            and event_wav == expected_wav
            and event.get("source_text_sha256") == expected_hash
        ):
            return True
    return False


def passed_asr(chunk_id: str) -> bool:
    path = EXPORT / f"qa/chunk-asr/{chunk_id}.asr-qa.md"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return report_field(text, "gate_status") == "pass" and report_field(text, "missing_critical") == "none"


def media_duration(path: Path) -> str:
    if not path.exists():
        return "missing"
    rc, out = run_capture(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)])
    if rc != 0:
        return f"ffprobe failed: {out}"
    try:
        seconds = float(out)
    except ValueError:
        return f"duration unknown: {out}"
    return f"{seconds:.2f}s"


def loudness_report_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    status = report_field(path.read_text(encoding="utf-8"), "status")
    return status or "unknown"


def final_video_passing_count(path: Path) -> tuple[int, int]:
    if not path.exists():
        return (0, 0)
    match = re.search(r"^Passing candidates:\s+`(\d+)/(\d+)`", path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    if not match:
        return (0, 0)
    return (int(match.group(1)), int(match.group(2)))


def report_image_links() -> list[str]:
    if not REPORT.exists():
        return []
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", REPORT.read_text(encoding="utf-8"))


def missing_report_images() -> list[str]:
    return [link for link in report_image_links() if not (REPORT.parent / link).exists()]


def mermaid_count() -> int:
    if not REPORT.exists():
        return 0
    return REPORT.read_text(encoding="utf-8").count("```mermaid")


def production_route_checks() -> list[Check]:
    source_only_rc, source_only_out = run_capture(
        ["python3", str(PROJECT / "tools/breezyvoice_chunk01_preflight.py"), "--source-only"]
    )
    full_rc, full_out = run_capture(["python3", str(PROJECT / "tools/breezyvoice_chunk01_preflight.py")])
    current_gpu = next((line for line in full_out.splitlines() if '"nvidia_smi"' in line), "nvidia_smi unavailable")
    return [
        Check(
            "3. RTX 5080-only source preflight",
            source_only_rc == 0,
            "chunk 01 source-only preflight passes; no generation attempted",
        ),
        Check(
            "3. RTX 5080 runtime preflight",
            full_rc == 0,
            current_gpu,
        ),
    ]


def checks() -> list[Check]:
    wavs = [EXPORT / f"chunks/{chunk_id}.wav" for chunk_id in CHUNK_IDS]
    generation_count = sum(matching_generation(chunk_id) for chunk_id in CHUNK_IDS)
    asr_count = sum(passed_asr(chunk_id) for chunk_id in CHUNK_IDS)
    semantic = [EXPORT / f"qa/semantic-sweeps/{chunk_id}.semantic-sweep.md" for chunk_id in CHUNK_IDS]
    accepted = [EXPORT / f"qa/chunk-decisions/{chunk_id}.accepted.md" for chunk_id in CHUNK_IDS]
    chunk01_semantic = EXPORT / "qa/semantic-sweeps/sbm_tts_01_opening.semantic-sweep.md"
    chunk01_accepted = EXPORT / "qa/chunk-decisions/sbm_tts_01_opening.accepted.md"
    final_videos = sorted((EXPORT / "video").glob("*")) if (EXPORT / "video").exists() else []
    loudness_report = EXPORT / "qa/audio-loudness-report.md"
    loudness_status = loudness_report_status(loudness_report)
    final_video_report = EXPORT / "qa/final-video-gate-status.md"
    final_video_passing, final_video_total = final_video_passing_count(final_video_report)
    provenance_manifest = EXPORT / "qa/provenance/artifact-provenance-manifest.md"
    submission_templates = [
        EXPORT / "submission/youtube-url.txt.TEMPLATE",
        EXPORT / "submission/padlet-post-proof.md.TEMPLATE",
        EXPORT / "submission/peer-engagement-proof.md.TEMPLATE",
        EXPORT / "submission/presenter-response-proof.md.TEMPLATE",
    ]
    return [
        Check("1. Markdown report screen", REPORT.exists(), str(REPORT)),
        Check("1. Markdown report visual assets", len(missing_report_images()) == 0, f"{len(report_image_links())} links; missing={len(missing_report_images())}"),
        Check("1. Mermaid diagrams present", mermaid_count() > 0, f"{mermaid_count()} Mermaid blocks"),
        Check("2. English narration script", SCRIPT.exists(), str(SCRIPT)),
        Check("2. BreezyVoice narration source exists", SOURCE.exists(), str(SOURCE)),
        Check("2. BreezyVoice chunk 01 source", bool(source_text("sbm_tts_01_opening")), "chunk 01 source text is present"),
        *production_route_checks(),
        Check("4. Chunk 01 provenanced BreezyVoice WAV", matching_generation("sbm_tts_01_opening"), "chunk 01 WAV must match current source generation provenance"),
        Check("4. Chunk 01 Breeze-ASR-25 transcript gate", passed_asr("sbm_tts_01_opening"), str(EXPORT / "qa/chunk-asr/sbm_tts_01_opening.asr-qa.md")),
        Check("5. Chunk 01 semantic sweep", chunk01_semantic.exists(), str(chunk01_semantic)),
        Check("5. Chunk 01 accepted marker", chunk01_accepted.exists(), str(chunk01_accepted)),
        Check("2. BreezyVoice chunk source coverage after chunk 01 acceptance", source_chunk_count() == 14, f"{source_chunk_count()}/14 chunks have source text"),
        Check("4. Provenanced BreezyVoice WAVs", generation_count == 14, f"{generation_count}/14 chunks have current-source generation provenance"),
        Check("4. Raw BreezyVoice WAV files", count(wavs) == 14, f"{count(wavs)}/14 WAVs exist"),
        Check("4. Breeze-ASR-25 transcript gates", asr_count == 14, f"{asr_count}/14 ASR reports pass"),
        Check("5. Semantic sweep markers", count(semantic) == 14, f"{count(semantic)}/14 semantic sweeps"),
        Check("5. Accepted chunk markers", count(accepted) == 14, f"{count(accepted)}/14 accepted markers"),
        Check("6. Stitched accepted WAV", STITCHED.exists(), f"{STITCHED}; duration={media_duration(STITCHED)}"),
        Check("8. Audio loudness gate", loudness_status == "PASS", f"{loudness_report}; status={loudness_status}"),
        Check("9. Recording HTML surface", (EXPORT / "recording/markdown-report-recording.html").exists(), str(EXPORT / "recording/markdown-report-recording.html")),
        Check("10. Final video QA", final_video_passing > 0, f"{final_video_report}; passing={final_video_passing}/{final_video_total}"),
        Check("10. Final video candidate", bool(final_videos), f"{len(final_videos)} files under {EXPORT / 'video'}"),
        Check("13. Artifact provenance manifest", provenance_manifest.exists(), str(provenance_manifest)),
        Check("13. Submission proof templates", count(submission_templates) == len(submission_templates), f"{count(submission_templates)}/{len(submission_templates)} templates"),
        Check("11. YouTube proof", (EXPORT / "submission/youtube-url.txt").exists(), str(EXPORT / "submission/youtube-url.txt")),
        Check("12. Padlet proof before 2026-06-13 23:00", (EXPORT / "submission/padlet-post-proof.md").exists(), str(EXPORT / "submission/padlet-post-proof.md")),
        Check("14. Peer engagement proof before 2026-06-17", (EXPORT / "submission/peer-engagement-proof.md").exists(), str(EXPORT / "submission/peer-engagement-proof.md")),
        Check("15. Presenter response proof before 2026-06-20", (EXPORT / "submission/presenter-response-proof.md").exists(), str(EXPORT / "submission/presenter-response-proof.md")),
    ]


def main() -> int:
    audited = checks()
    passed = sum(check.ok for check in audited)
    next_required = next((check.item for check in audited if not check.ok), "complete")
    lines = [
        "# BreezyVoice Final-Report Objective Audit",
        "",
        "This audit maps the current BreezyVoice 26 route to the full Smart Biomedicine final-report objective.",
        "",
        f"- passed_checks: `{passed}/{len(audited)}`",
        f"- next_required_gate: `{next_required}`",
        "",
        "| Requirement | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for check in audited:
        lines.append(f"| {check.item} | `{mark(check.ok)}` | {check.evidence} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `PASS` means current evidence proves the requirement or guardrail.",
            "- `TODO` means the full objective is not complete yet.",
            "- Chunk `02` generation remains out of bounds until chunk `01` has a provenanced BreezyVoice WAV, passing `breeze-asr-25` report, semantic sweep, and accepted marker.",
            "",
        ]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)
    print(f"passed_checks={passed}/{len(audited)}")
    print(f"next_required_gate={next_required}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
