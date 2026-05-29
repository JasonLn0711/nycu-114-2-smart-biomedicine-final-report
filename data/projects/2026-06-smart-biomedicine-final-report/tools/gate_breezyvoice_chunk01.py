#!/usr/bin/env python3
"""Run the BreezyVoice chunk 01 Breeze-ASR-25 transcript gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
GATE = ROOT / "data/projects/2026-06-smart-biomedicine-final-report/tools/chunk_asr_qa.py"
SEMANTIC_COMMAND = ROOT / "data/projects/2026-06-smart-biomedicine-final-report/tools/print_breezyvoice_chunk01_semantic_command.py"
SOURCE = ROOT / "data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-narration-chunks-v1.md"
EXPORT = ROOT / "exports/smart-biomedicine-breezyvoice"
CHUNKS_DIR = EXPORT / "chunks"
GENERATION_LOG = EXPORT / "qa/experiment-logs/breezyvoice-chunk-generations.jsonl"
CHUNK_ID = "sbm_tts_01_opening"


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def source_text(source_file: Path, chunk_id: str) -> str:
    text = source_file.read_text(encoding="utf-8")
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


def tracked_worktree_changes() -> str:
    return run_capture(["git", "status", "--porcelain", "--untracked-files=no"])


def refresh_origin_main() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "fetch", "origin", "main"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def matching_generation_event(log: Path, chunk_id: str, wav: Path, text_hash: str) -> dict[str, object] | None:
    if not log.exists():
        return None
    expected_wav = str(wav.resolve())
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
            and event.get("source_text_sha256") == text_hash
        ):
            return event
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-file", type=Path, default=SOURCE)
    parser.add_argument("--chunks-dir", type=Path, default=CHUNKS_DIR)
    parser.add_argument("--generation-log", type=Path, default=GENERATION_LOG)
    parser.add_argument("--required-gpu-name", default="RTX 5080")
    parser.add_argument(
        "--allow-dirty-checkout",
        action="store_true",
        help="Allow tracked local modifications. Avoid this for production ASR evidence.",
    )
    parser.add_argument(
        "--allow-unpushed-checkout",
        action="store_true",
        help="Allow HEAD to differ from origin/main. Avoid this for production ASR evidence.",
    )
    parser.add_argument(
        "--skip-remote-refresh",
        action="store_true",
        help="Skip git fetch origin main before comparing HEAD with origin/main. Use only for offline debugging.",
    )
    args = parser.parse_args()

    current_commit = run_capture(["git", "rev-parse", "HEAD"])
    dirty = tracked_worktree_changes()
    if dirty and not args.allow_dirty_checkout:
        return fail(
            "tracked worktree changes found; refusing chunk 01 ASR from an uncommitted checkout",
            dirty,
        )
    if not args.skip_remote_refresh:
        remote_refresh = refresh_origin_main()
        if remote_refresh.returncode != 0:
            return fail("could not refresh origin/main before chunk 01 ASR", remote_refresh.stdout)
    remote_commit = run_capture(["git", "rev-parse", "origin/main"])
    if remote_commit != current_commit and not args.allow_unpushed_checkout:
        return fail(
            "HEAD does not match origin/main; refusing chunk 01 ASR from an unpushed or stale checkout",
            f"head={current_commit}\norigin_main={remote_commit}",
        )

    wav = args.chunks_dir / f"{CHUNK_ID}.wav"
    if not wav.exists():
        return fail(f"BreezyVoice chunk WAV missing: {wav}")
    text = source_text(args.source_file, CHUNK_ID) if args.source_file.exists() else ""
    if not text:
        return fail(f"BreezyVoice chunk source text missing: {CHUNK_ID}", str(args.source_file))
    text_hash = source_hash(text)
    generation_event = matching_generation_event(args.generation_log, CHUNK_ID, wav, text_hash)
    if not generation_event:
        return fail(
            "matching BreezyVoice generation provenance missing; regenerate chunk 01 before ASR",
            "\n".join(
                [
                    f"generation_log={args.generation_log}",
                    f"wav={wav.resolve()}",
                    f"source_text_sha256={text_hash}",
                ]
            ),
        )
    if generation_event.get("git_commit") != current_commit or generation_event.get("origin_main_commit") != remote_commit:
        return fail(
            "matching BreezyVoice generation does not prove the current checkout provenance; regenerate chunk 01 before ASR",
            "\n".join(
                [
                    f"head={current_commit}",
                    f"origin_main={remote_commit}",
                    f"generation_git_commit={generation_event.get('git_commit', '')}",
                    f"generation_origin_main_commit={generation_event.get('origin_main_commit', '')}",
                ]
            ),
        )

    cmd = [
        "python3",
        str(GATE),
        "--chunk-id",
        CHUNK_ID,
        "--language",
        "en",
        "--gate",
        "--engine-label",
        "BreezyVoice-26",
        "--source-file",
        str(args.source_file),
        "--chunks-dir",
        str(args.chunks_dir),
        "--out-dir",
        str(ROOT / "exports/smart-biomedicine-breezyvoice/qa/chunk-asr"),
        "--repair-dir",
        str(ROOT / "exports/smart-biomedicine-breezyvoice/qa/chunk-repairs"),
        "--log-dir",
        str(ROOT / "exports/smart-biomedicine-breezyvoice/qa/experiment-logs"),
        "--decisions-dir",
        str(ROOT / "exports/smart-biomedicine-breezyvoice/qa/chunk-decisions"),
        "--required-gpu-name",
        args.required_gpu_name,
    ]
    gate = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if gate.returncode != 0:
        return fail("BreezyVoice chunk 01 transcript gate failed", gate.stdout)
    print(gate.stdout.strip())
    semantic_command = subprocess.run(
        ["python3", str(SEMANTIC_COMMAND)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if semantic_command.returncode != 0:
        return fail("could not print semantic review command", semantic_command.stdout)
    print(semantic_command.stdout.strip())
    print("Next gate: run the semantic sweep marker only after manually reading the ASR transcript.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
