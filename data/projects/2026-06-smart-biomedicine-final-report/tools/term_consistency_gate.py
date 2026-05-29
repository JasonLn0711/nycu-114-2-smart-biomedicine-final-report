#!/usr/bin/env python3
"""Check TTS chunk text for pronunciation-safe technical terms."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CHUNKS = ROOT / "data/projects/2026-06-smart-biomedicine-final-report/gpt-sovits-narration-chunks-v1.md"
OUT = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/term-consistency-gate.md"

EXPECTED_SAFE_FORMS = [
    "A. S. R.",
    "large language model",
    "HAY-ger",
    "Jee-ang",
    "Lang One",
    "Reh-Med-Ee",
    "Soh-Vits",
    "Pad-let",
]

UNSAFE_FORMS = {
    "ASR": "Use `A. S. R.` in TTS text.",
    "LLM": "Use `large language model` in TTS text.",
    "Hager": "Use `HAY-ger` in TTS text.",
    "Jiang": "Use `Jee-ang` in TTS text.",
    "Lang1": "Use `Lang One` in TTS text.",
    "ReMedE": "Use `Reh-Med-Ee` in TTS text.",
    "SoVITS": "Use `Soh-Vits` in TTS text.",
    "Padlet": "Use `Pad-let` in TTS text.",
}


def extract_tts_blocks(markdown: str) -> str:
    start = markdown.find("## TTS Chunks")
    source = markdown[start:] if start >= 0 else markdown
    blocks = re.findall(r"```text\n(.*?)\n```", source, flags=re.S)
    return "\n\n".join(blocks)


def main() -> int:
    text = CHUNKS.read_text(encoding="utf-8")
    tts = extract_tts_blocks(text)
    lines = [
        "# Term Consistency Gate",
        "",
        "This gate checks the TTS chunk text, not synthesized audio. Human listening still controls final pronunciation acceptance.",
        "",
        "## Expected Safe Forms",
        "",
        "| Safe form | Status | Count |",
        "| --- | --- | ---: |",
    ]
    all_expected_present = True
    for form in EXPECTED_SAFE_FORMS:
        count = tts.count(form)
        ok = count > 0
        all_expected_present = all_expected_present and ok
        lines.append(f"| `{form}` | `{'PASS' if ok else 'TODO'}` | `{count}` |")

    lines.extend(["", "## Unsafe Raw Forms", "", "| Raw form | Status | Count | Fix |", "| --- | --- | ---: | --- |"])
    unsafe_hits = 0
    for form, fix in UNSAFE_FORMS.items():
        pattern = re.compile(rf"(?<![A-Za-z0-9.]){re.escape(form)}(?![A-Za-z0-9.])")
        count = len(pattern.findall(tts))
        unsafe_hits += count
        lines.append(f"| `{form}` | `{'PASS' if count == 0 else 'TODO'}` | `{count}` | {fix} |")

    status = "PASS" if all_expected_present and unsafe_hits == 0 else "TODO"
    lines.extend(
        [
            "",
            f"Overall status: `{status}`",
            "",
            "Next action: if this gate reports TODO, edit only `gpt-sovits-narration-chunks-v1.md` TTS text before formal generation.",
            "",
        ]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)
    print(f"status={status} unsafe_hits={unsafe_hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
