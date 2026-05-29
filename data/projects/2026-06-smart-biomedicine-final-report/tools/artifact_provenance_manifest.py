#!/usr/bin/env python3
"""Write SHA-256 provenance for tracked and local report-production artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROJECT_TOOL_DIR = ROOT / "data/projects/2026-06-smart-biomedicine-final-report/tools"
DEFAULT_EXPORT_ROOT = ROOT / "exports/smart-biomedicine-gpt-sovits"

COMMON_TRACKED_FILES = [
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/markdown-report-v1.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/markdown-report-20min-script-v2.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/video-recording-cue-sheet-v1.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/video-recording-qa-sheet-v1.md",
]
GPT_TRACKED_FILES = [
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/gpt-sovits-narration-chunks-v1.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/gpt-sovits-production-runbook-v1.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/gpt-sovits-current-execution-plan-v1.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/gpt-sovits-asr-review-and-repair-plan-v1.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/reference-audio-candidates-v1.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/gpt-sovits-audio-qa-sheet-v1.md",
]
BREEZY_TRACKED_FILES = [
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-narration-chunks-v1.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-current-execution-plan-v1.md",
    ROOT / "data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-runtime-switch-v1.md",
]
SOURCE_VOICE = Path("/home/jnclaw/Downloads/260528_0839_record.mp3")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def category(path: Path) -> str:
    if path == SOURCE_VOICE:
        return "source_voice"
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return "external"
    if str(rel).startswith("data/projects/"):
        return "tracked_project_source"
    if str(rel).startswith("exports/"):
        return "local_generated"
    return "other"


def tracked_files(engine_label: str) -> list[Path]:
    if engine_label.lower().startswith("breezy"):
        return COMMON_TRACKED_FILES + BREEZY_TRACKED_FILES
    return COMMON_TRACKED_FILES + GPT_TRACKED_FILES


def collect_paths(export_root: Path, engine_label: str, out_dir: Path) -> list[Path]:
    paths: list[Path] = []
    if SOURCE_VOICE.exists():
        paths.append(SOURCE_VOICE)
    paths.extend(path for path in tracked_files(engine_label) if path.exists())
    paths.extend(path for path in PROJECT_TOOL_DIR.glob("*.py") if path.is_file())
    if export_root.exists():
        paths.extend(
            path for path in export_root.rglob("*")
            if path.is_file() and not path.resolve().is_relative_to(out_dir.resolve())
        )
    return sorted(set(paths), key=lambda p: str(p))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--export-root",
        type=Path,
        default=DEFAULT_EXPORT_ROOT,
        help="Generated artifact root whose local artifacts should be hashed.",
    )
    parser.add_argument("--engine-label", default="GPT-SoVITS")
    args = parser.parse_args()
    export_root = args.export_root if args.export_root.is_absolute() else ROOT / args.export_root

    out_dir = export_root / "qa/provenance"
    csv_out = out_dir / "artifact-provenance-manifest.csv"
    md_out = out_dir / "artifact-provenance-manifest.md"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = collect_paths(export_root, args.engine_label, out_dir)
    rows = []
    for path in paths:
        rows.append(
            {
                "category": category(path),
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    with csv_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "path", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)

    md = [
        "# Artifact Provenance Manifest",
        "",
        f"Engine route: `{args.engine_label}`",
        "",
        "This manifest records SHA-256 hashes for the report source, narration source, local generated artifacts, QA reports, recording surface, video candidates, and submission proof files.",
        "",
        f"- artifacts_hashed: `{len(rows)}`",
        "",
        "| Category | Path | Size | SHA-256 |",
        "| --- | --- | ---: | --- |",
    ]
    for row in rows:
        md.append(
            f"| `{row['category']}` | `{row['path']}` | `{row['size_bytes']}` | `{row['sha256']}` |"
        )
    md.append("")
    md_out.write_text("\n".join(md), encoding="utf-8")
    print(md_out)
    print(csv_out)
    print(f"artifacts_hashed={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
