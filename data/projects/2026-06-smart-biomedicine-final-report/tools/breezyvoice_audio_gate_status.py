#!/usr/bin/env python3
"""Print the current BreezyVoice audio-production gate status."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
SOURCE = PROJECT / "breezyvoice-narration-chunks-v1.md"
EXPORT = ROOT / "exports/smart-biomedicine-breezyvoice"
CHUNKS_DIR = EXPORT / "chunks"
ASR_DIR = EXPORT / "qa/chunk-asr"
DECISIONS_DIR = EXPORT / "qa/chunk-decisions"
SEMANTIC_SWEEP_DIR = EXPORT / "qa/semantic-sweeps"
STITCHED = EXPORT / "stitching/smart-biomedicine-final-report-narration-v1.wav"
GENERATION_LOG = EXPORT / "qa/experiment-logs/breezyvoice-chunk-generations.jsonl"
ASR_LOG = EXPORT / "qa/experiment-logs/chunk-asr-gates.jsonl"
SEMANTIC_LOG = EXPORT / "qa/experiment-logs/breezyvoice-semantic-sweeps.jsonl"
ROUTE = PROJECT / "tools/run_breezyvoice_chunk01_route.py"
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


def run_capture(cmd: list[str]) -> str:
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def chunk01_handoff_command() -> str:
    text = source_text("sbm_tts_01_opening")
    commit = run_capture(["git", "rev-parse", "HEAD"])
    return (
        "python3 "
        f"{ROUTE.relative_to(ROOT)} "
        "--write-preflight-report "
        "--overwrite "
        f"--expected-git-commit {commit} "
        f"--expected-source-sha256 {source_hash(text)}"
    )


def generation_provenance_status(chunk_id: str, wav: Path, text: str) -> str:
    if not wav.exists():
        return "TODO"
    if not text or not GENERATION_LOG.exists():
        return "STALE"
    expected_hash = source_hash(text)
    expected_wav = str(wav.resolve())
    for line in GENERATION_LOG.read_text(encoding="utf-8").splitlines():
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
            return "PASS"
    return "STALE"


def asr_gate_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^-\s+gate_status:\s+`([^`]*)`", text, flags=re.MULTILINE)
    return match.group(1) if match else "unknown"


def main() -> int:
    print("# BreezyVoice Audio Gate Status")
    print()
    print(f"- Active source: {mark(SOURCE.exists())} `{SOURCE}`")
    print(f"- Generation log: {mark(GENERATION_LOG.exists())} `{GENERATION_LOG}`")
    print(f"- ASR gate log: {mark(ASR_LOG.exists())} `{ASR_LOG}`")
    print(f"- Semantic sweep log: {mark(SEMANTIC_LOG.exists())} `{SEMANTIC_LOG}`")
    print(f"- Stitched WAV master: {mark(STITCHED.exists())} `{STITCHED}`")
    print()
    print("| Chunk | Source | WAV | Generation | ASR Gate | Semantic Sweep | Accepted |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    source_count = 0
    provenanced_count = 0
    stale_count = 0
    asr_pass_count = 0
    sweep_count = 0
    accepted_count = 0
    next_action = ""
    for chunk_id in CHUNK_IDS:
        text = source_text(chunk_id)
        has_source = bool(text)
        wav = CHUNKS_DIR / f"{chunk_id}.wav"
        generation_status = generation_provenance_status(chunk_id, wav, text)
        asr_report = ASR_DIR / f"{chunk_id}.asr-qa.md"
        sweep = SEMANTIC_SWEEP_DIR / f"{chunk_id}.semantic-sweep.md"
        accepted = DECISIONS_DIR / f"{chunk_id}.accepted.md"
        asr_status = asr_gate_status(asr_report)
        source_count += int(has_source)
        provenanced_count += int(generation_status == "PASS")
        stale_count += int(generation_status == "STALE")
        asr_pass_count += int(asr_status == "pass")
        sweep_count += int(sweep.exists())
        accepted_count += int(accepted.exists())
        print(
            f"| `{chunk_id}` | `{mark(has_source)}` | `{mark(wav.exists())}` | `{generation_status}` | "
            f"`{asr_status}` | `{mark(sweep.exists())}` | `{mark(accepted.exists())}` |"
        )
        if not next_action:
            if not has_source:
                next_action = f"add BreezyVoice source for `{chunk_id}` only after previous chunk is accepted"
            elif not wav.exists():
                if chunk_id == "sbm_tts_01_opening":
                    next_action = "run chunk 01 route on RTX 5080 with `run_breezyvoice_chunk01_route.py`"
                else:
                    next_action = f"generate `{chunk_id}` on RTX 5080 with `generate_next_breezyvoice_chunk_after_acceptance.py`"
            elif generation_status != "PASS":
                next_action = f"regenerate `{chunk_id}` on RTX 5080 so the WAV matches current source provenance"
            elif asr_status != "pass":
                next_action = f"run Breeze-ASR-25 CUDA gate for `{chunk_id}`"
            elif not sweep.exists():
                next_action = f"run semantic sweep marker for `{chunk_id}`"
            elif not accepted.exists():
                next_action = f"write accepted marker for `{chunk_id}` through semantic-sweep tooling"
    print()
    print(f"Source chunks: `{source_count}/14`")
    print(f"Provenanced generated chunks: `{provenanced_count}/14`")
    print(f"Stale or unproven WAV chunks: `{stale_count}/14`")
    print(f"ASR-passed chunks: `{asr_pass_count}/14`")
    print(f"Semantic-swept chunks: `{sweep_count}/14`")
    print(f"Accepted chunks: `{accepted_count}/14`")
    print(f"Next gate: {next_action or 'stitch accepted BreezyVoice chunks'}")
    if next_action.startswith("run chunk 01 route"):
        print()
        print("Exact chunk 01 RTX 5080 handoff command:")
        print("```bash")
        print(chunk01_handoff_command())
        print("```")
    print()
    print("Stitch command after 14/14 accepted and semantic-swept chunks:")
    print(
        "python3 data/projects/2026-06-smart-biomedicine-final-report/tools/stitch_accepted_chunks.py "
        "--chunks-dir exports/smart-biomedicine-breezyvoice/chunks "
        "--decisions-dir exports/smart-biomedicine-breezyvoice/qa/chunk-decisions "
        "--semantic-sweep-dir exports/smart-biomedicine-breezyvoice/qa/semantic-sweeps "
        "--require-semantic-sweep "
        "--output exports/smart-biomedicine-breezyvoice/stitching/smart-biomedicine-final-report-narration-v1.wav "
        "--silence 0.5"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
