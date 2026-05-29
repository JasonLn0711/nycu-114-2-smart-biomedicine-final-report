"""Resolve the single accepted GPT-SoVITS prompt reference."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/reference"
DECISIONS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-decisions"


@dataclass(frozen=True)
class AcceptedReference:
    stem: str
    wav: Path
    exact_transcript: Path
    marker: Path


def resolve_accepted_reference() -> AcceptedReference:
    markers = sorted(DECISIONS_DIR.glob("prompt_ref_candidate_*.accepted.md"))
    if not markers:
        raise RuntimeError(
            "no accepted reference marker found under "
            f"{DECISIONS_DIR}; run mark_reference_review_decision.py after human listening"
        )
    if len(markers) > 1:
        joined = "\n".join(str(path) for path in markers)
        raise RuntimeError("multiple accepted reference markers found; keep exactly one:\n" + joined)

    marker = markers[0]
    stem = marker.name.removesuffix(".accepted.md")
    wav = REFERENCE_DIR / f"{stem}.wav"
    exact = REFERENCE_DIR / f"{stem}.exact-transcript.txt"
    missing = [str(path) for path in [wav, exact, marker] if not path.exists()]
    if missing:
        raise RuntimeError("accepted reference is incomplete:\n" + "\n".join(missing))
    return AcceptedReference(stem=stem, wav=wav, exact_transcript=exact, marker=marker)
