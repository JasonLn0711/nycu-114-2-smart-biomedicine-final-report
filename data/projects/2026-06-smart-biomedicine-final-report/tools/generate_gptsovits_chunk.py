#!/usr/bin/env python3
"""Generate one accepted GPT-SoVITS narration chunk on RTX 4090 CUDA.

This production helper intentionally refuses ASR draft prompt text. First
human-verify the selected reference transcript, then pass that exact transcript
file with --ref-text.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime


ROOT = Path(__file__).resolve().parents[4]
RUNTIME = Path("/home/jnclaw/every_on_git_jnclaw/GPT-SoVITS")
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
DEFAULT_TEXT_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/chunk-text"
DEFAULT_OUTPUT_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks"
LOG_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/experiment-logs"
GENERATION_JSONL = LOG_DIR / "chunk-generations.jsonl"
GPT_MODEL = RUNTIME / "GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt"
SOVITS_MODEL = RUNTIME / "GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s2G2333k.pth"


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def run(cmd: list[str], cwd: Path = RUNTIME, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)


def append_jsonl(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def cuda_lib_path() -> str:
    nvidia_root = RUNTIME / ".venv/lib/python3.11/site-packages/nvidia"
    libs = sorted(str(path) for path in nvidia_root.glob("*/lib") if path.is_dir())
    return ":".join(libs)


def wav_duration(path: Path) -> float:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if probe.returncode != 0:
        raise RuntimeError(probe.stdout)
    return float(probe.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-id", required=True, help="Chunk id, for example sbm_tts_01_opening.")
    parser.add_argument("--ref-audio", required=True, help="Human-accepted GPT-SoVITS prompt WAV, 3-10 seconds.")
    parser.add_argument("--ref-text", required=True, help="Human-verified exact transcript for the prompt WAV.")
    parser.add_argument("--text-dir", default=str(DEFAULT_TEXT_DIR), help="Directory holding exported chunk .txt files.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for generated chunk WAVs.")
    parser.add_argument("--ref-language", default="中文", choices=["中文", "英文", "日文"])
    parser.add_argument(
        "--target-language",
        default="英文",
        choices=["中文", "英文", "日文", "中英混合", "日英混合", "多语种混合"],
    )
    args = parser.parse_args()

    py = RUNTIME / ".venv/bin/python"
    ref_audio = Path(args.ref_audio).resolve()
    ref_text = Path(args.ref_text).resolve()
    target_text = (Path(args.text_dir) / f"{args.chunk_id}.txt").resolve()
    output_dir = Path(args.output_dir).resolve()
    temp_dir = output_dir / ".tmp-gptsovits"
    temp_output = temp_dir / "output.wav"
    final_output = output_dir / f"{args.chunk_id}.wav"

    for path in [py, GPT_MODEL, SOVITS_MODEL, ref_audio, ref_text, target_text]:
        if not path.exists():
            return fail(f"required path missing: {path}")

    lower_ref_text_name = ref_text.name.lower()
    if "draft" in lower_ref_text_name or "asr" in lower_ref_text_name:
        return fail("ref text appears to be a draft; use a human-verified exact transcript file")

    try:
        duration = wav_duration(ref_audio)
    except RuntimeError as exc:
        return fail("could not inspect reference WAV duration", str(exc))
    if not 3.0 <= duration <= 10.0:
        return fail(f"reference WAV must be 3-10 seconds for GPT-SoVITS prompt mode; got {duration:.2f}s")

    smi = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,index,memory.total,memory.free,driver_version", "--format=csv,noheader"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if smi.returncode != 0:
        return fail("nvidia-smi failed", smi.stdout)
    if "RTX 4090" not in smi.stdout:
        return fail("RTX 4090 was not found; refusing CPU or non-4090 fallback", smi.stdout)

    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    if temp_output.exists():
        temp_output.unlink()

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"
    env["_CUDA_VISIBLE_DEVICES"] = "0"
    env["is_half"] = "True"
    env["version"] = "v2"
    env["PYTHONPATH"] = ".:GPT_SoVITS"
    env["LD_LIBRARY_PATH"] = ":".join(
        part for part in [cuda_lib_path(), env.get("LD_LIBRARY_PATH", "")] if part
    )

    cmd = [
        str(py),
        "GPT_SoVITS/inference_cli.py",
        "--gpt_model",
        str(GPT_MODEL),
        "--sovits_model",
        str(SOVITS_MODEL),
        "--ref_audio",
        str(ref_audio),
        "--ref_text",
        str(ref_text),
        "--ref_language",
        args.ref_language,
        "--target_text",
        str(target_text),
        "--target_language",
        args.target_language,
        "--output_path",
        str(temp_dir),
    ]
    synth = run(cmd, env=env)
    if synth.returncode != 0:
        return fail("GPT-SoVITS chunk generation failed", synth.stdout)
    if not temp_output.exists():
        return fail("GPT-SoVITS finished without output WAV", synth.stdout)

    shutil.move(str(temp_output), str(final_output))
    append_jsonl(
        GENERATION_JSONL,
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "event": "chunk_generation",
            "chunk_id": args.chunk_id,
            "runtime": "RTX 4090 CUDA only",
            "ref_audio": str(ref_audio),
            "ref_text": str(ref_text),
            "target_text": str(target_text),
            "output_wav": str(final_output),
            "target_language": args.target_language,
            "ref_language": args.ref_language,
            "nvidia_smi": smi.stdout.strip(),
        },
    )
    print(f"PASS: generated {args.chunk_id} on RTX 4090 CUDA")
    print(smi.stdout.strip())
    print(final_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
