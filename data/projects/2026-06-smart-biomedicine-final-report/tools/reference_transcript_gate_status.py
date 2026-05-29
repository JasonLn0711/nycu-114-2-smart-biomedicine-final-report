#!/usr/bin/env python3
"""Report exact-transcript and ASR-led decision status for prompt references."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/reference"
DECISIONS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-decisions"
OUT = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-transcript-gate.md"
BLOCKED_MARKERS = ["draft", "asr", "pending", "todo", "template", "<write exact transcript here>"]


def mark(ok: bool) -> str:
    return "PASS" if ok else "TODO"


def duration(path: Path) -> float | None:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if probe.returncode != 0:
        return None
    return float(probe.stdout.strip())


def exact_status(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    text = path.read_text(encoding="utf-8").strip()
    lowered = path.name.lower() + "\n" + text.lower()
    if not text:
        return False, "empty"
    for marker in BLOCKED_MARKERS:
        if marker in lowered:
            return False, f"contains `{marker}`"
    return True, "looks exact by filename/content gate"


def main() -> int:
    refs = sorted(REFERENCE_DIR.glob("prompt_ref_candidate_*.wav"))
    rows = []
    accepted_count = 0
    exact_count = 0
    for wav in refs:
        exact = REFERENCE_DIR / f"{wav.stem}.exact-transcript.txt"
        accepted = DECISIONS_DIR / f"{wav.stem}.accepted.md"
        rejected = DECISIONS_DIR / f"{wav.stem}.rejected.md"
        exact_ok, exact_note = exact_status(exact)
        exact_count += int(exact_ok)
        accepted_count += int(accepted.exists())
        dur = duration(wav)
        decision = "accepted" if accepted.exists() else "rejected" if rejected.exists() else "pending"
        rows.append((wav, dur, exact, exact_ok, exact_note, decision))

    out_lines = [
        "# Reference Transcript Gate",
        "",
        "This gate checks file-level evidence for the ASR-led prompt-reference workflow.",
        "",
        f"- prompt_references_found: `{len(refs)}`",
        f"- exact_transcripts_passing_file_gate: `{exact_count}/{len(refs)}`",
        f"- accepted_reference_markers: `{accepted_count}/{len(refs)}`",
        "",
        "| Reference | Duration | Exact transcript | Exact gate | Decision | Note |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for wav, dur, exact, exact_ok, exact_note, decision in rows:
        duration_text = f"{dur:.2f}s" if dur is not None else "unknown"
        out_lines.append(
            f"| `{wav.name}` | `{duration_text}` | `{exact}` | `{mark(exact_ok)}` | `{decision}` | {exact_note} |"
        )

    if accepted_count == 0:
        next_action = "Run Breeze-ASR-25 on the selected prompt reference, write the exact transcript, then record an accepted marker."
    elif accepted_count > 1:
        next_action = "Resolve multiple accepted references before formal generation."
    else:
        next_action = "Use the single accepted prompt reference for formal chunk generation."
    out_lines.extend(["", f"Next action: {next_action}", ""])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out_lines), encoding="utf-8")
    print(OUT)
    print(f"prompt_references={len(refs)} exact={exact_count}/{len(refs)} accepted={accepted_count}/{len(refs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
