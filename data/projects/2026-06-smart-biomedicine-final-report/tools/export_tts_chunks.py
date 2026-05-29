#!/usr/bin/env python3
"""Export GPT-SoVITS TTS chunks from the tracked narration chunk plan."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
DEFAULT_SOURCE = PROJECT / "gpt-sovits-narration-chunks-v1.md"
DEFAULT_OUT = ROOT / "exports/smart-biomedicine-gpt-sovits/chunk-text"


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    source = Path(args.source)
    out_dir = Path(args.out_dir)
    text = source.read_text(encoding="utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks = re.findall(r"### (sbm_tts_\d+_[^\n]+).*?```text\n(.*?)\n```", text, flags=re.S)
    if len(chunks) != 14:
        raise SystemExit(f"expected 14 chunks, found {len(chunks)}")

    manifest_lines = [
        "# Exported GPT-SoVITS Chunk Text Manifest",
        "",
        f"Source: `{source}`",
        f"Output directory: `{out_dir}`",
        "",
        "| Chunk | Words | Text file | Planned WAV | QA status |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for chunk_id, chunk_text in chunks:
        words = word_count(chunk_text)
        if not 120 <= words <= 220:
            raise SystemExit(f"{chunk_id} has {words} words; expected 120-220")
        text_path = out_dir / f"{chunk_id}.txt"
        text_path.write_text(chunk_text.strip() + "\n", encoding="utf-8")
        wav = f"exports/smart-biomedicine-gpt-sovits/chunks/{chunk_id}.wav"
        manifest_lines.append(
            f"| `{chunk_id}` | `{words}` | `{text_path}` | `{wav}` | `[ ] not generated` |"
        )

    manifest_path = out_dir / "chunk-text-manifest.md"
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"exported {len(chunks)} chunks to {out_dir}")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
