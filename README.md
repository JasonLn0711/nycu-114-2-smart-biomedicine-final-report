# NYCU 114-2 Smart Biomedicine Final Report

Execution repository for `【114 Spring】132603 智慧生醫概論 Introduction of Smart
Biomedicine`.

## Scope

This repo owns the final-report production package: Markdown report, narration
script, TTS chunk sources, QA gates, recording surface, provenance helpers, and
delivery evidence templates.

The planning repo remains the control plane for deadlines, capacity, Padlet /
YouTube status, peer engagement, and submission evidence:

`../planning-everything-track/data/projects/2026-06-smart-biomedicine-final-report.md`

## Current Topic

`從語音問診到醫師摘要：ASR + LLM 在智慧生醫臨床前問診中的應用與邊界`

Working English title:

`From Speech Intake to Clinician Summary: ASR and LLMs for Smart Biomedical Pre-visit Workflows`

## Key Paths

- Project package: `data/projects/2026-06-smart-biomedicine-final-report/`
- Current BreezyVoice plan:
  `data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-current-execution-plan-v1.md`
- Markdown report:
  `data/projects/2026-06-smart-biomedicine-final-report/markdown-report-v1.md`
- Narration script:
  `data/projects/2026-06-smart-biomedicine-final-report/markdown-report-20min-script-v2.md`
- Recording cue sheet:
  `data/projects/2026-06-smart-biomedicine-final-report/video-recording-cue-sheet-v1.md`
- Tools: `data/projects/2026-06-smart-biomedicine-final-report/tools/`
- Reusable TTS methodology: `docs/tts-methodology/`
- TTS experiment cards: `logs/tts-experiments/`
- Repo-safe TTS auto-QA summaries: `qa/tts-auto-checks/`
- Local generated artifacts: `exports/`
- Local-only TTS assets: `assets/tts-local-only/`

## Local Artifact Policy

`exports/` is intentionally ignored. It may contain generated WAVs, ASR reports,
review packets, stitched audio, recording HTML, and submission proof drafts.
Keep these local unless a specific final artifact is deliberately selected for
tracking.

## Common Gates

Run from the repo root:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/breezyvoice_audio_gate_status.py
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/breezyvoice_objective_audit.py
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/artifact_provenance_manifest.py --export-root exports/smart-biomedicine-breezyvoice --engine-label BreezyVoice-26
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_recording_html.py --export-root exports/smart-biomedicine-breezyvoice
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/video_recording_gate_status.py --export-root exports/smart-biomedicine-breezyvoice --engine-label BreezyVoice-26
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/final_video_gate_status.py --export-root exports/smart-biomedicine-breezyvoice
```

## Reusable TTS Research-Audio Workflow

Future TTS research audio should use the methodology in
`docs/tts-methodology/`. The production gate is automated or semi-automated:
ASR back-transcription, pronunciation/critical-term checks, audio-quality
checks, chunk consistency, and hash/provenance decide acceptance. Subjective
listening can inform repair decisions, but it is not the acceptance gate.

Each TTS run should create a card from `templates/tts-experiment-card.md` under
`logs/tts-experiments/`. Raw reference voice, generated audio, failed samples,
and private model artifacts stay in ignored local/private storage such as
`assets/tts-local-only/` or `exports/`.

## Optional Remotion Render Surface

The repo also contains a Remotion timeline scaffold under `src/` with scene
timings in `src/scenes.ts`. Render inputs live under ignored `public/` paths:
local narration audio, generated scene images, transcript copies, and rendered
MP4 outputs. Use `docs/video_plan.md` and `docs/asset_manifest.md` before
claiming the Remotion render path is complete.

## Attribution Surface

Image-generation attribution for the final video is tracked in
`docs/third_party_attribution.md`. YouTube and Google Drive sidecar text blocks
are tracked in `docs/submission_attribution_texts.md`.

## Delivery Gates

- Upload audiovisual final report to Padlet before `2026-06-13 23:00`.
- Upload video to YouTube or provide the course-accepted audiovisual link.
- Complete peer comment/question and like before `2026-06-17`.
- Answer questions on Jason's own Padlet post before `2026-06-20`.
