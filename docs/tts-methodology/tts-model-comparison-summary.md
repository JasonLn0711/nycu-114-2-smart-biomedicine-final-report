# TTS Model Comparison Summary

This table summarizes the Smart Biomedicine final-report TTS attempts and turns
them into reusable evidence for future research-audio production.

| model | strength | weakness | accepted use | rejected use | next test |
| --- | --- | --- | --- | --- | --- |
| BreezyVoice 26 / `MediaTek-Research/BreezyVoice-300M` | Produced the accepted final narration route after chunk-level repair, ASR back-transcription, semantic/critical phrase checks, stitching, loudness QA, and provenance capture. Strong for Taiwanese Mandarin and code-switching, and usable for English when text is simplified. | English dense noun phrases, acronyms, negation, and clinical-boundary wording required repeated model-facing text repair. Future workflow should convert historical semantic sweeps into deterministic critical-term checks. | Final Smart Biomedicine narration package and future long-form research narration when chunked and gated. | Ungated one-pass English long-form generation; stale-source audio; CPU fallback. | Add automated CER/WER, critical-term CSV comparison, silence/clipping scanner, and chunk-boundary checker into one command. |
| F5-TTS `F5TTS_v1_Base` | Generated all `14` chunks on RTX 5080 with a clear manifest and repeatable command. Fast candidate route for pilot voice generation. | The generated master was shorter than the accepted BreezyVoice target and did not yet pass the same ASR/term/audio/chunk gates. | Future pilot clips and model comparison baselines. | Final research package before ASR back-transcription and audio QA are added. | Run the same automated QA rubric and compare CER/WER, critical-term accuracy, loudness, and chunk consistency against BreezyVoice. |
| GPT-SoVITS | Produced detailed repair history and many useful failure patterns for text design, ASR gate design, critical phrase lists, and pronunciation instability. | Historical accepted markers do not transfer after a model switch; earlier flow depended on manual semantic sweep and did not represent the final route. | Failure taxonomy, text-repair rules, pronunciation lexicon seeds, and historical comparison. | Final package after switching to BreezyVoice; any route without current-source provenance. | Re-run a small pilot under the new automated rubric only if a future project needs a GPT-SoVITS baseline. |

## Decision

Use BreezyVoice-style chunked generation plus automated QA as the current
reference workflow. Treat F5-TTS and GPT-SoVITS as candidate or historical
routes until they pass the same automated gates.
