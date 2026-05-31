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

- `tts-research-audio-methodology-v1-zh-tw.md`: full production methodology.
- `tts-text-design-guide.md`: model-facing text design rules.
- `tts-auto-qa-rubric.md`: automated acceptance thresholds.
- `tts-failure-taxonomy.md`: repair-oriented error categories.
- `tts-ethics-rights-and-disclosure.md`: voice rights, consent, and storage
  record.
- `tts-model-comparison-summary.md`: summary of this project's BreezyVoice,
  F5-TTS, and GPT-SoVITS attempts.

## Templates And Logs

- `../../templates/tts-experiment-card.md`: required card for each TTS run.
- `../../templates/tts-pronunciation-lexicon.csv`: critical-term lexicon
  template.
- `../../templates/tts-term-error-list.csv`: term-error report template.
- `../../logs/tts-experiments/`: tracked experiment cards.
- `../../qa/tts-auto-checks/`: repo-safe QA summaries.
- `../../assets/tts-local-only/`: ignored local-only storage for reference
  audio, generated audio, and failed samples.
