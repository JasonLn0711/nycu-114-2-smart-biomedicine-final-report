#!/usr/bin/env python3
"""Build quantitative QA metadata for GPT-SoVITS reference candidates.

This is not a listening substitute. It gives the human reviewer a quick view of
duration, RMS, peak, near-clipping risk, and silence ratio before choosing a
prompt reference.
"""

from __future__ import annotations

from array import array
import csv
import wave
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/reference"
QA_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-quality"
CSV_OUT = QA_DIR / "reference-quality-manifest.csv"
MD_OUT = QA_DIR / "reference-quality-manifest.md"


@dataclass
class AudioFacts:
    path: Path
    duration: float
    sample_rate: int
    channels: int
    sample_width: int
    rms: int
    peak: int
    near_clip_ratio: float
    silence_ratio: float
    score: float
    recommendation: str


def audio_facts(path: Path) -> AudioFacts:
    with wave.open(str(path), "rb") as wav:
        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        frames = wav.readframes(wav.getnframes())
        frame_count = wav.getnframes()

    duration = frame_count / sample_rate if sample_rate else 0.0
    if channels != 1 or sample_width != 2:
        raise ValueError(f"expected mono 16-bit WAV: {path}")

    samples = array("h")
    samples.frombytes(frames)
    if samples.itemsize != sample_width:
        raise ValueError(f"unexpected sample width for native array: {path}")
    total_samples = len(samples)
    rms = int((sum(value * value for value in samples) / total_samples) ** 0.5) if total_samples else 0
    peak = max((abs(value) for value in samples), default=0)
    near_clip = 0
    silent = 0
    silence_threshold = 500
    near_clip_threshold = 30000
    for value in samples:
        abs_value = abs(value)
        if abs_value >= near_clip_threshold:
            near_clip += 1
        if abs_value <= silence_threshold:
            silent += 1
    near_clip_ratio = near_clip / total_samples if total_samples else 0.0
    silence_ratio = silent / total_samples if total_samples else 0.0

    score = 100.0
    score -= min(35.0, near_clip_ratio * 2500.0)
    score -= min(25.0, max(0.0, silence_ratio - 0.25) * 100.0)
    score -= 12.0 if duration < 3.0 or duration > 10.0 else 0.0
    score -= 8.0 if peak >= 32760 else 0.0
    score = max(0.0, score)

    if duration < 3.0 or duration > 10.0:
        recommendation = "review-only; not prompt-mode length"
    elif near_clip_ratio > 0.010:
        recommendation = "backup only; near-clipping risk"
    elif silence_ratio > 0.40:
        recommendation = "backup only; high silence ratio"
    elif score >= 80:
        recommendation = "strong prompt candidate pending human transcript"
    else:
        recommendation = "usable only after careful listening"

    return AudioFacts(
        path=path,
        duration=duration,
        sample_rate=sample_rate,
        channels=channels,
        sample_width=sample_width,
        rms=rms,
        peak=peak,
        near_clip_ratio=near_clip_ratio,
        silence_ratio=silence_ratio,
        score=score,
        recommendation=recommendation,
    )


def main() -> int:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    wavs = sorted(REFERENCE_DIR.glob("prompt_ref_candidate_*.wav")) + sorted(REFERENCE_DIR.glob("ref_candidate_*.wav"))
    rows = [audio_facts(path) for path in wavs]
    rows.sort(key=lambda row: (not row.path.name.startswith("prompt_ref"), -row.score, row.path.name))

    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "file",
                "duration_seconds",
                "sample_rate",
                "channels",
                "rms",
                "peak",
                "near_clip_ratio",
                "silence_ratio",
                "machine_score",
                "recommendation",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    str(row.path),
                    f"{row.duration:.3f}",
                    row.sample_rate,
                    row.channels,
                    row.rms,
                    row.peak,
                    f"{row.near_clip_ratio:.6f}",
                    f"{row.silence_ratio:.6f}",
                    f"{row.score:.1f}",
                    row.recommendation,
                ]
            )

    md = [
        "# Reference Quality Manifest",
        "",
        "This manifest is machine QA only. Human listening and exact transcript verification still control production acceptance.",
        "",
        "| File | Duration | RMS | Peak | Near-clip ratio | Silence ratio | Score | Recommendation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        md.append(
            "| "
            f"`{row.path.name}` | "
            f"`{row.duration:.2f}s` | "
            f"`{row.rms}` | "
            f"`{row.peak}` | "
            f"`{row.near_clip_ratio:.4f}` | "
            f"`{row.silence_ratio:.4f}` | "
            f"`{row.score:.1f}` | "
            f"{row.recommendation} |"
        )
    md.extend(
        [
            "",
            "## Operating Rule",
            "",
            "- Prefer prompt-ready `3-10s` WAVs with high score only after listening.",
            "- Reject any candidate whose exact transcript cannot be verified.",
            "- Treat near-clipping and high silence as review warnings, not automatic acceptance.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(md), encoding="utf-8")
    print(MD_OUT)
    print(CSV_OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
