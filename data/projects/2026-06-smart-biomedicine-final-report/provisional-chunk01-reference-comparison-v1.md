# Provisional Chunk 01 Reference Comparison v1

Purpose: compare GPT-SoVITS prompt references before committing to the formal `sbm_tts_01_opening.wav` production path.

Status: provisional review only. These WAVs used ASR-draft prompt transcripts, so none of them can be accepted as final production chunks.

## Runtime

- GPT-SoVITS runtime: `/home/jnclaw/every_on_git_jnclaw/GPT-SoVITS`
- GPU: RTX `4090`, `CUDA_VISIBLE_DEVICES=0`
- Target chunk: `sbm_tts_01_opening`
- Current repaired TTS text source: `gpt-sovits-narration-chunks-v1.md`
- Local provisional output directory: `exports/smart-biomedicine-gpt-sovits/chunks-provisional/`

## Outputs

| Variant | Reference prompt | Duration | Volume | ASR sanity result | Recommendation |
| --- | --- | ---: | --- | --- | --- |
| `sbm_tts_01_opening_ref01_repair1.provisional.wav` | `prompt_ref_candidate_01_000009_5p40s.wav` | `75.60s` | mean `-18.9 dB`, max `-1.1 dB` | Keeps general structure but ASR flags student number ending, `A. S. R.`, `near-term`, and `autonomous`. | Backup only. |
| `sbm_tts_01_opening_ref02_repair1.provisional.wav` | `prompt_ref_candidate_02_000036_8p00s.wav` | `80.72s` | mean `-17.9 dB`, max `-0.6 dB` | ASR flags name, student number, title phrase, and clinical-review phrasing. | Reject for first production attempt unless human listening strongly disagrees. |
| `sbm_tts_01_opening_ref04_repair1.provisional.wav` | `prompt_ref_candidate_04_000381_8p00s.wav` | `77.96s` | mean `-16.4 dB`, max `-0.5 dB` | Best ASR sanity result: title, student number, patient-speech question, near-term value, and clinical-review screen are mostly preserved. Still flags name pronunciation and one structured/summarized phrase. | Human-listen first; likely best first production reference if exact transcript is verified. |

## Current Recommendation

Use `prompt_ref_candidate_04_000381_8p00s.wav` as the first human-listening candidate for chunk `01`.

Before formal production:

- [ ] Listen to `prompt_ref_candidate_04_000381_8p00s.wav`.
- [ ] Confirm it has no clipping, harsh distortion, long pause, or unstable microphone distance.
- [ ] Write an exact transcript for that `8.00s` prompt reference.
- [ ] Save the exact transcript as a non-draft text file under the ignored reference workspace.
- [ ] Run `generate_gptsovits_chunk.py` for `sbm_tts_01_opening`.
- [ ] Listen to the resulting formal chunk before generating chunks `02-14`.

## Important Finding

The first provisional pass exposed a TTS-specific script issue: acronym spelling such as `A-S-R`, `L-L-M`, and `A-I` was unstable in GPT-SoVITS English output. The chunk script was repaired to use more spoken forms such as `A. S. R.`, `large language model`, and `artificial intelligence`.

This repair should be treated as an audio-production improvement, not a change to the report argument.
