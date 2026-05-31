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

The current repo already has ASR, repair, loudness, provenance, and objective
audit helpers. The next implementation step is to combine them into one
project-neutral auto-gate command that emits:

- `term_error_list.csv`
- `tts-auto-qa.json`
- `tts-auto-qa.md`
- per-chunk accepted/rejected status
- final package accepted/rejected status
