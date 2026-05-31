# TTS Auto QA Schema

This schema defines the minimum public-safe evidence package for one TTS auto-QA
run. The package is designed for repeatable teaching, research, and demo audio
production without using subjective listening as the formal gate.

## Output Files

Each run should write these files under a run-specific output directory:

```text
qa_result.json
qa_summary.md
term_error_list.csv
audio_quality_report.json
release_manifest.md
```

## Status Values

```text
accepted_auto_gate
accepted_with_warnings
rejected_text_mismatch
rejected_term_error
rejected_audio_quality
rejected_chunk_boundary
rejected_rights
rejected_platform_smoke
research_use_blocked
```

## Profiles

| Profile | CER | WER | Intended use |
| --- | ---: | ---: | --- |
| `internal_draft` | `<= 0.12` | `<= 0.18` | fast private iteration |
| `teaching_material` | `<= 0.08` | `<= 0.12` | course report, lecture, demo narration |
| `research_stimulus` | `<= 0.05` | `<= 0.08` | research stimuli where audio artifacts affect validity |
| `public_external` | `<= 0.06` | `<= 0.10` | publicly shared audio/video |

For mixed Chinese-English material, normalized CER is the primary similarity
signal. WER remains useful as a supporting signal.

## Minimum JSON Shape

```json
{
  "experiment_id": "EXP-20260531-001",
  "profile": "teaching_material",
  "status": "accepted_auto_gate",
  "source_text_sha256": "",
  "model_facing_text_sha256": "",
  "audio_sha256": [],
  "asr_transcript_sha256": "",
  "metrics": {
    "cer": 0.0,
    "wer": 0.0,
    "critical_term_accuracy": 1.0,
    "missing_critical_terms": [],
    "numeric_mismatches": [],
    "missing_sentence_count": 0,
    "repeated_sentence_count": 0
  },
  "audio_quality": {
    "clipping": false,
    "long_silence_count": 0,
    "integrated_loudness_lufs": -16.0,
    "sample_rate_consistent": true,
    "channel_layout_consistent": true,
    "chunk_loudness_spread_db": 0.0
  },
  "rights": {
    "status": "pass",
    "research_use_blocked": false,
    "external_sharing_blocked": false
  },
  "platform_smoke": {
    "status": "pass",
    "note": ""
  },
  "semantic_drift": {
    "status": "not_run",
    "issues": []
  },
  "warnings": [],
  "reject_reasons": [],
  "next_action": ""
}
```

## Critical Term Aliases

`critical=yes` terms must match the canonical term, preferred reading, or one of
the pipe-separated aliases. A critical term is checked only when that term or
one of its accepted variants appears in the source/model-facing text. This
prevents false rejects when a reusable lexicon contains terms that a specific
script does not use.

## Rights Fields

The rights manifest is required for any run that may leave private storage. For
public sharing, `can_share_externally` must be `yes`. For research stimuli,
`can_use_for_research` must be `yes`. If a real reference voice is used and
consent is missing, the run is blocked for research use.
