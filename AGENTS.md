# AGENTS.md

This repository owns the execution package for the NYCU 114-2 Smart Biomedicine
final report.

## Mission

Produce, verify, and submit the course final-report audiovisual package:

- Markdown report
- 20-minute narration script
- TTS chunk sources
- ASR / semantic QA gates
- recording surface
- provenance manifests
- final delivery evidence

## Ownership Boundary

This repo owns execution artifacts and validation mechanics.

The planning repo at `../planning-everything-track` owns only:

- deadline and capacity tracking
- Padlet / YouTube / peer-engagement status
- submission evidence locator
- high-level next action

Do not move day planning, weekly planning, or broad personal operating-system
logic into this repo.

## Working Rules

1. Keep commands runnable from the repository root.
2. Keep generated media and local QA outputs under `exports/`.
3. Track source Markdown, scripts, runbooks, and lightweight manifests.
4. Do not commit raw private voice recordings, generated WAVs, rendered videos,
   or local model artifacts unless the user explicitly asks.
5. Preserve the course scope: staff-review previsit intake support, no real
   patient data, no autonomous diagnosis, no autonomous triage, and no
   autonomous treatment planning.
6. Use evidence-led, positive-scope writing for report-facing prose:
   claim -> evidence -> contribution -> scope control -> next implication.
7. Keep clinical and safety boundaries visible as validation layers and
   claim-evidence alignment.

## Canonical Paths

- Project package: `data/projects/2026-06-smart-biomedicine-final-report/`
- Current execution plan:
  `data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-current-execution-plan-v1.md`
- Markdown report:
  `data/projects/2026-06-smart-biomedicine-final-report/markdown-report-v1.md`
- Narration script:
  `data/projects/2026-06-smart-biomedicine-final-report/markdown-report-20min-script-v2.md`
- Tools: `data/projects/2026-06-smart-biomedicine-final-report/tools/`
- Local generated artifacts: `exports/`

## Verification

Before claiming the package is ready, run the relevant gate scripts from this
repo root and inspect their output. Prefer narrow evidence over broad claims.
