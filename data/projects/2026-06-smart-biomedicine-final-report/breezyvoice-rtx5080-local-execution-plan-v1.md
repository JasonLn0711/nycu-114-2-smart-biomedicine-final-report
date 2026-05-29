# BreezyVoice RTX 5080 Local Execution Plan v1

Purpose: make the Smart Biomedicine final-report narration route executable on
the current workstation with RTX 5080, while preserving the real quality gates:
CUDA-only TTS, CUDA-only Breeze-ASR-25 transcript gate, manual semantic sweep,
and no chunk `02` work before chunk `01` is accepted.

## First Principle

Scarce resource: credible clinical-boundary meaning in the final spoken report,
not strict continuity with the earlier RTX 4090 machine.

Decision: the production GPU is now the local RTX `5080`. CPU fallback remains
out of scope. The accepted evidence must prove CUDA execution, current source
provenance, transcript preservation, and semantic-boundary preservation.

## Local Runtime Evidence

- GPU: `NVIDIA GeForce RTX 5080`, index `0`, driver `595.71.05`.
- BreezyVoice checkout:
  `/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/BreezyVoice`.
- BreezyVoice Python:
  `/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/breezyvoice/runtime/v1/venv/bin/python`.
- BreezyVoice runtime proof already observed in that venv:
  PyTorch CUDA is available on `NVIDIA GeForce RTX 5080`; ONNX Runtime exposes
  `CUDAExecutionProvider`.
- Breeze-ASR-25 model:
  `/home/jnln3799/.cache/huggingface/hub/models--SoybeanMilk--faster-whisper-Breeze-ASR-25/snapshots/85be11de5f67aaa6a92e931622f1c2b55cc1dd3a`.
- Breeze-ASR-25 Python:
  `/home/jnln3799/.cache/uroprevisit-asr-venv/bin/python`.
- ASR runtime proof already observed: the model loads with
  `WhisperModel(..., device='cuda', compute_type='float16')`.
- Prompt audio:
  `/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/breezyvoice/prompts/v1/jason_reference.wav`.

## Concrete Chunk 01 Route

1. Confirm the repaired chunk `01` source still passes the no-GPU phrase gate:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/check_breezyvoice_chunk01_gate_rules.py
```

2. Run the RTX `5080` production preflight:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/breezyvoice_chunk01_preflight.py --write-report
```

3. Print the current commit-pinned command:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/print_breezyvoice_chunk01_handoff.py
```

4. Regenerate and ASR-gate chunk `01` through the single route wrapper:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/run_breezyvoice_chunk01_route.py \
  --write-preflight-report \
  --overwrite
```

The route must stop after ASR and print the semantic-sweep command. It must not
write an accepted marker automatically.

5. Read the ASR report:

```bash
less exports/smart-biomedicine-breezyvoice/qa/chunk-asr/sbm_tts_01_opening.asr-qa.md
```

6. If the transcript preserves the clinical boundary, staff check, final
authority, and no-autonomous-medical-action meaning, write the semantic sweep:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/mark_breezyvoice_chunk01_semantic_sweep.py \
  --ack-clinical-boundary \
  --ack-human-staff-check \
  --ack-final-authority \
  --ack-no-autonomous-medical-action \
  --ack-no-meaning-changing-medical-error
```

7. Confirm chunk `01` is accepted before chunk `02`:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/breezyvoice_audio_gate_status.py
```

## After Chunk 01 Acceptance

Use the guarded next-chunk helper for chunks `02-14`:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/generate_next_breezyvoice_chunk_after_acceptance.py \
  --chunk-id sbm_tts_02_markdown_format
```

For each chunk:

1. generate on RTX `5080`;
2. run Breeze-ASR-25 CUDA transcript gate;
3. manually semantic-sweep clinical boundary, staff review, final authority,
   and no autonomous medical action;
4. accept only after the semantic sweep marker exists.

## Downstream Route

After `14/14` chunks are accepted and semantic-swept:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/stitch_accepted_chunks.py \
  --chunks-dir exports/smart-biomedicine-breezyvoice/chunks \
  --decisions-dir exports/smart-biomedicine-breezyvoice/qa/chunk-decisions \
  --semantic-sweep-dir exports/smart-biomedicine-breezyvoice/qa/semantic-sweeps \
  --require-semantic-sweep \
  --output exports/smart-biomedicine-breezyvoice/stitching/smart-biomedicine-final-report-narration-v1.wav \
  --silence 0.5
```

Then run loudness / spot-check QA, build the Markdown recording surface, record
the scrolling Markdown video, export the final video, run final-video QA, upload
to YouTube, post to Padlet, and preserve YouTube / Padlet proof.

## Stop Conditions

- RTX `5080` is not visible.
- BreezyVoice or Breeze-ASR-25 falls back to CPU.
- PyTorch CUDA is unavailable.
- ONNX Runtime lacks `CUDAExecutionProvider`.
- ASR transcript changes clinical-boundary meaning.
- Semantic sweep is missing.
- Chunk `02` is attempted before chunk `01` is accepted.
