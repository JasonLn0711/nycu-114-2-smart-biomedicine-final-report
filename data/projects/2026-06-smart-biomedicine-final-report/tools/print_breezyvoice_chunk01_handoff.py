#!/usr/bin/env python3
"""Print the exact guarded RTX 5080 handoff command for BreezyVoice chunk 01."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
SOURCE = PROJECT / "breezyvoice-narration-chunks-v1.md"
ROUTE = PROJECT / "tools/run_breezyvoice_chunk01_route.py"
CHUNK_ID = "sbm_tts_01_opening"


def run_capture(cmd: list[str]) -> str:
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def source_text(source_file: Path, chunk_id: str) -> str:
    text = source_file.read_text(encoding="utf-8")
    match = re.search(rf"^###\s+{re.escape(chunk_id)}\n(.*?)(?=^###\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    text_match = re.search(r"```text\n(.*?)\n```", match.group(1), flags=re.DOTALL)
    return text_match.group(1).strip() if text_match else ""


def main() -> int:
    text = source_text(SOURCE, CHUNK_ID) if SOURCE.exists() else ""
    if not text:
        raise SystemExit(f"missing chunk source text: {CHUNK_ID}")

    commit = run_capture(["git", "rev-parse", "HEAD"])
    source_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print("# BreezyVoice chunk 01 RTX 5080 handoff")
    print()
    print(f"- git_commit: `{commit}`")
    print(f"- chunk_id: `{CHUNK_ID}`")
    print(f"- source_file: `{SOURCE}`")
    print(f"- source_text_sha256: `{source_sha}`")
    print(f"- source_text_characters: `{len(text)}`")
    print()
    print("## Command")
    print()
    print("```bash")
    print(
        "python3 "
        f"{ROUTE.relative_to(ROOT)} "
        "--write-preflight-report "
        "--overwrite "
        f"--expected-git-commit {commit} "
        f"--expected-source-sha256 {source_sha}"
    )
    print("```")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
