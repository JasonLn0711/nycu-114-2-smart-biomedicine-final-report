#!/usr/bin/env python3
"""Generate Smart Biomedicine narration v2 with F5-TTS on RTX 5080 only."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
import wave
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
SOURCE = PROJECT / "breezyvoice-narration-chunks-v1.md"
EXPORT = ROOT / "exports/smart-biomedicine-f5-tts"
DEFAULT_REF_AUDIO = EXPORT / "reference/sbm_tts_01_opening_ref_14s.wav"
DEFAULT_REF_TEXT = (
    "Hello everyone. I am Jason. "
    "Today my report is about patient voice intake before a clinical visit. "
    "The goal is to turn patient speech into a clear draft summary for a clinician."
)
CHUNK_IDS = [
    "sbm_tts_01_opening",
    "sbm_tts_02_markdown_format",
    "sbm_tts_03_definitions",
    "sbm_tts_04_workflow_problem",
    "sbm_tts_05_speech_to_summary",
    "sbm_tts_06_evidence_landscape",
    "sbm_tts_07_hager_boundary",
    "sbm_tts_08_lang1_overview",
    "sbm_tts_09_lang1_results",
    "sbm_tts_10_architecture",
    "sbm_tts_11_scope_controls",
    "sbm_tts_12_synthetic_example",
    "sbm_tts_13_validation_risk",
    "sbm_tts_14_closing",
]


def parse_chunks(source: Path) -> dict[str, str]:
    text = source.read_text(encoding="utf-8")
    chunks = {
        chunk_id: body.strip()
        for chunk_id, body in re.findall(r"### (sbm_tts_\d+_[^\n]+).*?```text\n(.*?)\n```", text, flags=re.S)
    }
    missing = [chunk_id for chunk_id in CHUNK_IDS if chunk_id not in chunks]
    if missing:
        raise SystemExit(f"missing expected chunks in {source}: {', '.join(missing)}")
    return chunks


def require_rtx5080_cuda() -> dict[str, str | int | bool]:
    import torch

    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available; refusing CPU inference.")
    index = torch.cuda.current_device()
    name = torch.cuda.get_device_name(index)
    if "RTX 5080" not in name:
        raise SystemExit(f"Active CUDA device is {name!r}; expected RTX 5080. Refusing inference.")
    props = torch.cuda.get_device_properties(index)
    torch.zeros(1, device=f"cuda:{index}") + 1
    return {
        "cuda_available": True,
        "cuda_device_index": index,
        "cuda_device_name": name,
        "cuda_capability": f"{props.major}.{props.minor}",
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda or "",
    }


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def prepare_reference(ref_audio: Path) -> None:
    if ref_audio.exists():
        return
    source = ROOT / "exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_01_opening.wav"
    if not source.exists():
        raise SystemExit(f"missing reference source WAV: {source}")
    ref_audio.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-i",
            str(source),
            "-t",
            "14.0",
            "-ac",
            "1",
            "-ar",
            "24000",
            str(ref_audio),
        ]
    )


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def stitch(paths: list[Path], output: Path, silence: float) -> float:
    output.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 24000
    with open(output.parent / "concat-v2.txt", "w", encoding="utf-8") as handle:
        for index, path in enumerate(paths):
            handle.write(f"file '{path.resolve()}'\n")
            if index != len(paths) - 1:
                silence_path = output.parent / "silence-0.5s.wav"
                if not silence_path.exists():
                    run(
                        [
                            "ffmpeg",
                            "-hide_banner",
                            "-y",
                            "-f",
                            "lavfi",
                            "-i",
                            f"anullsrc=r={sample_rate}:cl=mono",
                            "-t",
                            str(silence),
                            "-sample_fmt",
                            "s16",
                            str(silence_path),
                        ]
                    )
                handle.write(f"file '{silence_path.resolve()}'\n")
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(output.parent / "concat-v2.txt"),
            "-c",
            "copy",
            str(output),
        ]
    )
    return sum(wav_duration(path) for path in paths) + silence * (len(paths) - 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(SOURCE))
    parser.add_argument("--output-root", default=str(EXPORT))
    parser.add_argument("--ref-audio", default=str(DEFAULT_REF_AUDIO))
    parser.add_argument("--ref-text", default=DEFAULT_REF_TEXT)
    parser.add_argument("--seed", type=int, default=2026052802)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--nfe-step", type=int, default=32)
    parser.add_argument("--smoke", action="store_true", help="Render only chunk 01 for GPU validation.")
    args = parser.parse_args()

    gpu = require_rtx5080_cuda()
    chunks = parse_chunks(Path(args.source))
    output_root = Path(args.output_root)
    chunk_dir = output_root / "chunks"
    text_dir = output_root / "chunk-text"
    qa_dir = output_root / "qa"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)
    ref_audio = Path(args.ref_audio)
    prepare_reference(ref_audio)

    from f5_tts.api import F5TTS

    started = datetime.now().astimezone().isoformat(timespec="seconds")
    t0 = time.time()
    f5tts = F5TTS(model="F5TTS_v1_Base", device="cuda:0")
    selected = CHUNK_IDS[:1] if args.smoke else CHUNK_IDS
    rows = []
    paths = []
    for offset, chunk_id in enumerate(selected):
        text = chunks[chunk_id]
        text_path = text_dir / f"{chunk_id}.txt"
        wav_path = chunk_dir / f"{chunk_id}.wav"
        text_path.write_text(text + "\n", encoding="utf-8")
        print(f"generating {chunk_id} on {gpu['cuda_device_name']}", flush=True)
        f5tts.infer(
            ref_file=str(ref_audio),
            ref_text=args.ref_text,
            gen_text=text,
            file_wave=str(wav_path),
            seed=args.seed + offset,
            speed=args.speed,
            nfe_step=args.nfe_step,
            remove_silence=False,
        )
        duration = wav_duration(wav_path)
        rows.append(
            {
                "chunk_id": chunk_id,
                "text_path": str(text_path),
                "wav_path": str(wav_path),
                "duration_seconds": f"{duration:.3f}",
                "seed": str(args.seed + offset),
            }
        )
        paths.append(wav_path)

    stitched_duration = None
    stitched_path = None
    if not args.smoke:
        stitched_path = output_root / "stitching/smart-biomedicine-final-report-f5tts-v2.wav"
        stitched_duration = stitch(paths, stitched_path, silence=0.5)

    manifest = {
        "started_at": started,
        "completed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time() - t0, 3),
        "model": "F5TTS_v1_Base",
        "source": str(Path(args.source)),
        "reference_audio": str(ref_audio),
        "reference_text": args.ref_text,
        "seed_base": args.seed,
        "speed": args.speed,
        "nfe_step": args.nfe_step,
        "smoke": args.smoke,
        "gpu": gpu,
        "chunks": rows,
        "stitched_wav": str(stitched_path) if stitched_path else "",
        "stitched_duration_seconds": round(stitched_duration, 3) if stitched_duration is not None else None,
    }
    (qa_dir / "f5tts-v2-generation-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (qa_dir / "f5tts-v2-chunks.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["chunk_id", "text_path", "wav_path", "duration_seconds", "seed"])
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"gpu": gpu, "chunks": len(rows), "stitched_wav": manifest["stitched_wav"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
