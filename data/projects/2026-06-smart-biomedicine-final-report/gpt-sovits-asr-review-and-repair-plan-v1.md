# GPT-SoVITS ASR Review And Repair Plan v1

Purpose: replace mandatory human listening gates with a repeatable `breeze-asr-25` transcript gate for the Smart Biomedicine final-report narration.

## Operating Rule

- Run every local ASR check with `breeze-asr-25` on RTX `4090` CUDA.
- Do not accept CPU fallback.
- Do not generate the next chunk until the current chunk has an accepted marker.
- If the ASR transcript does not match the source chunk text, reject the chunk, write a repair plan, apply the smallest wording repair, regenerate only that chunk, and rerun the gate.
- If the ASR score passes but a phrase changes meaning, treat it as a polish-repair failure and rerun the chunk before continuing.
- After an automatic accepted marker is written, perform a semantic sweep against the ASR transcript. If the transcript reverses a safety boundary, staff-review control, rejectability, or clinical-authority phrase, downgrade the chunk to rejected before repair.
- Do not treat a short local chunk as enough context when a phrase is semantically ambiguous. Add local before-and-after context inside the chunk text before rerunning ASR.
- Add plain-text prosody through shorter sentences, commas, and standalone scope-control sentences. Do not use decorative punctuation or SSML-style tags unless the runtime explicitly supports them.
- Human listening is now an exception path for ambiguous or repeatedly unstable ASR results, not the default acceptance gate.

## ASR Context And Prosody Control

`breeze-asr-25` is a speech recognizer, not a clinical reviewer. It performs better when the spoken phrase carries enough local context. When a chunk is short, dense, or full of ambiguous clinical terms, the ASR pass can misread a word even when the audio sounds plausible.

Use these repair rules before lowering the acceptance standard:

- Add local context before ambiguous terms: `The safety boundary is...`, `The staff review step is...`, `The output is for intake review...`.
- Add local context after high-risk phrases: `This means staff check the draft before care decisions.`
- Put negation and scope control in their own sentence: `Staff review comes first.` `Automatic medical action is outside the scope.`
- Replace fragile letter acronyms with full phrases unless the acronym itself is required for the report section.
- Avoid isolated single-word contrasts such as `review`, `surface`, `authority`, or `triage` without a nearby meaning cue.
- Prefer short affirmative scope sentences over compressed negative clauses when the ASR repeatedly loses `not`.
- Add commas and periods to create clear pause points. Use text-level rhythm: setup, key phrase, pause, consequence.
- Keep repairs semantically faithful to the report. A repair can simplify wording, but it must not change the claim.

## Default Command

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/chunk_asr_qa.py \
  --chunk-id sbm_tts_01_opening \
  --language en \
  --gate \
  --auto-decision
```

Outputs:

- ASR report: `exports/smart-biomedicine-gpt-sovits/qa/chunk-asr/<chunk-id>.asr-qa.md`
- ASR JSONL log: `exports/smart-biomedicine-gpt-sovits/qa/experiment-logs/chunk-asr-gates.jsonl`
- Generation JSONL log: `exports/smart-biomedicine-gpt-sovits/qa/experiment-logs/chunk-generations.jsonl`
- Accepted marker, if passed: `exports/smart-biomedicine-gpt-sovits/qa/chunk-decisions/<chunk-id>.accepted.md`
- Rejected marker, if failed: `exports/smart-biomedicine-gpt-sovits/qa/chunk-decisions/<chunk-id>.rejected.md`
- Repair plan, if failed: `exports/smart-biomedicine-gpt-sovits/qa/chunk-repairs/<chunk-id>.repair-plan.md`

## Pass Criteria

- `nvidia-smi` proves an RTX `4090` is visible.
- The ASR runtime prints `device=cuda`.
- The normalized ASR transcript reaches the configured token-ratio threshold.
- Critical phrases expected in the source text are present in the ASR transcript.
- Scope-control phrases and clinical responsibility phrases keep the same meaning.
- Prosody/context repairs have been applied for any phrase that repeatedly fails because the chunk lacks enough local context.
- The generated decision marker records `breeze_asr_25_cuda`, `breeze_asr_25_transcript_pass`, and `transcript_matches_source`.

## Repair Strategy

Use the smallest text change that makes the transcript stable:

- Convert punctuation-sensitive acronyms to spaced letters, for example `A S R` instead of `A. S. R.`.
- Convert hyphenated technical terms into spaced terms, for example `large language model`, `pre visit`, and `clinician ready`.
- If GPT-SoVITS skips a short sentence, split it into a standalone sentence before the next technical phrase.
- If the same term fails twice, simplify the wording while keeping the report meaning unchanged.
- If the same term fails because the chunk is too context-poor, add a short setup sentence or consequence sentence rather than only changing the term.

After a repair:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/export_tts_chunks.py
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/generate_gptsovits_chunk.py \
  --chunk-id <chunk-id> \
  --ref-audio exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_04_000381_8p00s.wav \
  --ref-text exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_04_000381_8p00s.exact-transcript.txt
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/chunk_asr_qa.py \
  --chunk-id <chunk-id> \
  --language en \
  --gate \
  --auto-decision
```

## Current Gate

Chunks `01-06` are generated and accepted by the ASR gate. Chunk `06` passed after source/export refresh, local context repair, plain-text prosody repair, and semantic sweep for safety-boundary and clinical-authority meaning. The current gate is to generate chunk `07`, run `chunk_asr_qa.py --chunk-id sbm_tts_07_hager_boundary --gate --auto-decision`, and repair any remaining mismatch before chunk `08`.
