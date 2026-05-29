# GPT-SoVITS Audio QA Sheet v1

Use this sheet after each GPT-SoVITS chunk is generated. Do not stitch a chunk until its row is marked `accepted`.

## Global Acceptance Rules

- Runtime proof: RTX 4090 GPU used; no CPU fallback.
- Reference proof: selected reference WAV has an exact transcript accepted through the `breeze-asr-25` CUDA transcript gate.
- Reference acceptance proof: selected reference has an accepted marker under `exports/smart-biomedicine-gpt-sovits/qa/reference-decisions/`.
- Format proof: generated output is WAV master.
- Loudness proof: generated chunks have a loudness report before final stitching.
- Term proof: `term_consistency_gate.py` passes before formal generation.
- Meaning proof: generated speech preserves technical meaning.
- Visual proof: Markdown scroll timing matches the spoken section.
- Acceptance proof: accepted chunks must have local accepted marker files under `exports/smart-biomedicine-gpt-sovits/qa/chunk-decisions/`.
- Fallback proof: if chunk `01` or chunk `14` uses real voice fallback audio, a fallback manifest must exist under `exports/smart-biomedicine-gpt-sovits/qa/fallback-chunks/`, and the chunk still needs `breeze-asr-25` transcript-gate acceptance.

## Chunk QA Table

| Chunk | Planned WAV | Generated | ASR gate | Accepted | Required checks |
| --- | --- | --- | --- | --- | --- |
| `sbm_tts_01_opening` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_01_opening.wav` | `[ ]` | `[ ]` | `[ ]` | identity, topic, `A. S. R.`, `large language model`, no drift |
| `sbm_tts_02_markdown_format` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_02_markdown_format.wav` | `[ ]` | `[ ]` | `[ ]` | Markdown, Mermaid, visual pacing |
| `sbm_tts_03_definitions` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_03_definitions.wav` | `[ ]` | `[ ]` | `[ ]` | definitions, acronyms, no skipped term |
| `sbm_tts_04_workflow_problem` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_04_workflow_problem.wav` | `[ ]` | `[ ]` | `[ ]` | first Mermaid diagram timing |
| `sbm_tts_05_speech_to_summary` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_05_speech_to_summary.wav` | `[ ]` | `[ ]` | `[ ]` | second Mermaid diagram timing |
| `sbm_tts_06_evidence_landscape` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_06_evidence_landscape.wav` | `[ ]` | `[ ]` | `[ ]` | report tone, no machine-reading rush |
| `sbm_tts_07_hager_boundary` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_07_hager_boundary.wav` | `[ ]` | `[ ]` | `[ ]` | `HAY-ger`, clinical boundary meaning |
| `sbm_tts_08_lang1_overview` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_08_lang1_overview.wav` | `[ ]` | `[ ]` | `[ ]` | `Jee-ang`, `Lang One`, source figure hold |
| `sbm_tts_09_lang1_results` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_09_lang1_results.wav` | `[ ]` | `[ ]` | `[ ]` | `Reh-Med-Ee`, results meaning, figure hold |
| `sbm_tts_10_architecture` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_10_architecture.wav` | `[ ]` | `[ ]` | `[ ]` | architecture decision node, no skipped step |
| `sbm_tts_11_scope_controls` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_11_scope_controls.wav` | `[ ]` | `[ ]` | `[ ]` | may-do / must-not-do boundary |
| `sbm_tts_12_synthetic_example` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_12_synthetic_example.wav` | `[ ]` | `[ ]` | `[ ]` | synthetic-only framing, no medical-advice tone |
| `sbm_tts_13_validation_risk` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_13_validation_risk.wav` | `[ ]` | `[ ]` | `[ ]` | validation layers, no rushed list |
| `sbm_tts_14_closing` | `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_14_closing.wav` | `[ ]` | `[ ]` | `[ ]` | final takeaway, `Soh-Vits`, `Pad-let` |

## Per-Chunk Checklist

For every accepted row, the ASR-led gate must prove:

- [ ] `breeze-asr-25` ran on RTX `4090` CUDA with no CPU fallback.
- [ ] Normalized ASR transcript matches the source chunk text.
- [ ] No missing words, repeated phrase, or swallowed ending appears in the transcript.
- [ ] Required terms and names are preserved in the transcript.
- [ ] Ambiguous terms have enough local before-and-after context for ASR to disambiguate them.
- [ ] Prosody is encoded with plain text rhythm: short sentences, clear pauses, and standalone safety/scope-control sentences.
- [ ] A repair plan exists for every rejected transcript gate.
- [ ] Volume fits neighboring chunks through `audio_loudness_gate.py`.

## Notes

- Chunk 01 is the preflight gate. Do not generate chunks 02-14 until chunk 01 is accepted by `breeze-asr-25`.
- If two consecutive chunks fail for the same reason, stop and change reference audio or GPT-SoVITS settings before continuing.
- If generated speech changes technical meaning, reject even if voice quality is good.
- If ASR repeatedly confuses a phrase because the chunk lacks context, add a short setup or consequence sentence instead of only changing one word.
- If negation or clinical scope is important, put it in a standalone sentence so ASR has a clear pause boundary.
- Use `chunk_asr_qa.py --gate --auto-decision` after each generated chunk. Stitching refuses to run without accepted marker files for all `14` chunks.
- Use `audio_loudness_gate.py` before stitching so volume jumps are found before the video-recording pass.
- Use `term_consistency_gate.py` before formal generation and again after any TTS text edit.
- If GPT-SoVITS identity is unstable, use `register_human_fallback_chunk.py` only for chunk `01` and/or chunk `14`, then run the same `breeze-asr-25` transcript gate before acceptance.
