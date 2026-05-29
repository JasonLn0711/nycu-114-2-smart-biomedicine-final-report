#!/usr/bin/env python3
"""Run GPU-only Breeze-ASR-25 on one generated chunk as the transcript gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "data/projects/2026-06-smart-biomedicine-final-report"
CHUNK_SOURCE = PROJECT / "gpt-sovits-narration-chunks-v1.md"
CHUNKS = ROOT / "exports/smart-biomedicine-gpt-sovits/chunks"
OUT_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/chunk-asr"
REPAIR_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/chunk-repairs"
LOG_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/experiment-logs"
ASR_JSONL = LOG_DIR / "chunk-asr-gates.jsonl"
DECISIONS_DIR = ROOT / "exports/smart-biomedicine-gpt-sovits/qa/chunk-decisions"
DECISION_TOOL = PROJECT / "tools/mark_chunk_review_decision.py"
DEFAULT_MODEL = Path(
    "/home/jnln3799/.cache/huggingface/hub/models--SoybeanMilk--faster-whisper-Breeze-ASR-25/"
    "snapshots/85be11de5f67aaa6a92e931622f1c2b55cc1dd3a"
)
DEFAULT_PYTHON = Path("/home/jnln3799/.cache/uroprevisit-asr-venv/bin/python")
CUDA_LIBS = [
    "/home/jnln3799/.cache/uroprevisit-asr-venv/lib/python3.12/site-packages/nvidia/cublas/lib",
    "/home/jnln3799/.cache/uroprevisit-asr-venv/lib/python3.12/site-packages/nvidia/cudnn/lib",
    "/home/jnln3799/.cache/uroprevisit-asr-venv/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib",
    "/home/jnln3799/.cache/uroprevisit-asr-venv/lib/python3.12/site-packages/nvidia/cuda_runtime/lib",
]

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


def run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)


def run_git(cmd: list[str]) -> str:
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def tracked_worktree_changes() -> str:
    return run_git(["git", "status", "--porcelain", "--untracked-files=no"])


def refresh_origin_main() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "fetch", "origin", "main"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_text(source_file: Path, chunk_id: str) -> str:
    text = source_file.read_text(encoding="utf-8")
    match = re.search(rf"^###\s+{re.escape(chunk_id)}\n(.*?)(?=^###\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    block = match.group(1)
    text_match = re.search(r"```text\n(.*?)\n```", block, flags=re.DOTALL)
    return text_match.group(1).strip() if text_match else ""


def asr_transcript(stdout: str) -> str:
    lines: list[str] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped or "=" in stripped and stripped.split("=", 1)[0] in {"device", "model", "language", "language_probability"}:
            continue
        lines.append(re.sub(r"^\[\d+(?:\.\d+)?-\d+(?:\.\d+)?\]\s*", "", stripped))
    return " ".join(lines).strip()


def normalize_tokens(text: str) -> list[str]:
    text = text.lower()
    text = text.replace("large-language-model", "large language model")
    text = text.replace("pre-visit", "pre visit")
    text = text.replace("near-term", "near term")
    text = text.replace("clinician-ready", "clinician ready")
    text = re.sub(r"\ba\.\s*s\.\s*r\.?\b", "a s r", text)
    text = re.sub(r"\basr\b", "a s r", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.findall(r"[a-z0-9]+", text)


def has_phrase(tokens: list[str], phrase: str) -> bool:
    phrase_tokens = phrase.split()
    if not phrase_tokens:
        return True
    return any(tokens[idx : idx + len(phrase_tokens)] == phrase_tokens for idx in range(len(tokens) - len(phrase_tokens) + 1))


def token_comparison(expected: str, actual: str) -> dict[str, object]:
    expected_tokens = normalize_tokens(expected)
    actual_tokens = normalize_tokens(actual)
    matcher = SequenceMatcher(a=expected_tokens, b=actual_tokens, autojunk=False)
    missing: list[str] = []
    replacements: list[str] = []
    extras: list[str] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag in {"delete", "replace"}:
            missing.extend(expected_tokens[i1:i2])
        if tag == "replace":
            replacements.append(
                "expected `"
                + " ".join(expected_tokens[i1:i2])
                + "` but ASR heard `"
                + " ".join(actual_tokens[j1:j2])
                + "`"
            )
        if tag == "insert":
            extras.extend(actual_tokens[j1:j2])
    ratio = matcher.ratio()
    critical_phrases = [
        "my answer is yes",
        "a s r",
        "automatic speech recognition",
        "large language model",
        "clinical review screen",
        "clinician review screen",
        "human staff keep clinical authority",
        "human staff keep final authority",
        "human clinicians keep clinical authority",
        "not clinical judgment",
        "does not become the clinical authority",
        "not automatically ready for medical action",
        "not ready for automatic medical action",
        "do not use it for automatic medical action",
        "staff can reject it",
        "staff review comes first",
        "automatic medical action is outside the scope",
        "clinical staff check and correct the draft",
        "human staff check the draft",
        "human staff can correct it",
        "human staff can reject it",
        "the draft is checked before any care decision",
        "the doctor keeps the final authority",
        "human staff check the screen",
        "the clinician makes the care decision",
        "the doctor makes the medical decision",
        "artificial intelligence to act like a doctor",
        "the system creates a review screen",
        "not asking the system to make a diagnosis",
        "not proposing automatic scoring",
        "not deciding patient priority",
        "not proposing a treatment recommendation",
        "step by step process",
        "review screen for intake",
        "not own final clinical authority",
        "not make final care decisions",
    ]
    missing_critical = [
        phrase
        for phrase in critical_phrases
        if has_phrase(expected_tokens, phrase)
        and not has_phrase(actual_tokens, phrase)
    ]
    return {
        "ratio": ratio,
        "expected_tokens": expected_tokens,
        "actual_tokens": actual_tokens,
        "missing": missing[:80],
        "extras": extras[:80],
        "replacements": replacements[:20],
        "missing_critical": missing_critical,
    }


def repair_suggestions(expected: str, comparison: dict[str, object]) -> list[str]:
    suggestions = [
        "Regenerate only this chunk after applying the smallest text repair; do not continue to the next chunk while this marker is rejected.",
        "Prefer pronunciation-friendly source text over punctuation tricks: write `A S R` instead of `A. S. R.` when the model swallows letters.",
        "Replace hyphenated terms with spaced terms when ASR misses or merges them, for example `large language model`, `pre visit`, and `clinician ready`.",
        "If a short sentence is skipped, split it into a standalone sentence before the next technical phrase, then regenerate the same chunk.",
    ]
    missing_critical = comparison["missing_critical"]
    if missing_critical:
        suggestions.insert(1, "Priority phrase repair needed: " + ", ".join(f"`{phrase}`" for phrase in missing_critical))
    if "my answer is yes" in expected.lower():
        suggestions.append("For chunk 01, keep `My answer is yes.` as a separate sentence with a pause before the ASR definition.")
    return suggestions


def write_repair_plan(
    repair_dir: Path,
    source_file: Path,
    chunks_dir: Path,
    out_dir: Path,
    decision_dir: Path,
    chunk_id: str,
    expected: str,
    actual: str,
    comparison: dict[str, object],
    min_ratio: float,
) -> Path:
    repair_dir.mkdir(parents=True, exist_ok=True)
    out = repair_dir / f"{chunk_id}.repair-plan.md"
    suggestions = repair_suggestions(expected, comparison)
    replacement_lines = [f"- {item}" for item in comparison["replacements"]] or ["- `none`"]
    out.write_text(
        "\n".join(
            [
                f"# Breeze-ASR-25 Repair Plan - {chunk_id}",
                "",
                f"- created_at: `{datetime.now().isoformat(timespec='seconds')}`",
                f"- gate: `failed`",
                f"- min_ratio: `{min_ratio:.3f}`",
                f"- observed_ratio: `{comparison['ratio']:.3f}`",
                "",
                "## Source Text",
                "",
                "```text",
                expected,
                "```",
                "",
                "## Breeze-ASR-25 Transcript",
                "",
                "```text",
                actual,
                "```",
                "",
                "## Mismatch Summary",
                "",
                "- missing_critical: "
                + (", ".join(f"`{phrase}`" for phrase in comparison["missing_critical"]) or "`none`"),
                "- missing_tokens_sample: "
                + (" ".join(f"`{token}`" for token in comparison["missing"]) or "`none`"),
                "",
                "## Replacement Windows",
                "",
                *replacement_lines,
                "",
                "## Automated Correction Strategy",
                "",
                *[f"- {item}" for item in suggestions],
                "",
                "## Next Command",
                "",
                "```bash",
                "# Regenerate this same chunk with the active TTS engine, then rerun the gate:",
                "python3 data/projects/2026-06-smart-biomedicine-final-report/tools/chunk_asr_qa.py \\",
                f"  --chunk-id {chunk_id} --language en --gate --auto-decision \\",
                f"  --source-file {source_file} \\",
                f"  --chunks-dir {chunks_dir} \\",
                f"  --out-dir {out_dir} \\",
                f"  --repair-dir {repair_dir} \\",
                f"  --decisions-dir {decision_dir}",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out


def record_decision(
    decision_tool: Path,
    chunks_dir: Path,
    decisions_dir: Path,
    engine_label: str,
    chunk_id: str,
    accepted: bool,
    notes: str,
    repair_plan: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = [
        "python3",
        str(decision_tool),
        "--chunk-id",
        chunk_id,
        "--decision",
        "accepted" if accepted else "rejected",
        "--chunks-dir",
        str(chunks_dir),
        "--decisions-dir",
        str(decisions_dir),
        "--engine-label",
        engine_label,
        "--notes",
        notes,
        "--ack-breeze-asr-25-cuda",
    ]
    if accepted:
        cmd.extend(["--ack-breeze-asr-25-transcript-pass", "--ack-transcript-matches-source"])
    elif repair_plan is not None:
        cmd.append("--ack-repair-plan-created")
    return run(cmd)


def append_jsonl(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-id", required=True, choices=CHUNK_IDS)
    parser.add_argument("--language", default="en", help="Whisper language code for auxiliary ASR; default is en.")
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--python", default=str(DEFAULT_PYTHON))
    parser.add_argument("--source-file", type=Path, default=CHUNK_SOURCE)
    parser.add_argument("--chunks-dir", type=Path, default=CHUNKS)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--repair-dir", type=Path, default=REPAIR_DIR)
    parser.add_argument("--log-dir", type=Path, default=LOG_DIR)
    parser.add_argument("--decisions-dir", type=Path, default=DECISIONS_DIR)
    parser.add_argument("--decision-tool", type=Path, default=DECISION_TOOL)
    parser.add_argument("--engine-label", default="GPT-SoVITS")
    parser.add_argument("--required-gpu-name", default="RTX 5080")
    parser.add_argument("--gate", action="store_true", help="Compare Breeze-ASR-25 transcript against source text.")
    parser.add_argument("--auto-decision", action="store_true", help="Write accepted/rejected marker from the ASR gate.")
    parser.add_argument("--min-ratio", type=float, default=0.97, help="Minimum normalized token ratio for ASR acceptance.")
    parser.add_argument(
        "--allow-dirty-checkout",
        action="store_true",
        help="Allow tracked local modifications. Avoid this for production ASR evidence.",
    )
    parser.add_argument(
        "--allow-unpushed-checkout",
        action="store_true",
        help="Allow HEAD to differ from origin/main. Avoid this for production ASR evidence.",
    )
    parser.add_argument(
        "--skip-remote-refresh",
        action="store_true",
        help="Skip git fetch origin main before comparing HEAD with origin/main. Use only for offline debugging.",
    )
    args = parser.parse_args()

    current_commit = run_git(["git", "rev-parse", "HEAD"])
    dirty = tracked_worktree_changes()
    if dirty and not args.allow_dirty_checkout:
        return fail("tracked worktree changes found; refusing ASR gate from an uncommitted checkout", dirty)
    if not args.skip_remote_refresh:
        remote_refresh = refresh_origin_main()
        if remote_refresh.returncode != 0:
            return fail("could not refresh origin/main before ASR gate", remote_refresh.stdout)
    remote_commit = run_git(["git", "rev-parse", "origin/main"])
    if remote_commit != current_commit and not args.allow_unpushed_checkout:
        return fail(
            "HEAD does not match origin/main; refusing ASR gate from an unpushed or stale checkout",
            f"head={current_commit}\norigin_main={remote_commit}",
        )

    wav = args.chunks_dir / f"{args.chunk_id}.wav"
    model = Path(args.model)
    py = Path(args.python)
    if not wav.exists():
        return fail(f"chunk WAV missing: {wav}")
    if not args.source_file.exists():
        return fail(f"chunk source file missing: {args.source_file}")
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
    if args.required_gpu_name not in smi.stdout:
        return fail(f"{args.required_gpu_name} was not found; refusing CPU or non-matching GPU fallback", smi.stdout)

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"
    env["LD_LIBRARY_PATH"] = ":".join(CUDA_LIBS + [env.get("LD_LIBRARY_PATH", "")]).rstrip(":")
    code = f"""
from faster_whisper import WhisperModel
model = WhisperModel({str(model)!r}, device='cuda', compute_type='float16')
segments, info = model.transcribe({str(wav)!r}, beam_size=5, vad_filter=True, language={args.language!r})
print('device=cuda')
print('model=breeze-asr-25')
print('language=' + str(info.language))
print('language_probability=' + str(info.language_probability))
for s in segments:
    print(f'[{{s.start:.2f}}-{{s.end:.2f}}] {{s.text.strip()}}')
"""
    asr = run([str(py), "-c", code], env=env)
    if asr.returncode != 0:
        return fail("CUDA chunk ASR failed; do not fall back to CPU", asr.stdout)
    if "device=cuda" not in asr.stdout:
        return fail("chunk ASR did not prove CUDA execution", asr.stdout)

    expected = source_text(args.source_file, args.chunk_id)
    expected_hash = text_hash(expected)
    actual = asr_transcript(asr.stdout)
    comparison = token_comparison(expected, actual)
    missing_critical = comparison["missing_critical"]
    gate_pass = bool(args.gate) and comparison["ratio"] >= args.min_ratio and not missing_critical
    repair_plan: Path | None = None
    decision_output = ""
    if args.gate and not gate_pass:
        repair_plan = write_repair_plan(
            args.repair_dir,
            args.source_file,
            args.chunks_dir,
            args.out_dir,
            args.decisions_dir,
            args.chunk_id,
            expected,
            actual,
            comparison,
            args.min_ratio,
        )
    if args.auto_decision:
        notes = (
            f"Breeze-ASR-25 transcript gate ratio={comparison['ratio']:.3f}; "
            f"missing_critical={', '.join(missing_critical) or 'none'}"
        )
        decision = record_decision(
            args.decision_tool,
            args.chunks_dir,
            args.decisions_dir,
            args.engine_label,
            args.chunk_id,
            gate_pass,
            notes,
            repair_plan,
        )
        decision_output = decision.stdout.strip()
        if decision.returncode != 0:
            return fail("could not record ASR-led chunk decision", decision.stdout)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / f"{args.chunk_id}.asr-qa.md"
    out.write_text(
        "\n".join(
            [
                f"# Chunk ASR QA - {args.chunk_id}",
                "",
                "This is the primary Breeze-ASR-25 transcript gate before semantic-sweep acceptance.",
                "",
                f"- chunk_id: `{args.chunk_id}`",
                f"- git_commit: `{current_commit}`",
                f"- origin_main_commit: `{remote_commit}`",
                f"- wav: `{wav}`",
                f"- language_hint: `{args.language}`",
                f"- runtime: `{args.required_gpu_name} CUDA only`",
                f"- source_text_sha256: `{expected_hash}`",
                f"- gate_enabled: `{str(args.gate).lower()}`",
                f"- gate_status: `{'pass' if gate_pass else 'fail' if args.gate else 'not_run'}`",
                f"- min_ratio: `{args.min_ratio:.3f}`",
                f"- observed_ratio: `{comparison['ratio']:.3f}`",
                f"- missing_critical: `{', '.join(missing_critical) or 'none'}`",
                f"- repair_plan: `{repair_plan if repair_plan else ''}`",
                "",
                "## Source Text",
                "",
                "```text",
                expected,
                "```",
                "",
                "## Normalized ASR Transcript",
                "",
                "```text",
                actual,
                "```",
                "",
                "## Breeze-ASR-25 Output",
                "",
                "```text",
                asr.stdout.strip(),
                "```",
                "",
                "## Transcript Gate Use",
                "",
                "- Compare the ASR output against the source text for missing or repeated phrases.",
                "- Ignore punctuation differences and normal ASR spelling differences.",
                "- If the transcript gate fails, use the repair plan, regenerate only this chunk, and rerun this gate.",
                "- Passing this transcript gate is not enough for BreezyVoice acceptance; record the semantic sweep before writing an accepted marker.",
                "- Human listening is now an exception path, used only when the ASR result is ambiguous or repeatedly unstable.",
                "",
                "## Decision Output",
                "",
                "```text",
                decision_output,
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(out)
    append_jsonl(
        args.log_dir / "chunk-asr-gates.jsonl",
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "event": "chunk_asr_gate",
            "chunk_id": args.chunk_id,
            "git_commit": current_commit,
            "origin_main_commit": remote_commit,
            "wav": str(wav),
            "language": args.language,
            "runtime": f"{args.required_gpu_name} CUDA only",
            "source_text_sha256": expected_hash,
            "gate_enabled": args.gate,
            "gate_status": "pass" if gate_pass else "fail" if args.gate else "not_run",
            "min_ratio": args.min_ratio,
            "observed_ratio": comparison["ratio"],
            "missing_critical": missing_critical,
            "repair_plan": str(repair_plan) if repair_plan else "",
            "asr_report": str(out),
            "decision_output": decision_output,
            "source_text": expected,
            "normalized_asr_transcript": actual,
            "raw_asr_output": asr.stdout.strip(),
        },
    )
    if args.gate:
        print(f"gate_status={'pass' if gate_pass else 'fail'} ratio={comparison['ratio']:.3f}")
        if repair_plan:
            print(f"repair_plan={repair_plan}")
    if decision_output:
        print(decision_output)
    print(asr.stdout.strip())
    return 0 if not args.gate or gate_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
