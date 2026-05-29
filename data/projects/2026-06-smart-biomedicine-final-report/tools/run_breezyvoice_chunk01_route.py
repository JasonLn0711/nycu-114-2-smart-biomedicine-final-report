#!/usr/bin/env python3
"""Run the BreezyVoice chunk 01 route through ASR, then stop for semantic sweep."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
SOURCE = PROJECT / "breezyvoice-narration-chunks-v1.md"
SELF_CHECK = PROJECT / "tools/check_breezyvoice_chunk01_gate_rules.py"
PREFLIGHT = PROJECT / "tools/breezyvoice_chunk01_preflight.py"
GENERATOR = PROJECT / "tools/generate_breezyvoice_chunk.py"
ASR_GATE = PROJECT / "tools/gate_breezyvoice_chunk01.py"
SEMANTIC_COMMAND = PROJECT / "tools/print_breezyvoice_chunk01_semantic_command.py"
CHUNK_ID = "sbm_tts_01_opening"


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def run_step(label: str, cmd: list[str]) -> subprocess.CompletedProcess[str]:
    print(f"## {label}", flush=True)
    print(" ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    print(result.stdout.strip())
    return result


def run_capture(cmd: list[str]) -> str:
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def tracked_worktree_changes() -> str:
    return run_capture(["git", "status", "--porcelain", "--untracked-files=no"])


def origin_main_commit() -> str:
    return run_capture(["git", "rev-parse", "origin/main"])


def refresh_origin_main() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "fetch", "origin", "main"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def source_text(source_file: Path, chunk_id: str) -> str:
    text = source_file.read_text(encoding="utf-8")
    match = re.search(rf"^###\s+{re.escape(chunk_id)}\n(.*?)(?=^###\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    text_match = re.search(r"```text\n(.*?)\n```", match.group(1), flags=re.DOTALL)
    return text_match.group(1).strip() if text_match else ""


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true", help="Regenerate chunk 01 even if a prior WAV exists.")
    parser.add_argument("--required-gpu-name", default="RTX 5080")
    parser.add_argument("--expected-git-commit", default="")
    parser.add_argument("--expected-source-sha256", default="")
    parser.add_argument("--write-preflight-report", action="store_true")
    parser.add_argument(
        "--allow-dirty-checkout",
        action="store_true",
        help="Allow tracked local modifications. Avoid this for production evidence unless intentionally debugging.",
    )
    parser.add_argument(
        "--allow-unpushed-checkout",
        action="store_true",
        help="Allow HEAD to differ from the local origin/main ref. Avoid this for production evidence.",
    )
    parser.add_argument(
        "--skip-remote-refresh",
        action="store_true",
        help="Skip git fetch origin main before comparing HEAD with origin/main. Use only for offline debugging.",
    )
    args = parser.parse_args()

    text = source_text(SOURCE, CHUNK_ID) if SOURCE.exists() else ""
    if not text:
        return fail(f"chunk source text missing: {CHUNK_ID}", str(SOURCE))
    commit = run_capture(["git", "rev-parse", "HEAD"])
    text_hash = source_hash(text)
    if args.expected_git_commit and args.expected_git_commit != commit:
        return fail("git commit does not match expected production commit", f"expected={args.expected_git_commit}\nactual={commit}")
    if args.expected_source_sha256 and args.expected_source_sha256 != text_hash:
        return fail(
            "chunk 01 source hash does not match expected production source",
            f"expected={args.expected_source_sha256}\nactual={text_hash}",
        )
    dirty = tracked_worktree_changes()
    if dirty and not args.allow_dirty_checkout:
        return fail(
            "tracked worktree changes found; refusing production generation from an uncommitted checkout",
            dirty,
        )
    if not args.skip_remote_refresh:
        remote_refresh = refresh_origin_main()
        if remote_refresh.returncode != 0:
            return fail("could not refresh origin/main before production route", remote_refresh.stdout)
    remote_commit = origin_main_commit()
    if remote_commit != commit and not args.allow_unpushed_checkout:
        return fail(
            "HEAD does not match origin/main; refusing production generation from an unpushed or stale checkout",
            f"head={commit}\norigin_main={remote_commit}",
        )
    print("## Route identity", flush=True)
    print(f"git_commit={commit}", flush=True)
    print(f"origin_main_commit={remote_commit}", flush=True)
    print(f"chunk_id={CHUNK_ID}", flush=True)
    print(f"source_file={SOURCE}", flush=True)
    print(f"source_text_sha256={text_hash}", flush=True)
    print(f"source_text_characters={len(text)}", flush=True)

    self_check = run_step("Chunk 01 source and gate-rule self-check", ["python3", str(SELF_CHECK)])
    if self_check.returncode != 0:
        return fail("chunk 01 source/gate-rule self-check failed; generation was not attempted")

    preflight_cmd = ["python3", str(PREFLIGHT), "--required-gpu-name", args.required_gpu_name]
    if args.write_preflight_report:
        preflight_cmd.append("--write-report")
    preflight = run_step("Preflight", preflight_cmd)
    if preflight.returncode != 0:
        return fail("preflight failed; chunk 01 generation was not attempted")

    generate_cmd = [
        "python3",
        str(GENERATOR),
        "--chunk-id",
        CHUNK_ID,
        "--required-gpu-name",
        args.required_gpu_name,
    ]
    if args.overwrite:
        generate_cmd.append("--overwrite")
    generation = run_step("BreezyVoice generation", generate_cmd)
    if generation.returncode != 0:
        return fail("BreezyVoice generation failed; ASR gate was not attempted")

    asr = run_step("Breeze-ASR-25 transcript gate", ["python3", str(ASR_GATE)])
    if asr.returncode != 0:
        return fail("ASR gate failed; semantic sweep should not be recorded")

    semantic_command = run_step("Post-ASR semantic review command", ["python3", str(SEMANTIC_COMMAND)])
    if semantic_command.returncode != 0:
        return fail("could not print semantic review command")

    print("PASS: chunk 01 generated and ASR-gated. Do not start chunk 02 yet.")
    print("Next required manual gate: read the ASR report and run the semantic-sweep command above only if it passes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
