#!/usr/bin/env python3
"""Create local submission proof templates for YouTube, Padlet, and peer gates."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_EXPORT_ROOT = ROOT / "exports/smart-biomedicine-gpt-sovits"


FILES = {
    "youtube-url.txt.TEMPLATE": """# Replace this template with the final YouTube URL after upload.
# Required before Padlet posting.
https://www.youtube.com/watch?v=<video-id>
""",
    "padlet-post-proof.md.TEMPLATE": """# Padlet Post Proof

- posted_at:
- padlet_url: https://padlet.com/nycu2/114-76l8lt7dq8w9iaqj
- youtube_url:
- student_id: 513559004
- student_name: 林家聖
- report_title: 從語音問診到醫師摘要：ASR + LLM 在智慧生醫臨床前問診中的應用與邊界
- screenshot_path:
- checked_playback_after_post: `[ ]`
""",
    "peer-engagement-proof.md.TEMPLATE": """# Peer Engagement Proof

Deadline: `2026-06-17`

- completed_at:
- classmate_student_id_or_name:
- classmate_report_title:
- watched_url_or_padlet_location:
- comment_or_question_text:
- liked: `[ ]`
- screenshot_path:
""",
    "presenter-response-proof.md.TEMPLATE": """# Presenter Response Proof

Deadline: `2026-06-20`

- checked_at:
- questions_found:
- responses_posted:
- response_text_or_summary:
- screenshot_path:
""",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--export-root",
        type=Path,
        default=DEFAULT_EXPORT_ROOT,
        help="Generated artifact root that should receive the submission/ proof templates.",
    )
    args = parser.parse_args()

    submission = args.export_root / "submission"
    submission.mkdir(parents=True, exist_ok=True)
    for name, content in FILES.items():
        path = submission / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
