#!/usr/bin/env python3
"""Report prompt-reference accept/reject/pending state and recommend next ASR gate target."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EXPORT = ROOT / "exports/smart-biomedicine-gpt-sovits"
REFERENCE = EXPORT / "reference"
DECISIONS = EXPORT / "qa/reference-decisions"
QUALITY_CSV = EXPORT / "qa/reference-quality/reference-quality-manifest.csv"
OUT = EXPORT / "qa/reference-decisions/reference-decision-status.md"
PREFERRED_LISTENING_ORDER = [
    "prompt_ref_candidate_04_000381_8p00s",
    "prompt_ref_candidate_01_000009_5p40s",
    "prompt_ref_candidate_02_000036_8p00s",
    "prompt_ref_candidate_03_000072_8p00s",
    "prompt_ref_candidate_05_000480_8p00s",
]


def read_quality() -> list[dict[str, str]]:
    if not QUALITY_CSV.exists():
        return []
    with QUALITY_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def decision_for(stem: str) -> tuple[str, Path | None]:
    accepted = DECISIONS / f"{stem}.accepted.md"
    rejected = DECISIONS / f"{stem}.rejected.md"
    if accepted.exists():
        return "accepted", accepted
    if rejected.exists():
        return "rejected", rejected
    return "pending", None


def reject_command(stem: str) -> str:
    return (
        "python3 data/projects/2026-06-smart-biomedicine-final-report/tools/"
        f"mark_reference_review_decision.py --candidate {stem} --decision rejected "
        '--notes "<why rejected by Breeze-ASR-25 transcript gate>" --ack-breeze-asr-25-cuda'
    )


def main() -> int:
    rows = []
    accepted_count = 0
    rejected_count = 0
    pending_candidates: list[tuple[float, str]] = []

    for row in read_quality():
        path = Path(row["file"])
        if not path.name.startswith("prompt_ref_candidate_"):
            continue
        stem = path.stem
        decision, marker = decision_for(stem)
        accepted_count += int(decision == "accepted")
        rejected_count += int(decision == "rejected")
        if decision == "pending":
            try:
                score = float(row.get("machine_score", "0") or 0)
            except ValueError:
                score = 0.0
            pending_candidates.append((score, stem))
        rows.append(
            {
                "stem": stem,
                "duration": row.get("duration_seconds", ""),
                "score": row.get("machine_score", ""),
                "near_clip": row.get("near_clip_ratio", ""),
                "silence": row.get("silence_ratio", ""),
                "decision": decision,
                "marker": marker,
            }
        )

    pending_stems = {stem for _, stem in pending_candidates}
    recommended = ""
    if pending_candidates and accepted_count == 0:
        recommended = next((stem for stem in PREFERRED_LISTENING_ORDER if stem in pending_stems), "")
        if not recommended:
            pending_candidates.sort(reverse=True)
            recommended = pending_candidates[0][1]
    if accepted_count > 1:
        next_action = "Resolve multiple accepted references; keep exactly one accepted marker."
    elif accepted_count == 1:
        next_action = "Accepted prompt reference exists; continue to formal chunk 01 generation."
    elif recommended:
        next_action = f"Run Breeze-ASR-25 transcript gate for `{recommended}` next; accept with exact transcript or reject with notes."
    else:
        next_action = "All prompt references are rejected or missing; extract new clean reference candidates."

    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Reference Decision Status",
        "",
        "This report separates machine quality ranking from the Breeze-ASR-25 transcript accept/reject gate.",
        "",
        f"- accepted_references: `{accepted_count}`",
        f"- rejected_references: `{rejected_count}`",
        f"- recommended_next_candidate: `{recommended or 'none'}`",
        f"- listening_order: `{' -> '.join(PREFERRED_LISTENING_ORDER)}`",
        f"- next_action: {next_action}",
        "",
        "| Candidate | Decision | Machine score | Duration | Near-clip ratio | Silence ratio | Marker |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        marker = str(row["marker"]) if row["marker"] else ""
        lines.append(
            f"| `{row['stem']}` | `{row['decision']}` | {row['score']} | {row['duration']} | "
            f"{row['near_clip']} | {row['silence']} | `{marker}` |"
        )
    lines.extend(
        [
            "",
            "## Reject Command Template",
            "",
            "Use this when Breeze-ASR-25 transcript matching or machine quality checks reject a candidate.",
            "",
        ]
    )
    for row in rows:
        if row["decision"] == "pending":
            lines.extend(["```bash", reject_command(row["stem"]), "```", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)
    print(f"accepted={accepted_count} rejected={rejected_count} recommended={recommended or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
