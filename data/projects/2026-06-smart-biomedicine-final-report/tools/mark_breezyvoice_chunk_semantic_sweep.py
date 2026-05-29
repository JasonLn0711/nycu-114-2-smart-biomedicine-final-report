#!/usr/bin/env python3
"""Record a manual semantic sweep for one BreezyVoice chunk."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
CHUNKS_DIR = ROOT / "exports/smart-biomedicine-breezyvoice/chunks"
QA_DIR = ROOT / "exports/smart-biomedicine-breezyvoice/qa"
ASR_DIR = QA_DIR / "chunk-asr"
DECISIONS_DIR = QA_DIR / "chunk-decisions"
SWEEP_DIR = QA_DIR / "semantic-sweeps"
LOG_DIR = QA_DIR / "experiment-logs"
DEFAULT_SOURCE = PROJECT / "breezyvoice-narration-chunks-v1.md"
GENERATION_LOG = LOG_DIR / "breezyvoice-chunk-generations.jsonl"
DECISION_TOOL = PROJECT / "tools/mark_chunk_review_decision.py"
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


def source_text(source_file: Path, chunk_id: str) -> str:
    text = source_file.read_text(encoding="utf-8")
    match = re.search(rf"^###\s+{re.escape(chunk_id)}\n(.*?)(?=^###\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    block = match.group(1)
    text_match = re.search(r"```text\n(.*?)\n```", block, flags=re.DOTALL)
    return text_match.group(1).strip() if text_match else ""


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def matching_generation(log: Path, chunk_id: str, wav: Path, text_hash: str) -> dict[str, object] | None:
    if not log.exists():
        return None
    wav_path = str(wav.resolve())
    matched: dict[str, object] | None = None
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
            and event_wav == wav_path
            and event.get("source_text_sha256") == text_hash
        ):
            matched = event
    return matched


def append_jsonl(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-id", required=True, choices=CHUNK_IDS)
    parser.add_argument("--asr-report", type=Path)
    parser.add_argument("--source-file", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--generation-log", type=Path, default=GENERATION_LOG)
    parser.add_argument("--chunks-dir", type=Path, default=CHUNKS_DIR)
    parser.add_argument("--decisions-dir", type=Path, default=DECISIONS_DIR)
    parser.add_argument("--sweep-dir", type=Path, default=SWEEP_DIR)
    parser.add_argument("--log-dir", type=Path, default=LOG_DIR)
    parser.add_argument("--required-phrase", action="append", default=[])
    parser.add_argument("--ack-clinical-boundary", action="store_true")
    parser.add_argument("--ack-staff-review", action="store_true")
    parser.add_argument("--ack-human-staff-check", dest="ack_staff_review", action="store_true")
    parser.add_argument("--ack-final-authority", action="store_true")
    parser.add_argument("--ack-no-autonomous-medical-action", action="store_true")
    parser.add_argument("--ack-no-meaning-changing-medical-error", action="store_true")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    asr_report = args.asr_report or (ASR_DIR / f"{args.chunk_id}.asr-qa.md")
    wav = args.chunks_dir / f"{args.chunk_id}.wav"
    if not wav.exists():
        return fail(f"BreezyVoice chunk WAV missing: {wav}")
    if not asr_report.exists():
        return fail(f"ASR report missing: {asr_report}")

    text = source_text(args.source_file, args.chunk_id) if args.source_file.exists() else ""
    if not text:
        return fail(f"chunk source text missing: {args.chunk_id}", str(args.source_file))
    text_hash = source_hash(text)
    generation = matching_generation(args.generation_log, args.chunk_id, wav, text_hash)
    if not generation:
        return fail(
            "matching BreezyVoice generation provenance missing",
            "\n".join(
                [
                    f"generation_log={args.generation_log}",
                    f"chunk_id={args.chunk_id}",
                    f"wav={wav.resolve()}",
                    f"source_text_sha256={text_hash}",
                ]
            ),
        )

    report = asr_report.read_text(encoding="utf-8")
    gate_status = report_field(report, "gate_status")
    missing_critical = report_field(report, "missing_critical")
    observed_ratio = report_field(report, "observed_ratio")
    transcript = fenced_section(report, "Normalized ASR Transcript")
    if gate_status != "pass":
        return fail("ASR report is not a passing transcript gate", f"gate_status={gate_status}")
    if missing_critical != "none":
        return fail("ASR report has missing critical phrases", f"missing_critical={missing_critical}")
    if not transcript:
        return fail("ASR transcript section missing from report", str(asr_report))

    normalized = normalize(transcript)
    missing_required = [phrase for phrase in args.required_phrase if normalize(phrase) not in normalized]
    if missing_required:
        return fail("semantic sweep failed required phrase check", json.dumps(missing_required, indent=2))

    ack_flags = {
        "clinical_boundary": args.ack_clinical_boundary,
        "staff_review": args.ack_staff_review,
        "final_authority": args.ack_final_authority,
        "no_autonomous_medical_action": args.ack_no_autonomous_medical_action,
        "no_meaning_changing_medical_error": args.ack_no_meaning_changing_medical_error,
    }
    missing_acks = [name for name, ok in ack_flags.items() if not ok]
    if missing_acks:
        return fail("manual semantic sweep acknowledgements are incomplete", "missing: " + ", ".join(missing_acks))

    args.sweep_dir.mkdir(parents=True, exist_ok=True)
    sweep = args.sweep_dir / f"{args.chunk_id}.semantic-sweep.md"
    sweep.write_text(
        "\n".join(
            [
                f"# BreezyVoice Semantic Sweep - {args.chunk_id}",
                "",
                f"- created_at: `{datetime.now().isoformat(timespec='seconds')}`",
                f"- chunk_id: `{args.chunk_id}`",
                f"- asr_report: `{asr_report}`",
                f"- generation_log: `{args.generation_log}`",
                f"- source_file: `{args.source_file}`",
                f"- source_text_sha256: `{text_hash}`",
                f"- observed_ratio: `{observed_ratio}`",
                "- gate_status: `pass`",
                "- missing_critical: `none`",
                *[f"- ack_{name}: `{str(ok).lower()}`" for name, ok in ack_flags.items()],
                f"- notes: `{args.notes}`",
                "",
                "## Required Phrases",
                "",
                *([f"- `{phrase}`" for phrase in args.required_phrase] or ["- `none`"]),
                "",
                "## ASR Transcript Reviewed",
                "",
                "```text",
                transcript,
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    append_jsonl(
        args.log_dir / "breezyvoice-semantic-sweeps.jsonl",
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "event": "breezyvoice_semantic_sweep",
            "chunk_id": args.chunk_id,
            "asr_report": str(asr_report),
            "semantic_sweep": str(sweep),
            "generation_log": str(args.generation_log),
            "source_file": str(args.source_file),
            "source_text_sha256": text_hash,
            "observed_ratio": observed_ratio,
            "ack_flags": ack_flags,
            "required_phrases": args.required_phrase,
            "notes": args.notes,
        },
    )

    decision = subprocess.run(
        [
            "python3",
            str(DECISION_TOOL),
            "--chunk-id",
            args.chunk_id,
            "--decision",
            "accepted",
            "--chunks-dir",
            str(args.chunks_dir),
            "--decisions-dir",
            str(args.decisions_dir),
            "--engine-label",
            "BreezyVoice-26",
            "--notes",
            f"ASR gate passed and semantic sweep recorded: {sweep}",
            "--ack-breeze-asr-25-cuda",
            "--ack-breeze-asr-25-transcript-pass",
            "--ack-transcript-matches-source",
            "--require-semantic-sweep",
            "--ack-semantic-sweep",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if decision.returncode != 0:
        return fail("could not record BreezyVoice accepted marker", decision.stdout)

    print(f"PASS: semantic sweep recorded for {args.chunk_id}")
    print(sweep)
    print(decision.stdout.strip())
    print("Next gate: generate the next chunk only through the guarded next-chunk helper.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
