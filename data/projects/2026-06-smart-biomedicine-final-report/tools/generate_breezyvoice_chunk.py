#!/usr/bin/env python3
"""Generate one BreezyVoice narration chunk on the required RTX 5080 path."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
DEFAULT_SOURCE = PROJECT / "breezyvoice-narration-chunks-v1.md"
DEFAULT_RUNTIME = Path("/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/BreezyVoice")
DEFAULT_OUTPUT_DIR = ROOT / "exports/smart-biomedicine-breezyvoice/chunks"
DEFAULT_LOG_DIR = ROOT / "exports/smart-biomedicine-breezyvoice/qa/experiment-logs"
DEFAULT_PYTHON = Path(
    "/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/breezyvoice/runtime/v1/venv/bin/python"
)
DEFAULT_PROMPT_AUDIO = Path(
    "/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/breezyvoice/prompts/v1/jason_reference.wav"
)
DEFAULT_PROMPT_TEXT = (
    "好朋友,先開始錄音,先有聽到嗎? 好,各位人各位長官,各位先進各位醫療與資訊領域的夥伴大家好 "
    "今天很榮幸有機會跟大家分享一個聽起來很有一點硬 但是實際上每天來都在醫院80的體目 "
    "也就是醫療設備與醫療資訊系統的自然要求"
)
DEFAULT_MODEL = "MediaTek-Research/BreezyVoice-300M"
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


def fail(message: str, detail: str = "") -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    return 1


def run(cmd: list[str], env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)


def run_capture(cmd: list[str]) -> str:
    result = run(cmd, cwd=ROOT)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def tracked_worktree_changes() -> str:
    return run_capture(["git", "status", "--porcelain", "--untracked-files=no"])


def refresh_origin_main() -> subprocess.CompletedProcess[str]:
    return run(["git", "fetch", "origin", "main"], cwd=ROOT)


def git_commit() -> str:
    return run_capture(["git", "rev-parse", "HEAD"])


def origin_main_commit() -> str:
    return run_capture(["git", "rev-parse", "origin/main"])


def append_jsonl(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def source_text(source_file: Path, chunk_id: str) -> str:
    text = source_file.read_text(encoding="utf-8")
    match = re.search(rf"^###\s+{re.escape(chunk_id)}\n(.*?)(?=^###\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    block = match.group(1)
    text_match = re.search(r"```text\n(.*?)\n```", block, flags=re.DOTALL)
    return text_match.group(1).strip() if text_match else ""


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def nvidia_smi(required_gpu_name: str) -> tuple[int, str]:
    smi = run([
        "nvidia-smi",
        "--query-gpu=name,index,memory.total,memory.free,driver_version",
        "--format=csv,noheader",
    ])
    if smi.returncode != 0:
        return smi.returncode, smi.stdout
    if required_gpu_name not in smi.stdout:
        return 2, smi.stdout
    return 0, smi.stdout


def cuda_lib_path(runtime: Path, py: Path) -> str:
    candidates = [
        runtime / ".venv/lib/python3.10/site-packages/nvidia",
        py.parents[1] / "lib/python3.10/site-packages/nvidia",
        py.parents[1] / "lib/python3.12/site-packages/nvidia",
    ]
    nvidia_root = next((path for path in candidates if path.exists()), candidates[0])
    libs = sorted(str(path) for path in nvidia_root.glob("*/lib") if path.is_dir())
    return ":".join(libs)


def runtime_probe(py: Path, runtime: Path) -> subprocess.CompletedProcess[str]:
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


def wav_facts(path: Path) -> str:
    probe = run([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=codec_name,sample_rate,channels",
        "-show_entries",
        "format=duration,size",
        "-of",
        "default=nw=1:nk=0",
        str(path),
    ])
    if probe.returncode != 0:
        raise RuntimeError(probe.stdout)
    return probe.stdout.strip()


def synthesis_script() -> str:
    return r"""
import os
import sys

import soundfile as sf
import torch
import torchaudio

runtime = os.environ["BV_RUNTIME"]
sys.path.insert(0, runtime)

if not hasattr(torchaudio, "set_audio_backend"):
    torchaudio.set_audio_backend = lambda *_args, **_kwargs: None

import single_inference as single_inference_mod


def load_wav_with_soundfile(wav: str, target_sr: int):
    data, sample_rate = sf.read(wav, dtype="float32", always_2d=True)
    speech = torch.from_numpy(data.T).float()
    speech = speech.mean(dim=0, keepdim=True)
    if sample_rate != target_sr:
        if sample_rate < target_sr:
            raise ValueError(f"wav sample rate {sample_rate} must be at least {target_sr}")
        speech = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)(speech)
    return speech


def save_wav_with_soundfile(path: str, waveform, sample_rate: int, **_kwargs):
    audio = waveform.detach().cpu()
    if audio.ndim == 2:
        audio = audio.squeeze(0)
    sf.write(path, audio.numpy(), sample_rate, subtype="PCM_16")


single_inference_mod.load_wav = load_wav_with_soundfile
single_inference_mod.torchaudio.save = save_wav_with_soundfile

cosyvoice = single_inference_mod.CustomCosyVoice(os.environ["BV_MODEL_PATH"])
converter = single_inference_mod.G2PWConverter()
single_inference_mod.single_inference(
    os.environ["BV_PROMPT_AUDIO"],
    os.environ["BV_CONTENT"],
    os.environ["BV_OUTPUT_WAV"],
    cosyvoice,
    converter,
    os.environ["BV_PROMPT_TEXT"],
)
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-id", required=True, choices=CHUNK_IDS)
    parser.add_argument("--source-file", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--prompt-audio", type=Path, default=DEFAULT_PROMPT_AUDIO)
    parser.add_argument("--prompt-text", default=DEFAULT_PROMPT_TEXT)
    parser.add_argument("--model-path", default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--required-gpu-name", default="RTX 5080")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--allow-dirty-checkout",
        action="store_true",
        help="Allow tracked local modifications. Avoid this for production WAV evidence.",
    )
    parser.add_argument(
        "--allow-unpushed-checkout",
        action="store_true",
        help="Allow HEAD to differ from origin/main. Avoid this for production WAV evidence.",
    )
    parser.add_argument(
        "--skip-remote-refresh",
        action="store_true",
        help="Skip git fetch origin main before comparing HEAD with origin/main. Use only for offline debugging.",
    )
    args = parser.parse_args()

    current_commit = git_commit()
    dirty = tracked_worktree_changes()
    if dirty and not args.allow_dirty_checkout:
        return fail(
            "tracked worktree changes found; refusing BreezyVoice generation from an uncommitted checkout",
            dirty,
        )
    if not args.skip_remote_refresh:
        remote_refresh = refresh_origin_main()
        if remote_refresh.returncode != 0:
            return fail("could not refresh origin/main before BreezyVoice generation", remote_refresh.stdout)
    remote_commit = origin_main_commit()
    if remote_commit != current_commit and not args.allow_unpushed_checkout:
        return fail(
            "HEAD does not match origin/main; refusing BreezyVoice generation from an unpushed or stale checkout",
            f"head={current_commit}\norigin_main={remote_commit}",
        )

    smi_status, smi_output = nvidia_smi(args.required_gpu_name)
    if smi_status == 1:
        return fail("nvidia-smi failed", smi_output)
    if smi_status == 2:
        return fail(f"{args.required_gpu_name} was not found; refusing CPU or non-matching GPU fallback", smi_output)

    runtime = args.runtime.resolve()
    # Keep the venv launcher path intact. Resolving the symlink can jump to the
    # base uv Python binary and lose the venv site-packages.
    py = args.python if args.python else runtime / ".venv/bin/python"
    single_inference = runtime / "single_inference.py"
    output_dir = args.output_dir.resolve()
    output_wav = output_dir / f"{args.chunk_id}.wav"

    for path in [args.source_file, runtime, py, single_inference, args.prompt_audio]:
        if not path.exists():
            return fail(f"required path missing: {path}")
    if output_wav.exists() and not args.overwrite:
        return fail(f"target WAV already exists; use --overwrite only after intentional rejection: {output_wav}")

    text = source_text(args.source_file, args.chunk_id)
    if not text:
        return fail(f"chunk text not found in source file: {args.chunk_id}", str(args.source_file))
    text_hash = source_hash(text)

    probe = runtime_probe(py, runtime)
    if probe.returncode != 0:
        return fail("BreezyVoice runtime CUDA probe failed; do not fall back to CPU", probe.stdout)

    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"
    env["PYTHONUTF8"] = "1"
    env["LD_LIBRARY_PATH"] = ":".join(
        part for part in [cuda_lib_path(runtime, py), env.get("LD_LIBRARY_PATH", "")] if part
    )
    env["BV_RUNTIME"] = str(runtime)
    env["BV_PROMPT_AUDIO"] = str(args.prompt_audio.resolve())
    env["BV_PROMPT_TEXT"] = args.prompt_text
    env["BV_CONTENT"] = text
    env["BV_OUTPUT_WAV"] = str(output_wav)
    env["BV_MODEL_PATH"] = args.model_path
    cmd = [str(py), "-c", synthesis_script()]
    synth = run(cmd, env=env, cwd=runtime)
    if synth.returncode != 0:
        return fail("BreezyVoice chunk generation failed", synth.stdout)
    if not output_wav.exists():
        return fail("BreezyVoice finished without output WAV", synth.stdout)

    try:
        facts = wav_facts(output_wav)
    except RuntimeError as exc:
        return fail("ffprobe failed for generated BreezyVoice WAV", str(exc))

    append_jsonl(
        args.log_dir / "breezyvoice-chunk-generations.jsonl",
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "event": "breezyvoice_chunk_generation",
            "chunk_id": args.chunk_id,
            "runtime": f"{args.required_gpu_name} CUDA only",
            "required_gpu_name": args.required_gpu_name,
            "git_commit": current_commit,
            "origin_main_commit": remote_commit,
            "source_file": str(args.source_file),
            "source_text_sha256": text_hash,
            "source_text_characters": len(text),
            "runtime_repo": str(runtime),
            "python": str(py),
            "prompt_audio": str(args.prompt_audio),
            "model_path": args.model_path,
            "output_wav": str(output_wav),
            "nvidia_smi": smi_output.strip(),
            "runtime_probe": probe.stdout.strip(),
            "wav_facts": facts,
        },
    )
    print(f"PASS: generated {args.chunk_id} with BreezyVoice on {args.required_gpu_name}")
    print(smi_output.strip())
    print(probe.stdout.strip())
    print(facts)
    print(output_wav)
    print("Next gate:")
    if args.chunk_id == "sbm_tts_01_opening":
        print("python3 data/projects/2026-06-smart-biomedicine-final-report/tools/gate_breezyvoice_chunk01.py")
    else:
        print(
            "python3 data/projects/2026-06-smart-biomedicine-final-report/tools/chunk_asr_qa.py "
            f"--chunk-id {args.chunk_id} --language en --gate "
            "--engine-label BreezyVoice-26 "
            "--source-file data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-narration-chunks-v1.md "
            "--chunks-dir exports/smart-biomedicine-breezyvoice/chunks "
            "--out-dir exports/smart-biomedicine-breezyvoice/qa/chunk-asr "
            "--repair-dir exports/smart-biomedicine-breezyvoice/qa/chunk-repairs "
            "--log-dir exports/smart-biomedicine-breezyvoice/qa/experiment-logs "
            "--decisions-dir exports/smart-biomedicine-breezyvoice/qa/chunk-decisions "
            f"--required-gpu-name {args.required_gpu_name!r}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
