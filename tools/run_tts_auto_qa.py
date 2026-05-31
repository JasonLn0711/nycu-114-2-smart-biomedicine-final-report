#!/usr/bin/env python3
"""Run a project-neutral TTS auto-QA gate.

The gate is intentionally conservative and dependency-light. It accepts plain
text files or existing chunk ASR Markdown reports, then emits one evidence
package with transcript similarity, critical-term matching, audio quality,
rights status, hashes, and release summary files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROFILE_THRESHOLDS = {
    "internal_draft": {"cer": 0.12, "wer": 0.18},
    "teaching_material": {"cer": 0.08, "wer": 0.12},
    "research_stimulus": {"cer": 0.05, "wer": 0.08},
    "public_external": {"cer": 0.06, "wer": 0.10},
}

STATUS_PRIORITY = [
    "research_use_blocked",
    "rejected_rights",
    "rejected_term_error",
    "rejected_audio_quality",
    "rejected_chunk_boundary",
    "rejected_text_mismatch",
    "rejected_platform_smoke",
]

MEDIA_EXTENSIONS = {".wav", ".mp3", ".m4a", ".mp4", ".mov", ".mkv", ".webm"}


@dataclass(frozen=True)
class LexiconEntry:
    term: str
    preferred_reading: str
    aliases: list[str]
    context: str
    critical: bool


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def slug_heading(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def extract_section(markdown: str, heading: str) -> str | None:
    """Extract the first fenced block after a Markdown heading."""

    wanted = slug_heading(heading)
    lines = markdown.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.startswith("#") and slug_heading(line.lstrip("#").strip()) == wanted:
            start = idx + 1
            break
    if start is None:
        return None

    next_heading = len(lines)
    for idx in range(start, len(lines)):
        if lines[idx].startswith("#"):
            next_heading = idx
            break
    body = "\n".join(lines[start:next_heading]).strip()
    fenced = re.search(r"```(?:text)?\n(.*?)\n```", body, flags=re.S)
    return fenced.group(1).strip() if fenced else body


def read_text_or_section(path: Path | None, section: str | None) -> str:
    if path is None:
        return ""
    text = read_text(path)
    if section:
        found = extract_section(text, section)
        if found is not None:
            return found
    if path.suffix.lower() in {".md", ".markdown"} and "## TTS Chunks" in text:
        body = text[text.find("## TTS Chunks") :]
        blocks = re.findall(r"```(?:text)?\n(.*?)\n```", body, flags=re.S)
        if blocks:
            return "\n\n".join(block.strip() for block in blocks if block.strip())
    return text


def collect_asr_reports(report_dir: Path) -> tuple[str, str, list[dict[str, Any]]]:
    source_parts: list[str] = []
    asr_parts: list[str] = []
    chunks: list[dict[str, Any]] = []
    for report in sorted(report_dir.glob("*.asr-qa.md")):
        text = read_text(report)
        source = extract_section(text, "Source Text") or ""
        transcript = extract_section(text, "Normalized ASR Transcript") or ""
        chunk_id = report.name.removesuffix(".asr-qa.md")
        source_parts.append(source)
        asr_parts.append(transcript)
        chunks.append(
            {
                "chunk_id": chunk_id,
                "asr_report": str(report),
                "source_text_sha256": sha256_text(source),
                "asr_transcript_sha256": sha256_text(transcript),
                "source_chars": len(source),
                "asr_chars": len(transcript),
            }
        )
    return "\n\n".join(source_parts), "\n\n".join(asr_parts), chunks


def normalize_for_cer(text: str) -> str:
    text = text.lower()
    text = text.replace("，", ",").replace("。", ".").replace("、", " ")
    text = re.sub(r"[\s\W_]+", "", text, flags=re.UNICODE)
    return text


def tokenize_for_wer(text: str) -> list[str]:
    text = text.lower()
    return re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", text)


def normalize_phrase(text: str) -> str:
    return normalize_for_cer(text)


def levenshtein_distance(a: list[str] | str, b: list[str] | str) -> int:
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            replace = previous[j - 1] + (0 if ca == cb else 1)
            current.append(min(insert, delete, replace))
        previous = current
    return previous[-1]


def ratio_error(reference: list[str] | str, observed: list[str] | str) -> float:
    if not reference:
        return 0.0 if not observed else 1.0
    return levenshtein_distance(reference, observed) / len(reference)


def sentence_units(text: str) -> list[str]:
    raw = re.split(r"(?<=[.!?。！？])\s+|\n{2,}", text)
    units = []
    for part in raw:
        normalized = normalize_phrase(part)
        if len(normalized) >= 18:
            units.append(normalized)
    return units


def count_missing_sentences(source: str, transcript: str) -> int:
    from difflib import SequenceMatcher

    transcript_norm = normalize_phrase(transcript)
    transcript_units = sentence_units(transcript)
    missing = 0
    for sentence in sentence_units(source):
        if sentence in transcript_norm:
            continue
        best_ratio = max((SequenceMatcher(a=sentence, b=unit, autojunk=False).ratio() for unit in transcript_units), default=0.0)
        if best_ratio < 0.72:
            missing += 1
    return missing


def count_repeated_sentences(transcript: str) -> int:
    units = [normalize_phrase(part) for part in re.split(r"[.!?。！？]\s*|\n+", transcript)]
    units = [unit for unit in units if len(unit) >= 12]
    repeats = 0
    seen: dict[str, int] = {}
    previous = ""
    for unit in units:
        if unit == previous:
            repeats += 1
        seen[unit] = seen.get(unit, 0) + 1
        previous = unit
    repeats += sum(count - 1 for count in seen.values() if count > 2)
    return repeats


def extract_numbers(text: str) -> list[str]:
    return re.findall(r"\d+(?:\.\d+)?", text)


def numeric_mismatches(source: str, transcript: str) -> list[dict[str, str]]:
    source_numbers = extract_numbers(source)
    transcript_numbers = extract_numbers(transcript)
    missing = [number for number in source_numbers if number not in transcript_numbers]
    extra = [number for number in transcript_numbers if number not in source_numbers]
    mismatches = []
    for number in missing:
        mismatches.append({"type": "missing_in_asr", "number": number})
    for number in extra:
        mismatches.append({"type": "extra_in_asr", "number": number})
    return mismatches


def read_lexicon(path: Path) -> list[LexiconEntry]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        entries = []
        for row in reader:
            aliases = [part.strip() for part in row.get("aliases", "").split("|") if part.strip()]
            critical = row.get("critical", "").strip().lower() in {"yes", "true", "1", "y"}
            entries.append(
                LexiconEntry(
                    term=row.get("term", "").strip(),
                    preferred_reading=row.get("preferred_reading", "").strip(),
                    aliases=aliases,
                    context=row.get("context", "").strip(),
                    critical=critical,
                )
            )
    return entries


def variants(entry: LexiconEntry) -> list[str]:
    values = [entry.term, entry.preferred_reading, *entry.aliases]
    return [value for value in values if value]


def contains_variant(text: str, entry: LexiconEntry) -> tuple[bool, str]:
    normalized_text = normalize_phrase(text)
    for value in variants(entry):
        if normalize_phrase(value) in normalized_text:
            return True, value
    return False, ""


def term_gate(
    source_text: str,
    model_facing_text: str,
    asr_transcript: str,
    entries: list[LexiconEntry],
) -> tuple[float, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    source_surface = "\n".join([source_text, model_facing_text])
    checked: list[LexiconEntry] = []
    term_rows: list[dict[str, str]] = []
    missing_critical: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    for entry in entries:
        present_in_source, source_variant = contains_variant(source_surface, entry)
        if not present_in_source:
            continue
        checked.append(entry)
        present_in_asr, observed_variant = contains_variant(asr_transcript, entry)
        status = "pass" if present_in_asr else "missing"
        row = {
            "term": entry.term,
            "expected_reading": entry.preferred_reading,
            "aliases": "|".join(entry.aliases),
            "context": entry.context,
            "critical": "yes" if entry.critical else "no",
            "source_variant": source_variant,
            "asr_observed": observed_variant,
            "error_type": "" if present_in_asr else "missing_term_or_alias",
            "status": status,
        }
        term_rows.append(row)
        if not present_in_asr and entry.critical:
            missing_critical.append(row)
        elif not present_in_asr:
            warnings.append(row)

    critical_checked = [entry for entry in checked if entry.critical]
    if not critical_checked:
        accuracy = 1.0
    else:
        accuracy = (len(critical_checked) - len(missing_critical)) / len(critical_checked)
    return accuracy, missing_critical, warnings, term_rows


def parse_simple_yaml(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    data: dict[str, str] = {}
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def yes(value: str | None) -> bool:
    return (value or "").strip().lower() in {"yes", "true", "1", "y"}


def no(value: str | None) -> bool:
    return (value or "").strip().lower() in {"no", "false", "0", "n"}


def not_applicable(value: str | None) -> bool:
    return (value or "").strip().lower() in {"not_applicable", "n/a", "na", "none"}


def rights_gate(profile: str, manifest: dict[str, str]) -> tuple[dict[str, Any], list[str], list[str]]:
    warnings: list[str] = []
    rejects: list[str] = []
    if not manifest:
        return (
            {
                "status": "missing",
                "research_use_blocked": profile == "research_stimulus",
                "external_sharing_blocked": profile == "public_external",
            },
            ["rights manifest missing"],
            ["research_use_blocked" if profile == "research_stimulus" else "rejected_rights"],
        )

    consent = manifest.get("consent_obtained", "")
    voice_source = manifest.get("voice_source", "")
    human_like_source = not not_applicable(voice_source) and "synthetic" not in voice_source.lower()
    research_blocked = False
    external_blocked = False

    if human_like_source and no(consent):
        research_blocked = True
        rejects.append("research_use_blocked")
    elif human_like_source and not (yes(consent) or not_applicable(consent)):
        warnings.append("consent status should be explicit yes/no/not_applicable")

    if profile == "research_stimulus" and not yes(manifest.get("can_use_for_research")):
        research_blocked = True
        rejects.append("research_use_blocked")
    if profile == "public_external" and not yes(manifest.get("can_share_externally")):
        external_blocked = True
        rejects.append("rejected_rights")
    if not manifest.get("synthetic_voice_disclosure_required"):
        warnings.append("synthetic_voice_disclosure_required not recorded")

    status = "pass" if not rejects else "fail"
    return (
        {
            "status": status,
            "research_use_blocked": research_blocked,
            "external_sharing_blocked": external_blocked,
            "manifest": manifest,
        },
        warnings,
        rejects,
    )


def run_command(command: list[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError:
        return 127, ""
    return completed.returncode, completed.stdout


def ffprobe(path: Path) -> dict[str, Any]:
    code, out = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ]
    )
    if code != 0 or not out.strip():
        return {"path": str(path), "probe_error": out.strip() or "ffprobe unavailable"}
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return {"path": str(path), "probe_error": out.strip()}
    audio_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    stream = audio_streams[0] if audio_streams else {}
    return {
        "path": str(path),
        "duration_seconds": float(data.get("format", {}).get("duration", 0) or 0),
        "sample_rate": int(stream.get("sample_rate", 0) or 0),
        "channels": int(stream.get("channels", 0) or 0),
        "channel_layout": stream.get("channel_layout") or f"{stream.get('channels', 'unknown')}ch",
        "codec_name": stream.get("codec_name", ""),
    }


def ffmpeg_audio_metrics(path: Path) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "mean_volume_db": None,
        "max_volume_db": None,
        "integrated_loudness_lufs": None,
        "long_silence_count": 0,
        "max_silence_seconds": 0.0,
        "ffmpeg_warnings": [],
    }

    code, out = run_command(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"]
    )
    if code == 127:
        metrics["ffmpeg_warnings"].append("ffmpeg unavailable")
        return metrics
    mean_match = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", out)
    max_match = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", out)
    if mean_match:
        metrics["mean_volume_db"] = float(mean_match.group(1))
    if max_match:
        metrics["max_volume_db"] = float(max_match.group(1))

    code, out = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "silencedetect=noise=-35dB:d=2.0",
            "-f",
            "null",
            "-",
        ]
    )
    silence_durations = [float(value) for value in re.findall(r"silence_duration:\s*(\d+(?:\.\d+)?)", out)]
    metrics["long_silence_count"] = len([duration for duration in silence_durations if duration > 2.0])
    metrics["max_silence_seconds"] = max(silence_durations) if silence_durations else 0.0

    code, out = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ]
    )
    loudness_match = re.search(r"\{\s*\"input_i\".*?\}", out, flags=re.S)
    if loudness_match:
        try:
            loudness = json.loads(loudness_match.group(0))
            metrics["integrated_loudness_lufs"] = float(loudness.get("input_i"))
        except (TypeError, ValueError, json.JSONDecodeError):
            metrics["ffmpeg_warnings"].append("could not parse loudnorm output")
    return metrics


def collect_audio(audio_dir: Path | None) -> tuple[dict[str, Any], list[str], list[str]]:
    if audio_dir is None:
        return (
            {
                "files": [],
                "clipping": False,
                "long_silence_count": 0,
                "integrated_loudness_lufs": None,
                "sample_rate_consistent": True,
                "channel_layout_consistent": True,
                "chunk_loudness_spread_db": 0.0,
                "status": "not_run",
            },
            ["audio-dir not provided; audio quality gate not run"],
            [],
        )

    paths = sorted(path for path in audio_dir.rglob("*") if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS)
    if not paths:
        return (
            {
                "files": [],
                "clipping": False,
                "long_silence_count": 0,
                "integrated_loudness_lufs": None,
                "sample_rate_consistent": False,
                "channel_layout_consistent": False,
                "chunk_loudness_spread_db": 0.0,
                "status": "missing_audio",
            },
            [],
            ["rejected_audio_quality"],
        )

    files: list[dict[str, Any]] = []
    warnings: list[str] = []
    rejects: list[str] = []
    for path in paths:
        probe = ffprobe(path)
        metrics = ffmpeg_audio_metrics(path)
        file_row = {
            **probe,
            **metrics,
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        files.append(file_row)
        warnings.extend(metrics.get("ffmpeg_warnings", []))

    sample_rates = {row.get("sample_rate") for row in files if row.get("sample_rate")}
    layouts = {row.get("channel_layout") for row in files if row.get("channel_layout")}
    loudness_values = [
        row["integrated_loudness_lufs"]
        for row in files
        if isinstance(row.get("integrated_loudness_lufs"), (int, float)) and not math.isnan(row["integrated_loudness_lufs"])
    ]
    max_volumes = [
        row["max_volume_db"]
        for row in files
        if isinstance(row.get("max_volume_db"), (int, float)) and not math.isnan(row["max_volume_db"])
    ]
    long_silence_count = sum(int(row.get("long_silence_count") or 0) for row in files)
    loudness_spread = (max(loudness_values) - min(loudness_values)) if loudness_values else 0.0
    integrated_loudness = sum(loudness_values) / len(loudness_values) if loudness_values else None
    clipping = any(value >= 0.0 for value in max_volumes)
    near_peak = any(-0.2 <= value < 0.0 for value in max_volumes)
    sample_rate_consistent = len(sample_rates) <= 1
    channel_layout_consistent = len(layouts) <= 1

    if clipping:
        rejects.append("rejected_audio_quality")
    if near_peak:
        warnings.append("audio peak is close to 0 dBFS; confirm limiter behavior")
    if long_silence_count > 0:
        rejects.append("rejected_audio_quality")
    if not sample_rate_consistent or not channel_layout_consistent:
        rejects.append("rejected_audio_quality")
    if loudness_spread > 6.0:
        rejects.append("rejected_audio_quality")
    if integrated_loudness is not None and abs(integrated_loudness - (-16.0)) > 4.0:
        warnings.append("integrated loudness differs from -16 LUFS narration target by more than 4 dB")

    status = "pass" if not rejects else "fail"
    return (
        {
            "files": files,
            "file_count": len(files),
            "clipping": clipping,
            "long_silence_count": long_silence_count,
            "integrated_loudness_lufs": integrated_loudness,
            "sample_rate_consistent": sample_rate_consistent,
            "channel_layout_consistent": channel_layout_consistent,
            "chunk_loudness_spread_db": loudness_spread,
            "status": status,
        },
        sorted(set(warnings)),
        sorted(set(rejects)),
    )


def semantic_drift_check(source: str, transcript: str) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    lower_source = source.lower()
    lower_asr = transcript.lower()
    for phrase in [
        "not a diagnosis",
        "not a treatment",
        "not final",
        "staff review",
        "doctor",
        "triage",
    ]:
        if phrase in lower_source and phrase not in lower_asr:
            issues.append({"type": "possible_clinical_boundary_drift", "phrase": phrase})
    for mismatch in numeric_mismatches(source, transcript):
        issues.append({"type": "numeric_mismatch", "detail": mismatch["number"]})
    status = "pass"
    if issues:
        status = "fail" if any(issue["type"] == "numeric_mismatch" for issue in issues) else "warning"
    return {"status": status, "issues": issues}


def choose_status(rejects: list[str], warnings: list[str]) -> str:
    unique_rejects = list(dict.fromkeys(rejects))
    for status in STATUS_PRIORITY:
        if status in unique_rejects:
            return status
    if unique_rejects:
        return unique_rejects[0]
    return "accepted_with_warnings" if warnings else "accepted_auto_gate"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_term_errors(path: Path, rows: list[dict[str, str]], experiment_id: str) -> None:
    fieldnames = [
        "experiment_id",
        "term",
        "expected_reading",
        "aliases",
        "context",
        "critical",
        "source_variant",
        "asr_observed",
        "error_type",
        "status",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            if row["status"] == "pass":
                continue
            writer.writerow({"experiment_id": experiment_id, **row})


def format_float(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "not_run"
    return f"{value:.{digits}f}"


def write_summary(path: Path, result: dict[str, Any]) -> None:
    metrics = result["metrics"]
    audio = result["audio_quality"]
    lines = [
        f"# TTS Auto QA Summary - {result['experiment_id']}",
        "",
        f"- status: `{result['status']}`",
        f"- profile: `{result['profile']}`",
        f"- created_at: `{result['created_at']}`",
        f"- CER: `{format_float(metrics['cer'])}`",
        f"- WER: `{format_float(metrics['wer'])}`",
        f"- critical_term_accuracy: `{format_float(metrics['critical_term_accuracy'])}`",
        f"- audio_files_checked: `{audio.get('file_count', 0)}`",
        f"- audio_status: `{audio.get('status')}`",
        f"- rights_status: `{result['rights'].get('status')}`",
        "",
        "## Reject Reasons",
        "",
    ]
    if result["reject_reasons"]:
        lines.extend(f"- `{reason}`" for reason in result["reject_reasons"])
    else:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    if result["warnings"]:
        lines.extend(f"- {warning}" for warning in result["warnings"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            result["next_action"],
            "",
            "## Evidence Files",
            "",
            "- `qa_result.json`",
            "- `term_error_list.csv`",
            "- `audio_quality_report.json`",
            "- `release_manifest.md`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_release_manifest(path: Path, result: dict[str, Any]) -> None:
    audio_rows = result["audio_quality"].get("files", [])
    lines = [
        f"# TTS Auto-QA Release Manifest - {result['experiment_id']}",
        "",
        f"- status: `{result['status']}`",
        f"- profile: `{result['profile']}`",
        f"- source_text_sha256: `{result['source_text_sha256']}`",
        f"- model_facing_text_sha256: `{result['model_facing_text_sha256']}`",
        f"- asr_transcript_sha256: `{result['asr_transcript_sha256']}`",
        f"- rights_status: `{result['rights'].get('status')}`",
        "",
        "## Audio Artifacts",
        "",
        "| Path | Size | SHA256 |",
        "| --- | ---: | --- |",
    ]
    for row in audio_rows:
        lines.append(f"| `{row.get('path')}` | `{row.get('size_bytes')}` | `{row.get('sha256')}` |")
    if not audio_rows:
        lines.append("| none | 0 |  |")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            result["next_action"],
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-text", type=Path)
    parser.add_argument("--model-facing-text", type=Path)
    parser.add_argument("--asr-transcript", type=Path)
    parser.add_argument("--source-section")
    parser.add_argument("--model-facing-section")
    parser.add_argument("--asr-section")
    parser.add_argument("--asr-report-dir", type=Path, help="Directory containing *.asr-qa.md reports.")
    parser.add_argument("--lexicon", type=Path, required=True)
    parser.add_argument("--audio-dir", type=Path)
    parser.add_argument("--rights-manifest", type=Path)
    parser.add_argument("--profile", choices=sorted(PROFILE_THRESHOLDS), default="teaching_material")
    parser.add_argument("--experiment-id")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--enable-llm-drift-check", action="store_true")
    parser.add_argument("--platform-smoke-status", choices=["not_run", "pass", "warning", "fail"], default="not_run")
    parser.add_argument("--platform-smoke-note", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    report_source = ""
    report_asr = ""
    chunks: list[dict[str, Any]] = []
    if args.asr_transcript and args.asr_transcript.is_dir():
        report_source, report_asr, chunks = collect_asr_reports(args.asr_transcript)
    elif args.asr_report_dir:
        report_source, report_asr, chunks = collect_asr_reports(args.asr_report_dir)

    source_text = read_text_or_section(args.source_text, args.source_section) or report_source
    model_facing_text = read_text_or_section(args.model_facing_text, args.model_facing_section) or source_text
    if args.asr_transcript and args.asr_transcript.is_dir():
        asr_transcript = report_asr
    else:
        asr_transcript = read_text_or_section(args.asr_transcript, args.asr_section) or report_asr
    if not source_text or not asr_transcript:
        parser.error("source/model text and ASR transcript are required, or provide --asr-report-dir")

    experiment_id = args.experiment_id or out_dir.name
    thresholds = PROFILE_THRESHOLDS[args.profile]

    cer = ratio_error(normalize_for_cer(source_text), normalize_for_cer(asr_transcript))
    wer = ratio_error(tokenize_for_wer(source_text), tokenize_for_wer(asr_transcript))
    missing_sentence_count = count_missing_sentences(source_text, asr_transcript)
    repeated_sentence_count = count_repeated_sentences(asr_transcript)
    number_mismatches = numeric_mismatches(source_text, asr_transcript)

    entries = read_lexicon(args.lexicon)
    critical_accuracy, missing_critical, term_warnings, term_rows = term_gate(
        source_text,
        model_facing_text,
        asr_transcript,
        entries,
    )

    audio_quality, audio_warnings, audio_rejects = collect_audio(args.audio_dir)
    rights, rights_warnings, rights_rejects = rights_gate(args.profile, parse_simple_yaml(args.rights_manifest))

    semantic_drift = {"status": "not_run", "issues": []}
    if args.enable_llm_drift_check:
        semantic_drift = semantic_drift_check(source_text, asr_transcript)

    warnings: list[str] = []
    reject_reasons: list[str] = []
    if cer > thresholds["cer"] or wer > thresholds["wer"]:
        reject_reasons.append("rejected_text_mismatch")
    if missing_sentence_count > 0:
        warnings.append(f"missing_sentence_count={missing_sentence_count}")
    if repeated_sentence_count > 0:
        reject_reasons.append("rejected_chunk_boundary")
    if missing_critical:
        reject_reasons.append("rejected_term_error")
    if term_warnings:
        warnings.append(f"non-critical term warnings={len(term_warnings)}")
    if number_mismatches:
        warnings.append(f"numeric_mismatches={len(number_mismatches)}")
    if semantic_drift["status"] == "fail":
        reject_reasons.append("rejected_text_mismatch")
    elif semantic_drift["status"] == "warning":
        warnings.append("semantic drift warning")
    if args.platform_smoke_status == "fail":
        reject_reasons.append("rejected_platform_smoke")
    elif args.platform_smoke_status in {"not_run", "warning"}:
        warnings.append(f"platform smoke check {args.platform_smoke_status}")

    reject_reasons.extend(audio_rejects)
    reject_reasons.extend(rights_rejects)
    warnings.extend(audio_warnings)
    warnings.extend(rights_warnings)

    reject_reasons = list(dict.fromkeys(reject_reasons))
    warnings = list(dict.fromkeys(warnings))
    status = choose_status(reject_reasons, warnings)
    if status == "accepted_auto_gate":
        next_action = "Accepted by the automated gate. Preserve hashes, QA files, and experiment card before release."
    elif status == "accepted_with_warnings":
        next_action = "Accepted with warnings. Review warnings and decide whether the target use profile needs repair."
    else:
        next_action = "Rejected by the automated gate. Repair the listed failure class, regenerate only affected chunks when possible, and rerun QA."

    result = {
        "experiment_id": experiment_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profile": args.profile,
        "status": status,
        "source_text_sha256": sha256_text(source_text),
        "model_facing_text_sha256": sha256_text(model_facing_text),
        "audio_sha256": [
            {"path": row.get("path"), "sha256": row.get("sha256")}
            for row in audio_quality.get("files", [])
        ],
        "asr_transcript_sha256": sha256_text(asr_transcript),
        "inputs": {
            "source_text": str(args.source_text) if args.source_text else None,
            "model_facing_text": str(args.model_facing_text) if args.model_facing_text else None,
            "asr_transcript": str(args.asr_transcript) if args.asr_transcript else None,
            "asr_report_dir": str(args.asr_report_dir) if args.asr_report_dir else None,
            "lexicon": str(args.lexicon),
            "audio_dir": str(args.audio_dir) if args.audio_dir else None,
            "rights_manifest": str(args.rights_manifest) if args.rights_manifest else None,
        },
        "chunks": chunks,
        "metrics": {
            "cer": cer,
            "wer": wer,
            "thresholds": thresholds,
            "critical_term_accuracy": critical_accuracy,
            "missing_critical_terms": [row["term"] for row in missing_critical],
            "numeric_mismatches": number_mismatches,
            "missing_sentence_count": missing_sentence_count,
            "repeated_sentence_count": repeated_sentence_count,
        },
        "audio_quality": audio_quality,
        "rights": rights,
        "platform_smoke": {
            "status": args.platform_smoke_status,
            "note": args.platform_smoke_note,
        },
        "semantic_drift": semantic_drift,
        "warnings": warnings,
        "reject_reasons": reject_reasons,
        "next_action": next_action,
    }

    write_json(out_dir / "qa_result.json", result)
    write_json(out_dir / "audio_quality_report.json", audio_quality)
    write_term_errors(out_dir / "term_error_list.csv", term_rows, experiment_id)
    write_summary(out_dir / "qa_summary.md", result)
    write_release_manifest(out_dir / "release_manifest.md", result)

    print(f"status={status}")
    print(out_dir / "qa_result.json")
    return 0 if not reject_reasons else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
