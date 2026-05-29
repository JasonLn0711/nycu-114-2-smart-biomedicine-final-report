# GPT-SoVITS Current Execution Plan v1

Status: legacy evidence. Jason switched the active TTS route to BreezyVoice 26 after GPT-SoVITS chunks `01-06` were accepted. Use `breezyvoice-current-execution-plan-v1.md` for the current production gate.

This file is the concrete next-action plan for producing the Smart Biomedicine final-report narration and video with GPT-SoVITS.

Canonical report surface: `markdown-report-v1.md`
TTS chunk source: `gpt-sovits-narration-chunks-v1.md`
Production runbook: `gpt-sovits-production-runbook-v1.md`
ASR review and repair plan: `gpt-sovits-asr-review-and-repair-plan-v1.md`
Reference gate dashboard: `exports/smart-biomedicine-gpt-sovits/review-packet/human-gate-dashboard/index.html`
Reference listening workbook: `exports/smart-biomedicine-gpt-sovits/review-packet/reference-listening-workbook/index.html`
Chunk QA workbook: `exports/smart-biomedicine-gpt-sovits/review-packet/chunk-qa-workbook/index.html`
Reference decision status: `exports/smart-biomedicine-gpt-sovits/qa/reference-decisions/reference-decision-status.md`
Production objective audit: `exports/smart-biomedicine-gpt-sovits/qa/production-objective-audit.md`
Generated artifact root: `exports/smart-biomedicine-gpt-sovits/`

## First Principle

Scarce resource: credible `20` minute course-report delivery before the Padlet deadline, not raw model runtime.

The correct workflow is evidence-gated:

1. choose one clean authorized reference,
2. write an exact transcript,
3. generate one chunk,
4. run `breeze-asr-25` transcript gate and accept or repair,
5. continue one chunk at a time,
6. stitch only accepted chunks,
7. record the Markdown report surface,
8. preserve submission proof.

## Current State

- Reference audio candidates: prepared.
- Reference visual QC: prepared.
- Reference gate dashboard: prepared.
- Reference workbook with slowed review audio: prepared.
- Per-chunk QA workbook for generated WAV ASR transcript review: prepared.
- Accept/reject reference decision status and next-candidate routing: prepared.
- Objective-level audit for the full eight-part production plan: prepared.
- GPT-SoVITS CUDA runtime: prepared on RTX `4090`.
- `breeze-asr-25` CUDA preflight: prepared.
- Narration chunk plan: `14` chunks prepared.
- Formal chunks: `6/14`.
- Accepted chunk QA: `6/14`.
- Current blocking gate: generate chunk `07`, run the `breeze-asr-25` transcript gate, perform semantic sweep, and repair any remaining mismatch before chunk `08`.

## Immediate Next 60-90 Minutes

1. Generate the next formal chunk after the accepted chunk `06` marker:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/generate_next_chunk_after_acceptance.py \
  --chunk-id sbm_tts_07_hager_boundary
```

2. Run the ASR transcript gate for chunk `07` on RTX `4090` CUDA:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/chunk_asr_qa.py \
  --chunk-id sbm_tts_07_hager_boundary \
  --language en \
  --gate \
  --auto-decision
```

3. If the gate fails or semantic sweep finds a meaning-changing phrase, use the generated repair plan:

```bash
ls exports/smart-biomedicine-gpt-sovits/qa/chunk-repairs/
```

4. Apply the smallest chunk-text repair, re-export chunk text, regenerate only the failed chunk, and rerun the same ASR gate:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/export_tts_chunks.py
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/generate_gptsovits_chunk.py \
  --chunk-id sbm_tts_07_hager_boundary \
  --ref-audio exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_04_000381_8p00s.wav \
  --ref-text exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_04_000381_8p00s.exact-transcript.txt
```

5. Rebuild gate dashboards after each accept or repair:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_chunk_qa_workbook.py
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/gptsovits_audio_gate_status.py
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/production_objective_audit.py
```

Repeat ASR gate -> accept/repair -> next chunk until `14/14` chunks are accepted.

## Reference Audio Selection

- Do not pass the whole `11:42` MP3 into GPT-SoVITS as one reference.
- Use the machine-selected `3-10s` prompt candidates under `exports/smart-biomedicine-gpt-sovits/reference/`.
- Prefer formal tone, stable volume, quiet background, no laughter, no long pause, no heavy filler, and clear mic distance.
- Use the visual QC report before final acceptance:

```text
exports/smart-biomedicine-gpt-sovits/qa/reference-visual-qc/reference-visual-qc.md
```

- Machine QA and `breeze-asr-25` transcript matching own the default decision. Human listening is now an exception path only when ASR is ambiguous or repeatedly unstable.

## Reference Transcript

- Every production prompt reference needs an exact transcript.
- `breeze-asr-25` transcript output becomes the default review evidence only when it runs on RTX `4090` CUDA.
- If the transcript cannot be aligned exactly, reject or repair the reference.
- Start with one `5-15s` prompt-mode reference, practically `3-10s` for the current GPT-SoVITS runtime.
- If zero-shot voice identity is unstable, use the `48s` adaptation review set only after ASR transcript coverage.

## Narration Generation

- Use the `14` chunks in `gpt-sovits-narration-chunks-v1.md`.
- Generate one WAV per chunk.
- Do not synthesize the full `20` minute report in one pass.
- Do not generate chunks `02-14` before chunk `01` is ASR-accepted.
- Use RTX `4090` only; CPU fallback is a stop condition.

## Per-Chunk Audio QA

Each chunk needs `breeze-asr-25` transcript-gate acceptance before the next chunk:

- ASR must run on RTX `4090` CUDA with no CPU fallback.
- normalized transcript must match the source chunk text,
- required terms such as `A-S-R`, `L-L-M`, `HAY-ger`, `Jee-ang`, `Lang One`, `Reh-Med-Ee`, `Soh-Vits`, and `Pad-let` must be preserved,
- context-sensitive phrases must include enough before-and-after wording for ASR to disambiguate them,
- prosody must be encoded in plain text through short sentences, clear commas, and standalone safety/scope-control sentences,
- failed transcript gates must produce a repair plan before regeneration,
- volume consistency remains covered by `audio_loudness_gate.py`.

Run the audio gate after each meaningful batch:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/gptsovits_audio_gate_status.py
```

Rebuild the chunk QA workbook after each new formal WAV or chunk decision:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_chunk_qa_workbook.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/review-packet/chunk-qa-workbook/index.html`

Run the objective audit when deciding whether the full workflow is ready to advance:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/production_objective_audit.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/qa/production-objective-audit.md`

## Stitching

- Stitch only after `14/14` formal WAVs exist and `14/14` accepted markers exist.
- Add `0.35-0.7s` silence between chunks.
- Keep the stitched WAV master.
- Do not compress to MP3/AAC until the WAV master passes review.

Command:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/stitch_accepted_chunks.py --silence 0.5
```

## Video Recording

- Use `markdown-report-v1.md` through the generated browser recording surface.
- Scroll with the stitched audio, not faster than the narration.
- Hold Mermaid diagrams and paper figures for `45-90s`.
- Target final video length: `19-20` minutes.
- Use the cue sheet and video QA sheet before recording.
- Close unrelated tabs, terminals, and notifications before recording.

## Fallback Path

If GPT-SoVITS sounds too synthetic or unstable:

- record Jason real voice for `sbm_tts_01_opening`,
- use GPT-SoVITS for `sbm_tts_02` through `sbm_tts_13`,
- record Jason real voice for `sbm_tts_14_closing`.

Register fallback audio with:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/register_human_fallback_chunk.py \
  --chunk-id sbm_tts_01_opening \
  --source-audio /path/to/jason-recorded-opening.wav \
  --ack-own-voice \
  --ack-recorded-for-this-report \
  --ack-content-matches-chunk \
  --ack-no-private-content
```

Use `--chunk-id sbm_tts_14_closing` for the closing fallback.

## Submission Plan

External hard gates:

- `2026-06-13 23:00`: Padlet upload deadline.
- `2026-06-17`: watch at least one classmate report, comment or ask a question, and like it.
- `2026-06-20`: answer questions on Jason's own report.

Internal safe gates:

- `2026-06-10`: finish reference acceptance and first formal chunk.
- `2026-06-11`: finish `14/14` generated and accepted narration chunks.
- `2026-06-12`: stitch WAV, record video, upload YouTube as unlisted or public according to course preference.
- `2026-06-13`: Padlet post and proof capture only, not first render.

Proof files:

- `exports/smart-biomedicine-gpt-sovits/submission/youtube-url.txt`
- `exports/smart-biomedicine-gpt-sovits/submission/padlet-post-proof.md`
- `exports/smart-biomedicine-gpt-sovits/submission/peer-engagement-proof.md`
- `exports/smart-biomedicine-gpt-sovits/submission/presenter-response-proof.md`

## Important Additions

These controls are important even though they were not the headline of the earlier plan.

1. Voice authorization and disclosure: the source voice is Jason's own voice. If the course expects disclosure, use: `Narration was produced from my own script using my own authorized voice with AI-assisted text-to-speech for recording support.`
2. Exact-transcript integrity: do not use ASR draft text as production prompt text. A slightly wrong prompt transcript can degrade identity, prosody, and intelligibility.
3. Source-figure readability: the final video must pause long enough for paper figures and figure-text explanations. A correct audio track can still fail as a report if the screen moves too quickly.
4. Upload resilience: finish rendering before the deadline day. Treat `2026-06-13` as upload/proof day, not production day.
5. ASR context window: when a chunk is short, ASR can misread terms without enough surrounding meaning. Repair by adding local context and pause rhythm before changing thresholds.
6. Prosody as text: use sentence breaks and short setup/consequence sentences to create practical `抑、揚、頓、挫`; avoid unsupported markup.
5. Local privacy: keep raw voice, generated chunks, ASR drafts, and failed synthesis artifacts out of Git and public uploads.
6. Version freeze: after formal generation starts, do not silently edit `gpt-sovits-narration-chunks-v1.md`; create `v2` if wording changes are necessary.
7. Playback consistency: listen with the same headphones or speakers during QA when possible, and check at least one phone/laptop playback before upload.
8. File provenance: refresh the artifact provenance manifest before final upload so the final video can be traced back to the report, chunks, source figures, and submission proof.
9. Human identity: if the fully synthetic version feels detached, use the opening/closing fallback. The goal is a credible course report, not maximal automation.
10. Stop rule: any CPU fallback, severe clipping, transcript mismatch, or technical-term meaning change stops production until fixed.
