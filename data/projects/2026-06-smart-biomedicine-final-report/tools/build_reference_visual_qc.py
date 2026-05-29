#!/usr/bin/env python3
"""Build waveform and spectrogram images for prompt-reference review."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE = ROOT / "exports/smart-biomedicine-gpt-sovits/reference"
OUT_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/reference-visual-qc"
MD_OUT = OUT_DIR / "reference-visual-qc.md"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def build_images(wav: Path) -> tuple[Path, Path]:
    waveform = OUT_DIR / f"{wav.stem}.waveform.png"
    spectrogram = OUT_DIR / f"{wav.stem}.spectrogram.png"
    wave = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(wav),
            "-filter_complex",
            "showwavespic=s=1200x220:colors=0x2563eb",
            "-frames:v",
            "1",
            str(waveform),
        ]
    )
    if wave.returncode != 0:
        raise RuntimeError(wave.stdout)
    spec = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(wav),
            "-lavfi",
            "showspectrumpic=s=1200x320:legend=disabled",
            str(spectrogram),
        ]
    )
    if spec.returncode != 0:
        raise RuntimeError(spec.stdout)
    return waveform, spectrogram


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    refs = sorted(REFERENCE.glob("prompt_ref_candidate_*.wav"))
    rows = []
    for wav in refs:
        waveform, spectrogram = build_images(wav)
        rows.append((wav, waveform, spectrogram))

    md = [
        "# Reference Visual QC",
        "",
        "These images support human listening. They do not prove transcript correctness or audio acceptance.",
        "",
        "| Reference | Waveform | Spectrogram |",
        "| --- | --- | --- |",
    ]
    for wav, waveform, spectrogram in rows:
        md.append(f"| `{wav.name}` | `{waveform}` | `{spectrogram}` |")
    md.append("")
    MD_OUT.write_text("\n".join(md), encoding="utf-8")
    print(MD_OUT)
    print(f"visual_qc_refs={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
