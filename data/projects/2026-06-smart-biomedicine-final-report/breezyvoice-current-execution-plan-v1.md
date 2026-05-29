# BreezyVoice Current Execution Plan v1

Purpose: operate the active Smart Biomedicine final-report narration route after Jason switched TTS from GPT-SoVITS to BreezyVoice 26.

Canonical report surface: `markdown-report-v1.md`
Base English script: `markdown-report-20min-script-v2.md`
Active BreezyVoice chunk source: `breezyvoice-narration-chunks-v1.md`
Prior chunk evidence: `gpt-sovits-narration-chunks-v1.md`
Runtime switch note: `breezyvoice-runtime-switch-v1.md`
RTX 5080 local plan: `breezyvoice-rtx5080-local-execution-plan-v1.md`
Generated artifact root: `exports/smart-biomedicine-breezyvoice/`

## First Principle

Scarce resource: credible, intelligible `20` minute English course-report delivery before the Padlet deadline, not model continuity.

The correct route is now:

1. keep BreezyVoice 26 as the active TTS engine,
2. run BreezyVoice only on the local RTX `5080` GPU,
3. keep generated audio under ignored `exports/smart-biomedicine-breezyvoice/`,
4. repair the English text for BreezyVoice-specific pronunciation and ASR stability,
5. generate one chunk at a time,
6. run `breeze-asr-25` CUDA transcript review after each chunk,
7. accept a chunk only after semantic sweep preserves the clinical-boundary meaning,
8. stitch only BreezyVoice accepted chunks.

## Current State

- BreezyVoice checkout: `/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/BreezyVoice`.
- BreezyVoice Python: `/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/breezyvoice/runtime/v1/venv/bin/python`.
- Breeze-ASR-25 Python: `/home/jnln3799/.cache/uroprevisit-asr-venv/bin/python`.
- Model: `MediaTek-Research/BreezyVoice-300M`.
- GPU proof: RTX `5080` visible through `nvidia-smi`; PyTorch CUDA is available; ONNX Runtime exposes `CUDAExecutionProvider`.
- Local runtime patches: official BreezyVoice ONNX sessions are patched locally to require `CUDAExecutionProvider`; CPU fallback is rejected.
- Smoke output: `exports/smart-biomedicine-breezyvoice/chunks/smoke-test.wav`.
- BreezyVoice chunk `01` first pass: generated, repaired, and superseded by the RTX `5080` accepted pass.
- BreezyVoice chunk `01`: accepted after RTX `5080` generation, Breeze-ASR-25 CUDA transcript gate, and manual semantic sweep.
- BreezyVoice chunk `01` accepted source is tracked in `breezyvoice-narration-chunks-v1.md`.
- Source-side preflight on `2026-05-28` found `missing_required_phrases: []` for the repaired chunk `01` text.
- The chunk `01` preflight now also rejects unstable source phrases such as `staff review`, `before it influences care`, `practical process`, `speech intake to clinician summary`, `transcribed`, `summarized`, and `the clinician makes the care decision` before RTX `5080` synthesis.
- The final authority sentence now uses `The doctor makes the medical decision.`
  because the RTX `5080` BreezyVoice pass repeatedly made `clinician` sound
  like `coalition` in final-authority sentences.
- Latest RTX `5080` repair after the first local BreezyVoice pass: replace
  `automatic priority scoring` with two short boundary sentences,
  `automatic scoring` and `automatic priority ranking`; replace
  `Artificial intelligence prepares a review screen` with
  `The system creates a review screen`.
- Latest RTX `5080` repair after later ASR passes: replace unstable
  `autonomous diagnosis` and `priority ranking` wording with direct boundary
  sentences: the system does not make a diagnosis, the workflow does not use
  automatic scoring, and it does not decide patient priority.
- BreezyVoice generation now records a `source_text_sha256` value, and semantic-sweep acceptance requires a matching generation-log entry for the WAV and current source text. This prevents accepting a stale chunk `01` WAV from an older failed script.
- The BreezyVoice status command now reports generation provenance separately from raw WAV presence. A WAV without a matching current-source generation log is `STALE` and must be regenerated before ASR or semantic acceptance.
- The chunk `01` ASR wrapper also refuses to run `breeze-asr-25` unless the WAV has matching current-source generation provenance.
- The chunk `01` ASR wrapper now also refuses dirty, stale, or unpushed checkouts by default, and the matching generation log must prove the same pushed commit before ASR evidence is recorded.
- The lower-level ASR report and JSONL log now record `git_commit`, `origin_main_commit`, and `source_text_sha256`, so a passing transcript gate can be tied back to the exact pushed source state.
- The chunk `01` route runner prints route identity before preflight: git commit, chunk id, source file, source text SHA-256, and source character count.
- Current blocking gate: add BreezyVoice-specific source coverage for chunks `02-14`, then continue one chunk at a time from `sbm_tts_02_markdown_format`.
- Current local execution check on `2026-05-28`: this checkout exposes `NVIDIA GeForce RTX 5080`; the route is now RTX `5080` CUDA-only. Smart Biomedicine BreezyVoice chunk `01` is accepted, so chunk `02` is the next production gate.

## Why GPT-SoVITS Acceptance Does Not Transfer

GPT-SoVITS chunks `01-06` are useful evidence for wording repairs and ASR gate design, but they are not final accepted audio after the model switch. BreezyVoice 26 has a different acoustic profile and currently produces different English error patterns.

## Chunk `01` Repair Targets

The latest BreezyVoice repair pass preserved some key phrases:

- `patient voice intake and clinical summaries`,
- `clinical review screen`,
- `Human staff keep final authority`.

It still failed semantic sweep because `breeze-asr-25` heard:

- `staff review` as `staff use`,
- `transcribed` as `described`,
- `summarized` as `summarizes`,
- `care` as `tear`,
- `practical process` as `critical process`.

Use the following repair strategy before another generation:

- replace `staff review` with `human staff check the draft`,
- replace `before it influences care` with `before any care decision`,
- replace `practical process` with `step by step process`,
- avoid compressed title phrases such as `speech intake to clinician summary`,
- keep clinical-boundary phrases in standalone sentences.

## Immediate Next Commands

Before rendering, run the full chunk `01` route preflight on the RTX `5080` machine:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/breezyvoice_chunk01_preflight.py \
  --write-report
```

If moving the source to a different machine, verify only the repaired source text without relaxing the RTX `5080` production gate:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/breezyvoice_chunk01_preflight.py \
  --source-only
```

Print the exact guarded RTX `5080` chunk `01` route command from the current checkout:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/print_breezyvoice_chunk01_handoff.py
```

Print the source-only preflight, exact handoff command, and current gate table together:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/breezyvoice_chunk01_handoff_status.py
```

That wrapper also prints the post-ASR semantic-review command, but the command remains hold-only until the chunk `01` ASR report exists and passes.

To run the complete chunk `01` machine route in order, use:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/run_breezyvoice_chunk01_route.py \
  --write-preflight-report \
  --overwrite
```

This route runs preflight, regenerates chunk `01`, runs the `breeze-asr-25` CUDA transcript gate, and then stops. It does not write the semantic-sweep accepted marker.
It refuses tracked local modifications by default, so production evidence is
tied to a committed checkout. Ignored local outputs such as export artifacts do
not block the route.
It also requires `HEAD` to match the local `origin/main` ref by default, so the
production attempt is tied to a pushed commit.
The route refreshes `origin/main` with `git fetch origin main` before that
comparison, so a stale remote-tracking ref does not clear production.
Before the RTX `5080` preflight, it also runs
`check_breezyvoice_chunk01_gate_rules.py`; if the repaired source phrases or
critical-phrase detector regress, generation is not attempted.
After a passing ASR gate, the route prints the same post-ASR semantic-review command and checklist, so the RTX `5080` terminal output carries the next manual gate.
For a stricter handoff, add `--expected-git-commit <commit>` and `--expected-source-sha256 <hash>` so the RTX `5080` run refuses stale checkout or stale source text before synthesis.

Regenerate only BreezyVoice chunk `01` from the repaired source after preflight passes. Keep the command GPU-only; the helper refuses CPU and non-RTX-5080 fallback before it touches runtime paths:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/generate_breezyvoice_chunk.py \
  --chunk-id sbm_tts_01_opening \
  --overwrite
```

The helper uses the repaired source text from `breezyvoice-narration-chunks-v1.md`, section `sbm_tts_01_opening`, and writes generation evidence to `exports/smart-biomedicine-breezyvoice/qa/experiment-logs/breezyvoice-chunk-generations.jsonl`.
It also refuses tracked local modifications and refreshes `origin/main` before
checking that `HEAD` matches it, so direct generator calls preserve the same
pushed-commit provenance boundary as the full route.

Then run `breeze-asr-25` CUDA review against the BreezyVoice artifact root:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/gate_breezyvoice_chunk01.py
```

This wrapper refreshes `origin/main`, requires `HEAD == origin/main`, checks for
tracked local modifications, verifies that the WAV was generated from the
current source text, and requires the generation log to name the same pushed
commit before it invokes `breeze-asr-25`.

The ASR wrapper prints the exact manual semantic-review command after a passing gate. To check the command and current ASR readiness separately, run:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/print_breezyvoice_chunk01_semantic_command.py
```

The semantic command helper also lists the chunk `01` required semantic
phrases and reports whether any required phrase is missing from the ASR
transcript. Treat any missing required phrase as `HOLD`, even if the ratio
looks acceptable.

If the ASR gate passes, manually read `exports/smart-biomedicine-breezyvoice/qa/chunk-asr/sbm_tts_01_opening.asr-qa.md`. Confirm clinical boundary, human staff check, final authority, and no-autonomous-medical-action meaning. Then write the semantic-sweep marker and the accepted marker:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/mark_breezyvoice_chunk01_semantic_sweep.py \
  --ack-clinical-boundary \
  --ack-human-staff-check \
  --ack-final-authority \
  --ack-no-autonomous-medical-action \
  --ack-no-meaning-changing-medical-error
```

Do not continue to chunk `02` while chunk `01` is not accepted.

After chunk `01` has both an accepted marker and a semantic-sweep marker, generate later chunks through the guarded next-chunk helper:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/generate_next_breezyvoice_chunk_after_acceptance.py \
  --chunk-id sbm_tts_02_markdown_format
```

The helper refuses to generate a chunk if the previous BreezyVoice WAV, accepted marker, or semantic-sweep marker is missing.

For later chunks, use the generic semantic-sweep marker after a passing ASR report:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/mark_breezyvoice_chunk_semantic_sweep.py \
  --chunk-id <chunk-id> \
  --ack-clinical-boundary \
  --ack-staff-review \
  --ack-final-authority \
  --ack-no-autonomous-medical-action \
  --ack-no-meaning-changing-medical-error
```

Check the current BreezyVoice gate state at any time:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/breezyvoice_audio_gate_status.py
```

When chunk `01` is the next gate, this status command prints the exact
commit-pinned and source-hash-pinned RTX `5080` handoff command. Use that
printed command for the next production attempt so the generated WAV is tied to
the current repaired English source.

The chunk `01` preflight and ASR gate now require the repaired wording for
staff checking, correction, rejection, the review screen, final authority, and
the final medical decision. A pass therefore has to preserve the current
clinical-boundary wording before the manual semantic sweep can accept it.

Run the no-GPU local self-check before the RTX `5080` production route:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/check_breezyvoice_chunk01_gate_rules.py
```

Audit the full BreezyVoice delivery objective, including Markdown screen, chunk `01` gate, `14/14` audio acceptance, stitching, recording, YouTube, Padlet, and proof:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/breezyvoice_objective_audit.py
```

Refresh the BreezyVoice provenance manifest before final upload and whenever major local artifacts are added:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/artifact_provenance_manifest.py \
  --export-root exports/smart-biomedicine-breezyvoice \
  --engine-label BreezyVoice-26
```

Prepare local proof templates for the BreezyVoice route before upload day:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/create_submission_proof_templates.py \
  --export-root exports/smart-biomedicine-breezyvoice
```

After stitching and before recording, check the BreezyVoice recording gate:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/build_recording_html.py \
  --export-root exports/smart-biomedicine-breezyvoice
```

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/video_recording_gate_status.py \
  --export-root exports/smart-biomedicine-breezyvoice \
  --engine-label BreezyVoice-26
```

After exporting the video candidate, check the BreezyVoice final-video gate:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/final_video_gate_status.py \
  --export-root exports/smart-biomedicine-breezyvoice
```

After `14/14` chunks have WAVs, passing ASR reports, semantic-sweep markers, and accepted markers, stitch only the accepted BreezyVoice chunks:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/stitch_accepted_chunks.py \
  --chunks-dir exports/smart-biomedicine-breezyvoice/chunks \
  --decisions-dir exports/smart-biomedicine-breezyvoice/qa/chunk-decisions \
  --semantic-sweep-dir exports/smart-biomedicine-breezyvoice/qa/semantic-sweeps \
  --require-semantic-sweep \
  --output exports/smart-biomedicine-breezyvoice/stitching/smart-biomedicine-final-report-narration-v1.wav \
  --silence 0.5
```

## Stop Conditions

- RTX `5080` is not visible.
- PyTorch CUDA is unavailable.
- ONNX Runtime lacks `CUDAExecutionProvider`.
- BreezyVoice or ASR attempts CPU fallback.
- ASR transcript changes a clinical-boundary phrase.
- Chunk `01` remains unstable after several small repairs; if this happens, use real-voice fallback for opening and continue BreezyVoice only after the opening identity is stable.
