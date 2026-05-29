#!/usr/bin/env python3
"""Preflight the RTX 5080-only BreezyVoice chunk 01 production route."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
SOURCE = PROJECT / "breezyvoice-narration-chunks-v1.md"
BREEZY_RUNTIME = Path("/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/BreezyVoice")
BREEZY_PYTHON = Path(
    "/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/breezyvoice/runtime/v1/venv/bin/python"
)
PROMPT_AUDIO = Path(
    "/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/breezyvoice/prompts/v1/jason_reference.wav"
)
ASR_MODEL = Path(
    "/home/jnln3799/.cache/huggingface/hub/models--SoybeanMilk--faster-whisper-Breeze-ASR-25/"
    "snapshots/85be11de5f67aaa6a92e931622f1c2b55cc1dd3a"
)
ASR_PYTHON = Path("/home/jnln3799/.cache/uroprevisit-asr-venv/bin/python")
OUT = ROOT / "exports/smart-biomedicine-breezyvoice/qa/preflight/chunk01-preflight.json"
CHUNK_ID = "sbm_tts_01_opening"
REQUIRED_PHRASES = [
    "Human staff check the draft",
    "Human staff can correct it",
    "Human staff can reject it",
    "The draft is checked before any care decision",
    "The doctor keeps the final authority",
    "I am not asking the system to make a diagnosis",
    "I am not proposing automatic scoring",
    "I am not deciding patient priority",
    "I am not proposing a treatment recommendation",
    "I am proposing a step by step process",
    "The system creates a review screen",
    "Human staff check the screen",
    "The doctor makes the medical decision",
]
UNSTABLE_PHRASES = [
    "staff review",
    "before it influences care",
    "practical process",
    "speech intake to clinician summary",
    "transcribed",
    "summarized",
    "the clinician makes the care decision",
]


def run(cmd: list[str], env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)


def fail(message: str, payload: dict[str, object]) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    return 1


def source_text(source_file: Path, chunk_id: str) -> str:
    text = source_file.read_text(encoding="utf-8")
    match = re.search(rf"^###\s+{re.escape(chunk_id)}\n(.*?)(?=^###\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    block = match.group(1)
    text_match = re.search(r"```text\n(.*?)\n```", block, flags=re.DOTALL)
    return text_match.group(1).strip() if text_match else ""


def cuda_lib_path(runtime: Path, py: Path) -> str:
    candidates = [
        runtime / ".venv/lib/python3.10/site-packages/nvidia",
        py.parents[1] / "lib/python3.10/site-packages/nvidia",
        py.parents[1] / "lib/python3.12/site-packages/nvidia",
    ]
    nvidia_root = next((path for path in candidates if path.exists()), candidates[0])
    libs = sorted(str(path) for path in nvidia_root.glob("*/lib") if path.is_dir())
    return ":".join(libs)


def breeze_runtime_probe(py: Path, runtime: Path) -> subprocess.CompletedProcess[str]:
    code = """
import onnxruntime as ort
import torch
print("torch_cuda=" + str(torch.cuda.is_available()))
print("torch_device=" + (torch.cuda.get_device_name(0) if torch.cuda.is_available() else ""))
print("ort_providers=" + ",".join(ort.get_available_providers()))
if not torch.cuda.is_available():
    raise SystemExit("PyTorch CUDA unavailable")
if "CUDAExecutionProvider" not in ort.get_available_providers():
    raise SystemExit("ONNX Runtime CUDAExecutionProvider unavailable")
"""
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"
    env["PYTHONUTF8"] = "1"
    env["LD_LIBRARY_PATH"] = ":".join(
        part for part in [cuda_lib_path(runtime, py), env.get("LD_LIBRARY_PATH", "")] if part
    )
    return run([str(py), "-c", code], env=env, cwd=runtime)


def asr_runtime_probe(py: Path, model: Path) -> subprocess.CompletedProcess[str]:
    code = f"""
from faster_whisper import WhisperModel
model = WhisperModel({str(model)!r}, device='cuda', compute_type='float16')
print('device=cuda')
print('model=breeze-asr-25')
"""
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"
    return run([str(py), "-c", code], env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-file", type=Path, default=SOURCE)
    parser.add_argument("--breezy-runtime", type=Path, default=BREEZY_RUNTIME)
    parser.add_argument("--breezy-python", type=Path, default=BREEZY_PYTHON)
    parser.add_argument("--prompt-audio", type=Path, default=PROMPT_AUDIO)
    parser.add_argument("--asr-model", type=Path, default=ASR_MODEL)
    parser.add_argument("--asr-python", type=Path, default=ASR_PYTHON)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--required-gpu-name", default="RTX 5080")
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Validate only the repaired chunk 01 source text; do not require RTX 5080/runtime paths.",
    )
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    text = source_text(args.source_file, CHUNK_ID) if args.source_file.exists() else ""
    missing_phrases = [phrase for phrase in REQUIRED_PHRASES if phrase.lower() not in text.lower()]
    present_unstable_phrases = [phrase for phrase in UNSTABLE_PHRASES if phrase.lower() in text.lower()]
    source_ok = bool(text) and not missing_phrases and not present_unstable_phrases
    paths = {
        "source_file": args.source_file,
        "breezy_runtime": args.breezy_runtime,
        "breezy_python": args.breezy_python,
        "breezy_single_inference": args.breezy_runtime / "single_inference.py",
        "prompt_audio": args.prompt_audio,
        "asr_model": args.asr_model,
        "asr_python": args.asr_python,
    }
    path_status = {name: path.exists() for name, path in paths.items()}
    smi = run([
        "nvidia-smi",
        "--query-gpu=name,index,memory.total,memory.free,driver_version",
        "--format=csv,noheader",
    ])
    gpu_ok = smi.returncode == 0 and args.required_gpu_name in smi.stdout

    breezy_probe = None
    asr_probe = None
    if gpu_ok and all(path_status.values()) and source_ok:
        breezy_probe = breeze_runtime_probe(args.breezy_python, args.breezy_runtime)
        asr_probe = asr_runtime_probe(args.asr_python, args.asr_model)

    payload = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "chunk_id": CHUNK_ID,
        "required_gpu_name": args.required_gpu_name,
        "nvidia_smi_returncode": smi.returncode,
        "nvidia_smi": smi.stdout.strip(),
        "gpu_ok": gpu_ok,
        "path_status": path_status,
        "source_text_characters": len(text),
        "missing_required_phrases": missing_phrases,
        "present_unstable_phrases": present_unstable_phrases,
        "source_ok": source_ok,
        "source_only": args.source_only,
        "breezy_runtime_probe_returncode": breezy_probe.returncode if breezy_probe else None,
        "breezy_runtime_probe": breezy_probe.stdout.strip() if breezy_probe else "",
        "asr_runtime_probe_returncode": asr_probe.returncode if asr_probe else None,
        "asr_runtime_probe": asr_probe.stdout.strip() if asr_probe else "",
    }
    payload["preflight_ok"] = bool(
        gpu_ok
        and all(path_status.values())
        and source_ok
        and breezy_probe
        and breezy_probe.returncode == 0
        and asr_probe
        and asr_probe.returncode == 0
    )

    if args.write_report:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.source_only:
        if not source_ok:
            return fail("BreezyVoice chunk 01 source text is not ready for generation", payload)
        print(f"PASS: BreezyVoice chunk 01 source text is ready for {args.required_gpu_name} preflight")
        return 0
    if not payload["preflight_ok"]:
        return fail("BreezyVoice chunk 01 preflight is not ready for generation", payload)
    print(f"PASS: BreezyVoice chunk 01 preflight is ready for {args.required_gpu_name} generation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
