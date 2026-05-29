# BreezyVoice 26 Runtime Switch v1

Purpose: switch the Smart Biomedicine final-report TTS production path from GPT-SoVITS to BreezyVoice 26 while preserving the RTX GPU-only rule.

## Decision

- Active TTS engine: `BreezyVoice 26` / `MediaTek-Research/BreezyVoice-300M`.
- Runtime checkout: `/home/jnclaw/every_on_git_jnclaw/BreezyVoice`.
- Generated artifact root: `exports/smart-biomedicine-breezyvoice/`.
- Reference voice source: Jason's accepted prompt reference `prompt_ref_candidate_04_000381_8p00s`.
- Hard rule: use the local RTX `5080` GPU only. Do not accept CPU fallback for TTS generation or ASR review.
- Review rule: every BreezyVoice chunk must pass `breeze-asr-25` CUDA transcript review and semantic sweep. GPT-SoVITS accepted markers do not transfer to BreezyVoice output.

## Runtime Setup Completed

- Cloned official BreezyVoice repo to `/home/jnclaw/every_on_git_jnclaw/BreezyVoice`.
- Created `.venv` with Python `3.10.20` using `uv`.
- Installed inference dependencies with CUDA PyTorch `2.3.1+cu118` and `torchaudio==2.3.1+cu118`.
- Excluded `deepspeed` from local inference install because it attempted CUDA op compilation and the machine does not expose `CUDA_HOME`; inference does not require this training path.
- Removed CPU `onnxruntime` and kept `onnxruntime-gpu`.
- Pinned `numpy<2`, `protobuf==4.25.0`, `packaging==24.2`, and `ruamel.yaml<0.18` for runtime compatibility.
- Added local `libnvrtc.so` symlink inside the BreezyVoice venv so cuDNN can resolve `libnvrtc.so`.

## GPU-Only Local Patches

The official BreezyVoice checkout needed local GPU-only enforcement:

- `cosyvoice/cli/frontend.py`: changed both `campplus_session` and `speech_tokenizer_session` to require `CUDAExecutionProvider`.
- `single_inference.py`: added a runtime guard that rejects missing `CUDAExecutionProvider` and wraps ONNX `InferenceSession` calls so unspecified providers become `["CUDAExecutionProvider"]`.

These patches are local runtime patches in the BreezyVoice checkout, not planning-repo source files.

## Verified Evidence

- RTX GPU detected for the revised route: `NVIDIA GeForce RTX 5080`, index `0`, `16303 MiB`, driver `595.71.05`.
- Active BreezyVoice checkout: `/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/BreezyVoice`.
- Active BreezyVoice Python: `/home/jnln3799/every_on_git_ubuntu/cybersec-2026-ai-samd-talk/.local/breezyvoice/runtime/v1/venv/bin/python`.
- Active Breeze-ASR-25 Python: `/home/jnln3799/.cache/uroprevisit-asr-venv/bin/python`.
- PyTorch CUDA check passed: `torch.cuda.is_available() == True`.
- ONNX Runtime provider check passed: `CUDAExecutionProvider` available.
- BreezyVoice model downloaded to Hugging Face cache:
  `/home/jnclaw/.cache/huggingface/hub/models--MediaTek-Research--BreezyVoice-300M/snapshots/e33b502e0ac21c16b0ee0d00df66ac3fa737393d`.
- Smoke render succeeded:
  `exports/smart-biomedicine-breezyvoice/chunks/smoke-test.wav`.
- Formal BreezyVoice chunk `01` first pass produced:
  `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_01_opening.wav`,
  duration about `71.26s`.
- Formal BreezyVoice chunk `01` repair pass produced:
  `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_01_opening.repair01.wav`,
  duration about `73.35s`.

## Current Quality Gate

Chunk `01` is generated but not accepted.

`breeze-asr-25` CUDA review for the first direct GPT-SoVITS-style text found meaning-changing English errors:

- `speech intake to clinician summary` became `speech index determination summary`.
- `workflow` became `role`.
- `This works only...` became `This is worse...`.
- `workflow` / `staff keep final authority` degraded near the final boundary sentence.

Repair pass `01` improved several phrases and preserved:

- `patient voice intake and clinical summaries`,
- `clinical review screen`,
- `Human staff keep final authority`.

But it still needs repair before acceptance because ASR reported:

- `staff review` as `staff use`,
- `transcribed` as `described`,
- `summarized` as `summarizes`,
- `care` as `tear`,
- `practical process` as `critical process`.

## Important Finding

BreezyVoice 26 is usable locally on RTX GPU, but this model is primarily adapted for Taiwanese Mandarin and code-switching. For this all-English report, it needs a BreezyVoice-specific speaking script with shorter, simpler English phrases and repeated local context around clinical boundary terms.

The GPT-SoVITS chunk text should not be treated as final BreezyVoice source text.

## Next Step

1. Create a BreezyVoice-specific chunk `01` text that avoids unstable phrases:
   - replace `staff review` with `human staff check the draft`,
   - replace `influences care` with `before any care decision`,
   - replace `practical process` with `step by step process`,
   - avoid compressed title phrases such as `speech intake to clinician summary`.
2. Regenerate only BreezyVoice chunk `01`.
3. Rerun `breeze-asr-25` CUDA transcript review.
4. Accept chunk `01` only after both transcript ratio and semantic sweep pass.
5. Continue to chunk `02` only after BreezyVoice chunk `01` has its own accepted marker.

## 2026-05-28 Local Execution Check

- Repaired BreezyVoice chunk `01` source now lives in `breezyvoice-narration-chunks-v1.md`.
- The ASR decision tooling now supports BreezyVoice-specific source, chunk, QA, repair, log, and decision directories while preserving the legacy GPT-SoVITS defaults.
- A dedicated generation helper now exists at `tools/generate_breezyvoice_chunk.py`; it extracts chunk text from the BreezyVoice source file, checks for RTX `5080`, checks PyTorch CUDA and ONNX `CUDAExecutionProvider`, and writes generation evidence under `exports/smart-biomedicine-breezyvoice/qa/experiment-logs/`.
- A dedicated chunk `01` gate wrapper now exists at `tools/gate_breezyvoice_chunk01.py`; it routes the `breeze-asr-25` transcript gate to BreezyVoice QA directories without writing an accepted marker.
- A generic semantic-sweep marker now exists at `tools/mark_breezyvoice_chunk_semantic_sweep.py` for all BreezyVoice chunks. The chunk `01` wrapper at `tools/mark_breezyvoice_chunk01_semantic_sweep.py` preserves the stricter opening-specific phrase checks. Both paths require a passing ASR report, explicit manual acknowledgements, and a semantic-sweep marker before writing a BreezyVoice accepted marker.
- A BreezyVoice status command now exists at `tools/breezyvoice_audio_gate_status.py`; it reports source, WAV, ASR, semantic-sweep, and accepted-marker state for all `14` chunks.
- A BreezyVoice objective audit now exists at `tools/breezyvoice_objective_audit.py`; it maps the full route from Markdown report screen through RTX `5080` chunk `01`, `14/14` acceptance, stitching, recording, YouTube, Padlet, and proof.
- The BreezyVoice objective audit treats audio loudness and final-video QA as passing only when their reports contain passing status evidence; placeholder reports do not satisfy those gates.
- `tools/artifact_provenance_manifest.py` now accepts `--export-root` and `--engine-label`, so the final upload package can hash BreezyVoice route files and local artifacts under `exports/smart-biomedicine-breezyvoice/`.
- `tools/create_submission_proof_templates.py` now accepts `--export-root`, so the YouTube, Padlet, peer-engagement, and presenter-response proof templates can be created under `exports/smart-biomedicine-breezyvoice/`.
- `tools/video_recording_gate_status.py` and `tools/final_video_gate_status.py` now accept `--export-root`, so recording and final-video readiness can be checked against the BreezyVoice artifact root instead of the legacy GPT-SoVITS root.
- `tools/build_recording_html.py` now accepts `--export-root`, so the Markdown scrolling recording surface can be generated directly under `exports/smart-biomedicine-breezyvoice/recording/`.
- `tools/stitch_accepted_chunks.py` now accepts BreezyVoice chunk, decision, and semantic-sweep directories. For the BreezyVoice route, stitching must use `--require-semantic-sweep`.
- A chunk `01` route preflight now exists at `tools/breezyvoice_chunk01_preflight.py`; it checks the repaired source phrases, RTX `5080`, BreezyVoice runtime paths, prompt audio, ASR model/runtime paths, PyTorch CUDA, and ONNX `CUDAExecutionProvider` before synthesis.
- The chunk `01` preflight also rejects known unstable source phrases from the failed BreezyVoice passes before synthesis, so the RTX `5080` route does not render a regressed opening script.
- The same preflight supports `--source-only` for source review. This mode proves the repaired text checks while keeping the default production route strict about RTX `5080`, runtime paths, PyTorch CUDA, and ONNX CUDA.
- BreezyVoice generation records `source_text_sha256` in the generation log, and semantic-sweep acceptance requires the WAV to match a generation-log entry for the current source hash. This keeps older failed chunk `01` audio from being accepted after a script repair.
- `tools/breezyvoice_audio_gate_status.py` now reports generation provenance as its own gate. A raw WAV without a current-source generation-log match is shown as `STALE` and does not count as a provenanced generated chunk.
- `tools/gate_breezyvoice_chunk01.py` now performs the same current-source generation provenance check before invoking `breeze-asr-25`, so stale chunk `01` audio fails before ASR work starts.
- `tools/run_breezyvoice_chunk01_route.py` prints route identity before preflight, including git commit and chunk `01` source SHA-256, so RTX `5080` generation evidence can be tied back to the repaired source state.
- `tools/run_breezyvoice_chunk01_route.py` also supports `--expected-git-commit` and `--expected-source-sha256` to refuse stale RTX `5080` handoff state before synthesis.
- `tools/run_breezyvoice_chunk01_route.py` and `tools/gate_breezyvoice_chunk01.py` print the post-ASR semantic-review command after a passing ASR gate, then stop before writing acceptance.
- `tools/print_breezyvoice_chunk01_handoff.py` prints the exact guarded RTX `5080` route command from the current checkout, including the expected git commit and chunk `01` source SHA-256.
- `tools/print_breezyvoice_chunk01_semantic_command.py` prints the exact post-ASR semantic-review command and reports whether the chunk `01` ASR report is ready for manual acceptance.
- `tools/breezyvoice_chunk01_handoff_status.py` prints source-only preflight, the guarded RTX `5080` command, the post-ASR semantic-review command, and the current BreezyVoice gate table in one pass.
- `tools/gate_breezyvoice_chunk01.py` now refreshes `origin/main`, refuses tracked local modifications, requires `HEAD == origin/main`, and requires the matching generation log to name the same pushed commit before invoking `breeze-asr-25`.
- `tools/chunk_asr_qa.py` now records `git_commit`, `origin_main_commit`, and `source_text_sha256` in the ASR report and JSONL log, and refuses dirty or unpushed checkouts by default for production transcript evidence.
- The final chunk `01` authority sentence now uses `medical decision` instead of repeating `care decision`, reducing exposure to the known `care` to `tear` ASR failure while preserving the required `before any care decision` boundary sentence.
- A chunk `01` route runner now exists at `tools/run_breezyvoice_chunk01_route.py`; it runs preflight, regeneration, and ASR gating in order, then stops before the manual semantic-sweep accepted marker.
- A guarded next-chunk helper now exists at `tools/generate_next_breezyvoice_chunk_after_acceptance.py`; it refuses chunks `02-14` unless the previous BreezyVoice WAV, accepted marker, and semantic-sweep marker exist.
- Current local GPU evidence from this checkout: `NVIDIA GeForce RTX 5080`, index `0`, driver `595.71.05`.
- Production decision: synthesize Smart Biomedicine BreezyVoice audio on this RTX `5080` path. The active route remains CUDA-only and rejects CPU fallback.
- Current source-side preflight result in this checkout: chunk `01` repaired text has `missing_required_phrases: []`; production generation is now planned on the RTX `5080` runtime, and chunk `02` remains blocked until chunk `01` has WAV, ASR pass, semantic sweep, and accepted marker.
