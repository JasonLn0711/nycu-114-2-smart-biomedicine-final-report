# F5-TTS v2 Generation Log - 2026-05-28

Purpose: record the RTX 5080-only F5-TTS v2 narration run for the Smart
Biomedicine final report.

## Result

- Status: generated.
- Model route: official GitHub F5-TTS repository, `F5TTS_v1_Base`.
- F5-TTS Git commit: `2ae2c9b`.
- Source text: `breezyvoice-narration-chunks-v1.md`.
- Source mode: reuse v1 narration chunk text.
- Output root: `exports/smart-biomedicine-f5-tts/`.
- Master WAV:
  `exports/smart-biomedicine-f5-tts/stitching/smart-biomedicine-final-report-f5tts-v2.wav`.
- Chunk WAVs:
  `exports/smart-biomedicine-f5-tts/chunks/sbm_tts_01_opening.wav`
  through
  `exports/smart-biomedicine-f5-tts/chunks/sbm_tts_14_closing.wav`.

## GPU Gate

- Required device: RTX 5080 GPU only.
- Observed CUDA device: `NVIDIA GeForce RTX 5080`.
- CUDA capability: `12.0`.
- PyTorch: `2.11.0+cu128`.
- CUDA runtime reported by PyTorch: `12.8`.
- CPU fallback: refused by script before model load.

## Artifact Check

- Chunk count: `14`.
- Chunk format: `24000 Hz`, mono WAV.
- Master format: `pcm_s16le`, `24000 Hz`, mono.
- Master duration: `733.566667` seconds.
- Master size: `35211278` bytes.
- Reference audio:
  `exports/smart-biomedicine-f5-tts/reference/sbm_tts_01_opening_ref_14s.wav`.
- Generation manifest:
  `exports/smart-biomedicine-f5-tts/qa/f5tts-v2-generation-manifest.json`.

## Re-run Command

```bash
HF_HOME=.local/huggingface XDG_CACHE_HOME=.local/cache \
  .local/tts-tools/f5tts-venv/bin/python \
  data/projects/2026-06-smart-biomedicine-final-report/tools/generate_f5tts_v2_gpu.py
```

The script verifies CUDA availability and the active device name before
loading F5-TTS. If the active CUDA device is not `NVIDIA GeForce RTX 5080`, it
exits without generating audio.
