# TTS Auto QA Summary - 2026-05-31

This summary converts the Smart Biomedicine TTS work into repo-safe automated QA
evidence for future reuse.

| Experiment | Model | Evidence Level | Current Decision | Main Evidence |
| --- | --- | --- | --- | --- |
| `EXP-20260528-001` | BreezyVoice 26 | strongest | accepted for final package | `14` chunk WAVs, `14` ASR reports, `14` accepted markers, `14` semantic-sweep markers, stitched master SHA256, loudness/final-video QA in ignored exports |
| `EXP-20260528-002` | F5-TTS `F5TTS_v1_Base` | candidate | hold/reject for final package | `14` chunk WAVs and stitched candidate master exist, but full ASR/term/audio/chunk gates were not completed |
| `EXP-20260528-003` | GPT-SoVITS | historical | rejected for final package, accepted as repair evidence | detailed repair history, repeated ASR mismatch patterns, and critical phrase lessons |

## Active Acceptance Rule

Future TTS outputs should not be accepted through subjective listening. The
acceptance gate should require:

```text
CER <= 8%
WER <= 12%
Critical term accuracy = 100%
No clipping
No abnormal silence > 2.0 sec
No broken chunk boundary
No meaning-changing omission
Complete provenance
```

## Immediate Tool Gap

The current repo now has one project-neutral auto-gate command:

```bash
python3 tools/run_tts_auto_qa.py \
  --asr-report-dir exports/smart-biomedicine-breezyvoice/qa/chunk-asr \
  --model-facing-text data/projects/2026-06-smart-biomedicine-final-report/breezyvoice-narration-chunks-v1.md \
  --lexicon templates/tts-pronunciation-lexicon.csv \
  --audio-dir exports/smart-biomedicine-breezyvoice/chunks \
  --rights-manifest qa/tts-auto-checks/EXP-20260531-001/rights-manifest.yaml \
  --profile teaching_material \
  --experiment-id EXP-20260531-001 \
  --out qa/tts-auto-checks/EXP-20260531-001
```

The first BreezyVoice package run emitted:

- `qa_result.json`
- `qa_summary.md`
- `term_error_list.csv`
- `audio_quality_report.json`
- `release_manifest.md`

Result: `accepted_with_warnings`.

Key metrics:

- `CER = 0.0087`
- `WER = 0.0175`
- `critical_term_accuracy = 1.0000`
- `audio_files_checked = 14`
- `audio_status = pass`
- `rights_status = pass`

Warnings are delivery/edge-review items rather than hard rejects:

- `platform_smoke_check = not_run`
- audio peak is close to `0 dBFS`; limiter behavior should be confirmed before
  future public releases.
- fuzzy sentence matching reported `missing_sentence_count=2`; this is a watch
  item because CER/WER and critical-term accuracy are already within the
  teaching-material gate.
