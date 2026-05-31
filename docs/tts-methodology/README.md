# TTS Methodology Index

This folder defines the reusable TTS research-audio workflow for future
research, teaching, presentation, clinical-previsit simulation, and ASR/LLM demo
materials.

The operating rule is that generated speech is accepted by automated or
semi-automated QA gates, not by subjective listening approval. Human review may
read machine reports, but the production gate should be based on ASR
back-transcription, critical-term checks, audio-quality checks, chunk
consistency, and provenance.

## Documents

- `tts-reproducible-research-notes-cybersec-smart-biomedicine-v1-zh-tw.md`:
  cross-project reproducible research note combining the CYBERSEC / CDE
  BreezyVoice production experience with the Smart Biomedicine BreezyVoice,
  F5-TTS, and GPT-SoVITS evidence, plus web-verified 2026-05-31 technology
  stack updates.
- `tts-research-audio-methodology-v1-zh-tw.md`: full production methodology.
- `tts-text-design-guide.md`: model-facing text design rules.
- `tts-auto-qa-rubric.md`: automated acceptance thresholds.
- `tts-auto-qa-schema.md`: JSON/Markdown/CSV evidence-package schema for the
  runnable auto-QA gate.
- `tts-failure-taxonomy.md`: repair-oriented error categories.
- `tts-ethics-rights-and-disclosure.md`: voice rights, consent, and storage
  record.
- `tts-platform-delivery-qa.md`: final-video and platform smoke checks kept
  outside the core TTS methodology.
- `tts-model-comparison-summary.md`: summary of this project's BreezyVoice,
  F5-TTS, and GPT-SoVITS attempts.

## Runnable MVP

The current runnable gate is:

```bash
python3 tools/run_tts_auto_qa.py \
  --source-text data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-narration-chunks-v1.md \
  --model-facing-text data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-narration-chunks-v1.md \
  --asr-transcript exports/smart-biomedicine-breezyvoice/qa/chunk-asr \
  --lexicon templates/tts-pronunciation-lexicon.csv \
  --audio-dir exports/smart-biomedicine-breezyvoice/chunks \
  --rights-manifest qa/tts-auto-checks/EXP-20260531-001/rights-manifest.yaml \
  --profile teaching_material \
  --experiment-id EXP-20260531-001 \
  --out qa/tts-auto-checks/EXP-20260531-001
```

It emits `qa_result.json`, `qa_summary.md`, `term_error_list.csv`,
`audio_quality_report.json`, and `release_manifest.md`.

## Templates And Logs

- `../../templates/tts-experiment-card.md`: required card for each TTS run.
- `../../templates/tts-pronunciation-lexicon.csv`: critical-term lexicon
  template with alias support.
- `../../templates/tts-run-environment.yaml`: runtime, model snapshot,
  command, parameter, and hash manifest for reproducible TTS generation.
- `../../templates/tts-rights-manifest.yaml`: rights and disclosure manifest.
- `../../templates/tts-golden-pilot-manifest.yaml`: stable pilot set for
  cross-model comparison.
- `../../templates/tts-term-error-list.csv`: term-error report template.
- `../../golden_pilots/`: opening, mixed-term, and case-story pilot texts.
- `../../logs/tts-experiments/`: tracked experiment cards.
- `../../qa/tts-auto-checks/`: repo-safe QA summaries.
- `../../assets/tts-local-only/`: ignored local-only storage for reference
  audio, generated audio, and failed samples.
