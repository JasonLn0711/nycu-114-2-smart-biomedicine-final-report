#!/usr/bin/env python3
"""Run a GPU-only GPT-SoVITS synthesis smoke test.

This is not a production chunk generator. It proves that the local
GPT-SoVITS runtime can load the v2 pretrained weights and synthesize a short
WAV on RTX 4090 CUDA. The reference transcript used here is still an ASR draft,
so the output must not be marked accepted for the final report.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNTIME = Path("/home/jnclaw/every_on_git_jnclaw/GPT-SoVITS")
SMOKE_ROOT = ROOT / "exports/smart-biomedicine-gpt-sovits/runtime-smoke"
REF_AUDIO = ROOT / "exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_01_000009_5p40s.wav"
REF_TEXT = SMOKE_ROOT / "ref_candidate_01_draft_prompt_text.txt"
TARGET_TEXT = SMOKE_ROOT / "gptsovits_cuda_smoke_target.txt"
OUTPUT_DIR = SMOKE_ROOT / "output"
OUTPUT_WAV = OUTPUT_DIR / "output.wav"
GPT_MODEL = RUNTIME / "GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt"
SOVITS_MODEL = RUNTIME / "GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s2G2333k.pth"


def run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=RUNTIME, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def require(path: Path) -> int:
    if not path.exists():
        return fail(f"required path missing: {path}")
    return 0


def cuda_lib_path() -> str:
    nvidia_root = RUNTIME / ".venv/lib/python3.11/site-packages/nvidia"
    libs = sorted(str(path) for path in nvidia_root.glob("*/lib") if path.is_dir())
    return ":".join(libs)


def main() -> int:
    for path in [RUNTIME / ".venv/bin/python", REF_AUDIO, REF_TEXT, TARGET_TEXT, GPT_MODEL, SOVITS_MODEL]:
        rc = require(path)
        if rc:
            return rc

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

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUT_WAV.exists():
        OUTPUT_WAV.unlink()

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
        str(RUNTIME / ".venv/bin/python"),
        "GPT_SoVITS/inference_cli.py",
        "--gpt_model",
        str(GPT_MODEL),
        "--sovits_model",
        str(SOVITS_MODEL),
        "--ref_audio",
        str(REF_AUDIO),
        "--ref_text",
        str(REF_TEXT),
        "--ref_language",
        "中文",
        "--target_text",
        str(TARGET_TEXT),
        "--target_language",
        "英文",
        "--output_path",
        str(OUTPUT_DIR),
    ]
    synth = run(cmd, env=env)
    if synth.returncode != 0:
        return fail("GPT-SoVITS CUDA synthesis smoke test failed", synth.stdout)
    if not OUTPUT_WAV.exists():
        return fail("GPT-SoVITS smoke command finished without output WAV", synth.stdout)

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_name,sample_rate,channels",
            "-show_entries",
            "format=duration,size",
            "-of",
            "default=nw=1:nk=0",
            str(OUTPUT_WAV),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if probe.returncode != 0:
        return fail("ffprobe failed on smoke output", probe.stdout)

    print("PASS: GPT-SoVITS CUDA synthesis smoke test succeeded")
    print(smi.stdout.strip())
    print(str(OUTPUT_WAV))
    print(probe.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
