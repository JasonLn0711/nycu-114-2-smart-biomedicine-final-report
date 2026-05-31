# TTS Auto Checks

This folder stores repo-safe summaries of automated TTS QA evidence. Raw audio,
reference voice, generated WAV/MP3/M4A files, failed samples, and model outputs
must stay in `assets/tts-local-only/` or ignored `exports/` paths.

Required public-safe QA evidence:

- source/model-facing text path and hash
- model/checkpoint/runtime summary
- generation command
- output hash
- ASR back-transcription result
- CER/WER or current substitute score
- critical-term accuracy
- audio-quality result
- chunk-consistency result
- accepted/rejected decision

Runnable MVP evidence package:

- `EXP-20260531-001/qa_result.json`
- `EXP-20260531-001/qa_summary.md`
- `EXP-20260531-001/term_error_list.csv`
- `EXP-20260531-001/audio_quality_report.json`
- `EXP-20260531-001/release_manifest.md`

The active methodology is documented in
`docs/tts-methodology/tts-research-audio-methodology-v1-zh-tw.md`.
