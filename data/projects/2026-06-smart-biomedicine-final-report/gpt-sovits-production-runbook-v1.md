# GPT-SoVITS Production Runbook v1

Status: legacy evidence. Jason switched the active Smart Biomedicine TTS route to BreezyVoice 26. Keep this runbook for GPT-SoVITS setup history and ASR-gate lessons; use `breezyvoice-current-execution-plan-v1.md` for current production.

This runbook turns the Smart Biomedicine Markdown report into a controlled GPT-SoVITS narration workflow.

Canonical visual report: `markdown-report-v1.md`
TTS chunk source: `gpt-sovits-narration-chunks-v1.md`
Reference candidates: `reference-audio-candidates-v1.md`
Audio QA sheet: `gpt-sovits-audio-qa-sheet-v1.md`
Current execution plan: `gpt-sovits-current-execution-plan-v1.md`
Local generated artifact root: `exports/smart-biomedicine-gpt-sovits/`

## Non-Negotiable Runtime Rule

- Use RTX 4090 GPU only.
- Do not run GPT-SoVITS generation or local ASR on CPU.
- Set `CUDA_VISIBLE_DEVICES=0`.
- If CUDA fails, stop and fix the GPU runtime. Do not accept CPU fallback.
- Local ASR may use `breeze-asr-25`, but only when it is running on CUDA.

Current verified GPU:

```text
NVIDIA GeForce RTX 4090 Laptop GPU, index 0, 16376 MiB VRAM
```

Current ASR runtime note:

- `breeze-asr-25` is cached locally.
- `project_aura/.venv` has `faster_whisper` and `ctranslate2`.
- CUDA ASR works only after setting the venv-local CUDA library path for `cublas`, `cudnn`, and `cuda_nvrtc`.

Current GPT-SoVITS runtime note:

- Local runtime path: `/home/jnclaw/every_on_git_jnclaw/GPT-SoVITS`
- Runtime source: official `RVC-Boss/GPT-SoVITS` checkout, commit `08d627c`.
- Python runtime: `.venv` with Python `3.11.15`, `torch==2.11.0+cu128`, `torchaudio==2.11.0+cu128`, `torchcodec==0.11.1+cu128`, `onnxruntime-gpu==1.26.0`, and `nvidia-npp-cu12==12.4.1.87`.
- Pretrained model bundle, G2PW, NLTK data, and OpenJTalk dictionary are installed locally.
- CUDA runtime smoke test passed with the helper below:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/gptsovits_cuda_runtime_smoke.py
```

- Smoke output: `exports/smart-biomedicine-gpt-sovits/runtime-smoke/output/output.wav`
- Output facts: `pcm_s16le`, `32000 Hz`, mono, about `5.86s`
- Formal chunks `01-06` have passed the `breeze-asr-25` transcript gate; keep advancing one chunk at a time.
- Provisional chunk `01` reference comparison currently recommends `prompt_ref_candidate_04_000381_8p00s.wav` first. See `provisional-chunk01-reference-comparison-v1.md`.
- Local review packet for the original reference gate:
  `exports/smart-biomedicine-gpt-sovits/review-packet/chunk01-reference-review/index.html`

## Phase 0 - Current Execution Path

For historical reconstruction, use `gpt-sovits-current-execution-plan-v1.md` as the short operational checklist for the earlier GPT-SoVITS session. For current production, use `breezyvoice-current-execution-plan-v1.md`.

Use the objective-level audit to verify the full eight-part plan:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/production_objective_audit.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/qa/production-objective-audit.md`

Current next gate:

1. Generate chunk `07` after the accepted chunk `06` marker.
2. Run `chunk_asr_qa.py --chunk-id sbm_tts_07_hager_boundary --language en --gate --auto-decision`.
3. If the gate passes, run a semantic sweep for safety-boundary, staff-review, and clinical-authority meaning.
4. If the gate or semantic sweep fails, add local context and plain-text pause rhythm, regenerate only chunk `07`, and rerun the ASR gate.
5. Repeat one chunk at a time until `14/14` chunks have accepted markers.

Internal safe schedule:

- `2026-06-10`: reference acceptance and first formal chunk accepted.
- `2026-06-11`: `14/14` generated chunks and `14/14` accepted QA markers.
- `2026-06-12`: stitched WAV master, screen recording, YouTube upload.
- `2026-06-13`: Padlet post and proof capture before `23:00`.

## Phase 1 - Reference Audio Finalization

Input:

- `/home/jnclaw/Downloads/260528_0839_record.mp3`
- Candidate WAV files under `exports/smart-biomedicine-gpt-sovits/reference/`
- Candidate manifest: `reference-audio-candidates-v1.md`

Tasks:

- [ ] Run `breeze-asr-25` on candidate WAVs with RTX `4090` CUDA.
- [ ] Pick one GPT-SoVITS prompt-ready `3-10s` reference WAV.
- [ ] Write an exact transcript for the selected reference segment from ASR-gated evidence.
- [ ] Record an accepted reference marker after ASR transcript verification.
- [ ] Reject or repair any candidate with clipping, room noise, laughter, unstable mic distance, or transcript mismatch.
- [ ] If zero-shot output is unstable, prepare a `45-90s` longer clean reference set from the same source voice.

Recommended first test:

- Listen to `ref_candidate_01_000009_12s.wav` as the review source, then use `prompt_ref_candidate_01_000009_5p40s.wav` as the first prompt-ready GPT-SoVITS reference if the exact transcript is confirmed.

Critical control:

- ASR draft text becomes production evidence only after the CUDA transcript gate is explicitly accepted and recorded.
- Do not feed the `12s` review WAV directly to GPT-SoVITS; local runtime testing showed GPT-SoVITS rejects prompt audio outside the `3-10s` range.
- Do not start formal chunk generation with only an exact-transcript file. Formal generation now also requires an accepted reference marker under `exports/smart-biomedicine-gpt-sovits/qa/reference-decisions/`.
- When ASR confuses a term because the chunk is too short or context-poor, repair by adding nearby meaning context and plain-text prosody before relaxing thresholds.
- Encode `抑、揚、頓、挫` through supported text: short sentences, commas, standalone scope-control lines, and setup/consequence sentences.

Reference transcript review packet:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_reference_transcript_review_packet.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/review-packet/reference-transcript-review/index.html`
- five exact-transcript templates, one for each prompt-ready reference candidate

Reference listening workbook:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_reference_listening_workbook.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/review-packet/reference-listening-workbook/index.html`
- original prompt-reference copies under `exports/smart-biomedicine-gpt-sovits/review-packet/reference-listening-workbook/audio/`
- transcript-aid copies slowed to `0.85x` and attenuated by `-3 dB`

Interpretation: the slowed copies are legacy transcript aids. Production prompt-mode synthesis still uses the original prompt WAV plus an ASR-gated exact transcript.

Reference accept/reject decision status:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/reference_decision_status.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/qa/reference-decisions/reference-decision-status.md`

Interpretation: this report keeps the machine ranking separate from the ASR-led accept/reject decision. It currently recommends checking candidates in this order: `prompt_ref_candidate_04_000381_8p00s`, then `prompt_ref_candidate_01_000009_5p40s`, then `prompt_ref_candidate_02_000036_8p00s`, then `prompt_ref_candidate_03_000072_8p00s`, then `prompt_ref_candidate_05_000480_8p00s`.

Chunk QA workbook:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_chunk_qa_workbook.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/review-packet/chunk-qa-workbook/index.html`
- screenshot proof: `exports/smart-biomedicine-gpt-sovits/review-packet/chunk-qa-workbook/qa/chunk-qa-workbook-top.png`

Interpretation: rebuild this workbook after each formal chunk WAV or chunk review decision. It shows the source text, pronunciation notes, visual hold target, generated audio if present, ASR gate commands, ASR reports, repair plans, and WAV facts for each of the `14` chunks.

Reference gate dashboard:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_human_gate_dashboard.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/review-packet/human-gate-dashboard/index.html`
- screenshot proof: `exports/smart-biomedicine-gpt-sovits/review-packet/human-gate-dashboard/qa/human-gate-dashboard-top.png`

Use this dashboard as a reference page: it shows the five prompt-reference audio players, machine QA metrics, exact transcript targets, command templates, reference transcript gate, and delivery gate.

Reference quality manifest:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_reference_quality_manifest.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/qa/reference-quality/reference-quality-manifest.md`
- `exports/smart-biomedicine-gpt-sovits/qa/reference-quality/reference-quality-manifest.csv`

Interpretation: this is a machine QA screen only. It highlights duration, silence, and near-clipping risk. It does not replace human listening or exact transcript verification.

Reference visual QC:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_reference_visual_qc.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/qa/reference-visual-qc/reference-visual-qc.md`
- waveform and spectrogram PNGs for each prompt-ready reference

Interpretation: visual QC helps spot silence, clipped peaks, and noisy tails before acceptance. It is not a substitute for headphone listening.

Reference transcript gate:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/reference_transcript_gate_status.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/qa/reference-transcript-gate.md`

Interpretation: this checks whether every prompt-ready reference has an exact transcript file and whether an ASR-led decision marker exists. It does not certify speech quality by itself.

After ASR transcript verification accepts the selected reference and the exact transcript file exists, record the marker:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/mark_reference_review_decision.py \
  --candidate prompt_ref_candidate_04_000381_8p00s \
  --decision accepted \
  --exact-transcript exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_04_000381_8p00s.exact-transcript.txt \
  --ack-breeze-asr-25-cuda \
  --ack-breeze-asr-25-transcript-pass \
  --ack-transcript-matches-reference \
  --ack-own-voice-authorized \
  --ack-3-to-10s \
  --ack-clean-audio \
  --ack-no-heavy-filler \
  --ack-no-clipping \
  --ack-transcript-exact
```

To write the exact transcript with explicit ASR acknowledgements:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/create_exact_transcript.py \
  --candidate prompt_ref_candidate_04_000381_8p00s \
  --text "<exact transcript text>" \
  --ack-breeze-asr-25-cuda \
  --ack-breeze-asr-25-transcript-pass \
  --ack-transcript-exact
```

Preferred one-command path after the exact transcript is created:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/advance_after_reference_review.py \
  --candidate prompt_ref_candidate_04_000381_8p00s \
  --accept-reference \
  --ack-breeze-asr-25-cuda \
  --ack-breeze-asr-25-transcript-pass \
  --ack-transcript-matches-reference \
  --ack-own-voice-authorized \
  --ack-3-to-10s \
  --ack-clean-audio \
  --ack-no-heavy-filler \
  --ack-no-clipping \
  --ack-transcript-exact
```

This helper records the accepted reference marker, runs the reference transcript gate, term consistency gate, RTX `4090` / CUDA `breeze-asr-25` preflight, formal chunk `01` generation, and the audio gate status. It stops if any required evidence is missing. The candidate can be changed if ASR-led review chooses another prompt-ready reference; downstream generation resolves the single accepted reference marker rather than hard-coding `ref04`.

Fallback adaptation review set, prepared only for the case where prompt-mode zero-shot identity is unstable:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/prepare_adaptation_clean_set.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/reference/adaptation-clean-set-v1/adaptation_clean_set_v1_review_only.wav`
- `exports/smart-biomedicine-gpt-sovits/reference/adaptation-clean-set-v1/adaptation_clean_set_v1_review_only.md`

Guardrail: this `48s` set is review-only until each included segment is human-listened and covered by an exact transcript bundle.

## Phase 2 - GPT-SoVITS Chunk Generation

Input:

- `gpt-sovits-narration-chunks-v1.md`
- Optional helper: `tools/export_tts_chunks.py`

Output:

- `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_01_opening.wav`
- through
- `exports/smart-biomedicine-gpt-sovits/chunks/sbm_tts_14_closing.wav`

Rules:

- [ ] Generate one chunk at a time.
- [ ] Use the same accepted reference audio and exact prompt transcript unless a chunk clearly fails.
- [ ] Keep WAV output as the master format.
- [ ] Do not batch all chunks without listening.
- [ ] Do not synthesize the full report in one pass.
- [ ] Do not use CPU fallback.

Generation order:

1. Generate `sbm_tts_01_opening`.
2. Listen immediately.
3. If the voice identity is poor, fix reference audio before generating the rest.
4. Generate `sbm_tts_02` through `sbm_tts_14` only after chunk 01 is accepted.

Helper command for exporting chunk text files:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/export_tts_chunks.py
```

Production helper for generating exactly one chunk after the reference prompt transcript is human-verified:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/generate_gptsovits_chunk.py \
  --chunk-id sbm_tts_01_opening \
  --ref-audio exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_01_000009_5p40s.wav \
  --ref-text exports/smart-biomedicine-gpt-sovits/reference/<human-verified-exact-transcript>.txt
```

Guardrail: this helper refuses `draft` / `asr-draft` reference text filenames, requires a `3-10s` prompt WAV, and checks for RTX `4090` before synthesis.

Optional provisional review helper before formal generation:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/generate_gptsovits_provisional_chunk.py \
  --chunk-id sbm_tts_01_opening \
  --output-label sbm_tts_01_opening_ref04_repair1 \
  --ref-audio exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_04_000381_8p00s.wav \
  --ref-text exports/smart-biomedicine-gpt-sovits/runtime-smoke/ref_candidate_04_draft_prompt_text.txt
```

Guardrail: provisional files go to `exports/smart-biomedicine-gpt-sovits/chunks-provisional/` and are never accepted production chunks.

After the exact transcript is saved as
`exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_04_000381_8p00s.exact-transcript.txt`,
run the post-transcript helper:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/run_formal_chunk01_after_transcript.py
```

Guardrail: this helper refuses to proceed until the exact transcript file exists and does not look like draft / ASR / template text.

Current status helper:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/gptsovits_audio_gate_status.py
```

After human listening accepts a formal chunk, record the acceptance marker:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/mark_chunk_review_decision.py \
  --chunk-id sbm_tts_01_opening \
  --decision accepted \
  --ack-human-listened \
  --ack-no-missing-words \
  --ack-no-repeats \
  --ack-pronunciation-ok \
  --ack-no-artifacts \
  --ack-volume-ok \
  --ack-stitch-ok
```

After chunk `01` is accepted, generate exactly one next chunk:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/generate_next_chunk_after_acceptance.py \
  --chunk-id sbm_tts_02_markdown_format
```

Guardrail: the next-chunk helper refuses to run unless the previous formal WAV exists and has an accepted QA marker.

## Phase 3 - Per-Chunk Audio QA

Tracked QA sheet:

- `gpt-sovits-audio-qa-sheet-v1.md`

For each chunk:

- [ ] No missing words.
- [ ] No repeated words or repeated phrases.
- [ ] No swallowed final words.
- [ ] `A-S-R`, `L-L-M`, `HAY-ger`, `Jee-ang`, `Lang One`, `Reh-Med-Ee`, `Soh-Vits`, and `Pad-let` are pronounced acceptably where they appear.
- [ ] No sudden speed jump.
- [ ] No unwanted emotion drift.
- [ ] No metallic artifact, clipping, popping, or tail residue.
- [ ] Volume is consistent with nearby chunks.
- [ ] Ending leaves enough space for a natural stitch.
- [ ] Visual scroll position matches the spoken content.

Important additional QA not to skip:

- Run the term consistency gate before formal generation so TTS text keeps pronunciation-safe forms for acronyms and paper names.

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/term_consistency_gate.py
```

- Compare a few generated chunks against the Markdown visual timing. If audio is shorter than expected, increase screen hold time rather than adding filler narration.
- Confirm source-figure sections do not move before the figure-text explanation is complete.
- Confirm the final audio sounds like a report, not a continuous machine reading. Add screen pauses and section breaks if needed.
- Run a basic loudness report before final stitching. This is not ASR or TTS inference; it checks generated WAV levels so one chunk does not jump in volume.

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/audio_loudness_gate.py
```

## Phase 4 - Stitching

Only stitch accepted chunks.

Rules:

- [ ] Every formal chunk WAV exists under `exports/smart-biomedicine-gpt-sovits/chunks/`.
- [ ] Every chunk has a matching accepted marker under `exports/smart-biomedicine-gpt-sovits/qa/chunk-decisions/`.
- [ ] Add `0.35-0.7s` silence between chunks.
- [ ] Confirm chunk sample rate, channel count, and sample width are consistent before concat.
- [ ] Keep WAV master.
- [ ] Do not export compressed MP3/AAC until the stitched WAV passes review.
- [ ] After stitching, listen at every chunk boundary.
- [ ] Check loudness consistency after stitching.

Suggested output:

- `exports/smart-biomedicine-gpt-sovits/stitching/smart-biomedicine-final-report-narration-v1.wav`

Helper command:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/stitch_accepted_chunks.py --silence 0.5
```

## Phase 5 - Markdown Screen Recording

Visual source:

- `markdown-report-v1.md`

Preferred generated recording surface:

- `exports/smart-biomedicine-gpt-sovits/recording/markdown-report-recording.html`

Recording cue sheet:

- `video-recording-cue-sheet-v1.md`

Video QA sheet:

- `video-recording-qa-sheet-v1.md`

Readiness helper:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/video_recording_gate_status.py
```

Build the local browser recording HTML after Markdown edits:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_recording_html.py
```

Basic render proof currently lives at:

- `exports/smart-biomedicine-gpt-sovits/recording/qa/recording-html-top.png`

Rules:

- [ ] Record the Markdown page, not a slide deck.
- [ ] Do not scroll continuously.
- [ ] Hold each Mermaid diagram or source figure for `45-90s`.
- [ ] Use the upper end of visual holds if narration feels too fast.
- [ ] Target final video duration: `19-20` minutes.
- [ ] Confirm images render before recording.
- [ ] Confirm Mermaid diagrams render in the chosen viewer before recording.
- [ ] If Mermaid rendering is unavailable in the recorder, export diagrams as images before the final take.

Final video gate after export:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/final_video_gate_status.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/qa/final-video-gate-status.md`

Place the local video candidate under `exports/smart-biomedicine-gpt-sovits/video/` before running this gate.

Recommended screen rhythm:

- Title and thesis: slow opening.
- Definitions: hold table long enough for scanning.
- Mermaid diagrams: hold until narration finishes the figure-text explanation.
- Source figures: no fast scrolling; let the audience see the paper evidence.
- Risk matrix: hold and summarize, do not read every cell too quickly.

## Phase 6 - Fallback

Fallback rule:

- If GPT-SoVITS sounds too synthetic, unstable, or detached, record Jason's own voice for opening and closing.

Fallback structure:

- Jason real voice: `sbm_tts_01_opening`
- GPT-SoVITS: `sbm_tts_02` through `sbm_tts_13`
- Jason real voice: `sbm_tts_14_closing`

Reason:

- This makes the report identity clear and reduces the feeling of a fully synthetic reading.

Human fallback registration helper:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/register_human_fallback_chunk.py \
  --chunk-id sbm_tts_01_opening \
  --source-audio /path/to/jason-recorded-opening.wav \
  --ack-own-voice \
  --ack-recorded-for-this-report \
  --ack-content-matches-chunk \
  --ack-no-private-content
```

Use `--chunk-id sbm_tts_14_closing` for the closing fallback. The helper converts the source audio to the formal chunk WAV location and writes a fallback manifest under `exports/smart-biomedicine-gpt-sovits/qa/fallback-chunks/`. It does not mark the chunk accepted; run `mark_chunk_review_decision.py` after listening.

## Phase 7 - Submission

Required course gates:

- [ ] Upload final audiovisual report to Padlet before `2026-06-13 23:00`.
- [ ] Watch at least one classmate report by `2026-06-17`.
- [ ] Leave a comment or question and give a like by `2026-06-17`.
- [ ] Answer classmates' questions on Jason's report by `2026-06-20`.

End-to-end delivery gate:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/delivery_gate_status.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/qa/delivery-gate-status.md`

This gate reports the status of reference selection, exact transcripts, chunk generation, chunk acceptance, stitching, recording, YouTube proof, Padlet proof, peer engagement, and presenter-response proof.

Artifact provenance manifest:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/artifact_provenance_manifest.py
```

Output:

- `exports/smart-biomedicine-gpt-sovits/qa/provenance/artifact-provenance-manifest.md`
- `exports/smart-biomedicine-gpt-sovits/qa/provenance/artifact-provenance-manifest.csv`

Use this before final upload to confirm which report source, source voice, reference WAVs, review packets, recording HTML, and generated QA artifacts were used.

Padlet text:

```text
學號：513559004
姓名：林家聖
報告題目：從語音問診到醫師摘要：ASR + LLM 在智慧生醫臨床前問診中的應用與邊界
```

## Additional Controls Now In Force

These were not fully discussed earlier but matter for the final report.

### Academic-use disclosure

If the course expects a spoken presentation by the student, use a short disclosure if needed:

```text
Narration was produced from my own script using my own authorized voice with AI-assisted text-to-speech for recording support.
```

### Local privacy

Keep raw voice audio, generated chunks, and ASR drafts local. Do not commit generated audio to Git unless there is a deliberate release decision.

### Version freeze

Once chunk generation starts, freeze the TTS text in `gpt-sovits-narration-chunks-v1.md`. If wording changes are needed, create `v2` instead of silently editing the active production text.

### Preflight test before full generation

Before producing all `14` chunks:

- [ ] Run `tools/gptsovits_gpu_asr_preflight.py`.
- [ ] Build the reference transcript review packet.
- [ ] Build the reference quality manifest.
- [ ] Save the selected reference's exact transcript.
- [ ] Record the accepted reference marker.
- [ ] Generate chunk 01 only.
- [ ] Check voice identity.
- [ ] Check English acronym pronunciation.
- [ ] Check volume and artifact level.
- [ ] Confirm the GPU was used.
- [ ] Only then produce chunks 02-14.

### Failure stop rules

Stop production if:

- CUDA is unavailable.
- GPT-SoVITS or ASR falls back to CPU.
- The chosen reference transcript is not exact.
- The chosen reference has no accepted human-review marker.
- The first generated chunk has severe voice drift.
- The source voice candidate has obvious clipping or noisy artifacts.
- Any generated chunk changes technical terms enough to alter meaning.

### Screen-recording privacy

Before recording the Markdown report screen, close unrelated tabs and terminals, disable desktop notifications, and use the generated recording HTML rather than an editor with private file paths visible in sidebars.

### Submission resilience

Keep the final WAV master, final video file, YouTube URL, Padlet post proof, and peer-engagement proof as separate evidence. Do not wait until the final evening to upload; the Padlet gate is a submission gate, not the first rendering deadline.

Suggested local proof files after submission:

- `exports/smart-biomedicine-gpt-sovits/submission/youtube-url.txt`
- `exports/smart-biomedicine-gpt-sovits/submission/padlet-post-proof.md`
- `exports/smart-biomedicine-gpt-sovits/submission/peer-engagement-proof.md`
- `exports/smart-biomedicine-gpt-sovits/submission/presenter-response-proof.md`

Create proof templates before upload day:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/create_submission_proof_templates.py
```
