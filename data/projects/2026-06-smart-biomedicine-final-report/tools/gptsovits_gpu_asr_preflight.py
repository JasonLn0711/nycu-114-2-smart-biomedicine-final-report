#!/usr/bin/env python3
"""GPU-only preflight for Smart Biomedicine GPT-SoVITS production.

This script intentionally fails if RTX 4090 / CUDA ASR is not usable. It does
not provide a CPU fallback because the production rule requires GPU execution.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_AUDIO = ROOT / "exports/smart-biomedicine-gpt-sovits/reference/ref_candidate_01_000009_12s.wav"
DEFAULT_MODEL = Path(
    "/home/jnclaw/.cache/huggingface/hub/models--SoybeanMilk--faster-whisper-Breeze-ASR-25/"
    "snapshots/85be11de5f67aaa6a92e931622f1c2b55cc1dd3a"
)
DEFAULT_PYTHON = Path("/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/bin/python")
CUDA_LIBS = [
    "/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/lib/python3.12/site-packages/nvidia/cublas/lib",
    "/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/lib/python3.12/site-packages/nvidia/cudnn/lib",
    "/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib",
]


def run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", default=str(DEFAULT_AUDIO), help="Reference WAV to transcribe for CUDA ASR smoke test.")
    parser.add_argument("--model", default=str(DEFAULT_MODEL), help="Local faster-whisper Breeze-ASR-25 model path.")
    parser.add_argument("--python", default=str(DEFAULT_PYTHON), help="Python interpreter with faster_whisper installed.")
    args = parser.parse_args()

    audio = Path(args.audio)
    model = Path(args.model)
    py = Path(args.python)

    if not audio.exists():
        return fail(f"audio file missing: {audio}")
    if not model.exists():
        return fail(f"Breeze-ASR-25 model path missing: {model}")
    if not py.exists():
        return fail(f"ASR Python runtime missing: {py}")

    smi = run([
        "nvidia-smi",
        "--query-gpu=name,index,memory.total,memory.free,driver_version",
        "--format=csv,noheader",
    ])
    if smi.returncode != 0:
        return fail("nvidia-smi failed", smi.stdout)
    if "RTX 4090" not in smi.stdout:
        return fail("RTX 4090 was not found; refusing CPU or non-4090 fallback", smi.stdout)

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"
    env["LD_LIBRARY_PATH"] = ":".join(CUDA_LIBS + [env.get("LD_LIBRARY_PATH", "")]).rstrip(":")

    code = f"""
from faster_whisper import WhisperModel
model = WhisperModel({str(model)!r}, device='cuda', compute_type='float16')
segments, info = model.transcribe({str(audio)!r}, beam_size=5, vad_filter=True, language='zh')
print('device=cuda')
print('model=breeze-asr-25')
print('language=' + str(info.language))
for s in segments:
    print(f'[{{s.start:.2f}}-{{s.end:.2f}}] {{s.text.strip()}}')
"""
    smoke = run([str(py), "-c", code], env=env)
    if smoke.returncode != 0:
        return fail("CUDA ASR smoke test failed; do not fall back to CPU", smoke.stdout)
    if "device=cuda" not in smoke.stdout:
        return fail("CUDA ASR smoke test did not prove CUDA execution", smoke.stdout)

    print("PASS: RTX 4090 and CUDA Breeze-ASR-25 smoke test succeeded")
    print(smi.stdout.strip())
    print(smoke.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
