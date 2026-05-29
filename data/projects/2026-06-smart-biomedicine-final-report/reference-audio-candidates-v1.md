# Reference Audio Candidates v1

Source voice: `/home/jnclaw/Downloads/260528_0839_record.mp3`
Use case: Jason's own-voice reference material for GPT-SoVITS narration
Selection method: machine-selected candidate windows using basic audio features, then draft-transcribed with `breeze-asr-25` on RTX 4090 CUDA
Status: `12s` review candidates and GPT-SoVITS prompt-ready `3-10s` candidates prepared; local reference-transcript review packet, reference listening workbook, reference quality manifest, reference visual QC, and fallback adaptation review set prepared; human listening, exact transcript confirmation, and accepted reference marker still required before production prompt use

## Source Audio Facts

- File: `/home/jnclaw/Downloads/260528_0839_record.mp3`
- Duration: about `11:42.86`
- Format: MP3
- Sample rate: `16 kHz`
- Channels: mono
- Bitrate: about `24 kb/s`
- Whole-file measured mean volume: about `-15.8 dB`
- Whole-file max volume: `0.0 dB`
- Important quality warning: the source reaches digital full scale. Candidate references must be listened to for clipping, harsh consonants, and tail artifacts before use.

## GPU / ASR Gate

- Required GPU: RTX 4090, `CUDA_VISIBLE_DEVICES=0`.
- CPU fallback is not allowed for ASR or GPT-SoVITS production.
- ASR model: `SoybeanMilk/faster-whisper-Breeze-ASR-25`
- Local cached model path:
  `/home/jnclaw/.cache/huggingface/hub/models--SoybeanMilk--faster-whisper-Breeze-ASR-25/snapshots/85be11de5f67aaa6a92e931622f1c2b55cc1dd3a`
- Working ASR runtime:
  `/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/bin/python`
- Required CUDA library path:

```bash
export CUDA_VISIBLE_DEVICES=0
export LD_LIBRARY_PATH=/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/lib/python3.12/site-packages/nvidia/cublas/lib:/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/lib/python3.12/site-packages/nvidia/cudnn/lib:/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib
```

Evidence from local run: model load and transcription succeeded with `device='cuda'`, `compute_type='float16'` after the CUDA library path was set. Without this path, the run failed with `RuntimeError: Library libcublas.so.12 is not found or cannot be loaded`.

## Candidate Files

Generated local WAV files live under:

`exports/smart-biomedicine-gpt-sovits/reference/`

These files are intentionally ignored by Git. This manifest is the tracked record.

| Candidate | Source window | WAV path | RMS | Peak | Silence ratio | Near-clip ratio | Use recommendation |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| `ref_candidate_01` | `00:09-00:21` | `exports/smart-biomedicine-gpt-sovits/reference/ref_candidate_01_000009_12s.wav` | `5380.5` | `32768` | `0.310` | `0.0039` | Best first prompt candidate: formal greeting, stable report-style opening. |
| `ref_candidate_02` | `00:36-00:48` | `exports/smart-biomedicine-gpt-sovits/reference/ref_candidate_02_000036_12s.wav` | `5759.8` | `32768` | `0.310` | `0.0055` | Useful mixed Mandarin-English style sample; contains `Well`. |
| `ref_candidate_03` | `01:12-01:24` | `exports/smart-biomedicine-gpt-sovits/reference/ref_candidate_03_000072_12s.wav` | `6525.6` | `32768` | `0.328` | `0.0076` | Useful clinical/hospital content sample; listen for clipping. |
| `ref_candidate_04` | `06:21-06:33` | `exports/smart-biomedicine-gpt-sovits/reference/ref_candidate_04_000381_12s.wav` | `6034.3` | `32768` | `0.338` | `0.0054` | Natural rhetorical delivery; useful if formal style needs more energy. |
| `ref_candidate_05` | `08:00-08:12` | `exports/smart-biomedicine-gpt-sovits/reference/ref_candidate_05_000480_12s.wav` | `7537.4` | `32768` | `0.432` | `0.0156` | Backup only; higher silence and near-clipping risk. |

## Prompt-Ready Reference Files

GPT-SoVITS rejected the original `12s` reference during runtime smoke testing because prompt audio must be within the accepted `3-10s` range. Keep the `12s` files for listening review, but use one of the following prompt-ready files for actual GPT-SoVITS prompt-mode synthesis after human transcript verification.

| Candidate | Source window | WAV path | Duration | Draft transcript |
| --- | ---: | --- | ---: | --- |
| `prompt_ref_candidate_01` | `00:09.0-00:14.4` | `exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_01_000009_5p40s.wav` | `5.40s` | `各位長官各位先進各位醫療與資訊領域的夥伴大家好` |
| `prompt_ref_candidate_02` | `00:36.0-00:44.0` | `exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_02_000036_8p00s.wav` | `8.00s` | `你可能一定想說好自然那可能有時候要講防火牆弱密碼或者是不要亂點連結well` |
| `prompt_ref_candidate_03` | `01:12.0-01:20.0` | `exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_03_000072_8p00s.wav` | `8.00s` | `對醫院的醫療系統來說真的可怕的其實並不是檔案被加密而是病人正在等待檢查` |
| `prompt_ref_candidate_04` | `06:21.0-06:29.0` | `exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_04_000381_8p00s.wav` | `8.00s` | `有人跟你說這只是資訊式的問題而你可以很溫柔的回答他那醫院明天的 CT` |
| `prompt_ref_candidate_05` | `08:00.0-08:08.0` | `exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_05_000480_8p00s.wav` | `8.00s` | `這種很大的公寓每個人都說自己的家門有鎖可是地下室逃生門` |

Runtime smoke result:

- GPT-SoVITS CUDA runtime succeeded with `prompt_ref_candidate_01_000009_5p40s.wav` and the draft prompt text.
- Output: `exports/smart-biomedicine-gpt-sovits/runtime-smoke/output/output.wav`
- Output facts: `pcm_s16le`, `32000 Hz`, mono, about `5.86s`
- Production caveat: this proves runtime readiness only. It does not replace human listening or exact transcript approval.

## ASR Draft Transcripts

These transcripts were generated with `breeze-asr-25` on CUDA. They are draft transcripts, not exact prompt transcripts. Human verification is required before using a segment as GPT-SoVITS reference text.

### ref_candidate_01

Draft:

```text
各位長官各位先進各位醫療與資訊領域的夥伴大家好今天很榮幸有機會跟大家分享一個聽起來很有點硬但是實際上
```

Human exact transcript: `[ ] pending`

### ref_candidate_02

Draft:

```text
你可能一定想說好資安那可能有時候要講防火牆弱密碼或者是不要亂點連結Well 這很合理但資安簡報通常還有另外一個特色
```

Human exact transcript: `[ ] pending`

### ref_candidate_03

Draft:

```text
對醫院的醫療系統來說真的可怕的其實並不是檔案被加密而是病人正在等待檢查但是系統卻不能用然後醫生正在
```

Human exact transcript: `[ ] pending`

### ref_candidate_04

Draft:

```text
有人跟你說這只是資訊式的問題你可以很溫柔的回答他那醫院明天的 CT 不能看你要不要去急診你要不要去跟急診醫師說
```

Human exact transcript: `[ ] pending`

### ref_candidate_05

Draft:

```text
這種很大的公寓每個人都說自己的家門有鎖可是地下室 保存門 物流入口管理人士冷氣維修通道
```

Human exact transcript: `[ ] pending`

## Candidate Decision Gate

Before GPT-SoVITS generation:

- [ ] Listen to each candidate on headphones.
- [ ] Reject any candidate with obvious clipping, harsh distortion, laughter, long pause, unstable mic distance, or transcript mismatch.
- [ ] Select one prompt-ready `3-10s` WAV, not the `12s` review WAV.
- [ ] Write exact transcript for the selected prompt-ready reference.
- [ ] Prefer `prompt_ref_candidate_01` for the first zero-shot prompt test unless listening reveals quality problems.
- [ ] Keep `prompt_ref_candidate_02` or `prompt_ref_candidate_03` as backup if English/code-switching style improves GPT-SoVITS output.
- [ ] Use `prompt_ref_candidate_05` only if the first four are rejected.

Local reference transcript review packet:

- `exports/smart-biomedicine-gpt-sovits/review-packet/reference-transcript-review/index.html`
- `exports/smart-biomedicine-gpt-sovits/review-packet/reference-listening-workbook/index.html`
- Template transcripts:
  - `prompt_ref_candidate_01_000009_5p40s.exact-transcript.TEMPLATE.txt`
  - `prompt_ref_candidate_02_000036_8p00s.exact-transcript.TEMPLATE.txt`
  - `prompt_ref_candidate_03_000072_8p00s.exact-transcript.TEMPLATE.txt`
  - `prompt_ref_candidate_04_000381_8p00s.exact-transcript.TEMPLATE.txt`
  - `prompt_ref_candidate_05_000480_8p00s.exact-transcript.TEMPLATE.txt`

Acceptance marker command for the current first-choice candidate after human listening:

Exact transcript helper:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/create_exact_transcript.py \
  --candidate prompt_ref_candidate_04_000381_8p00s \
  --text "<exact transcript text>" \
  --ack-human-listened \
  --ack-transcript-exact
```

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/mark_reference_review_decision.py \
  --candidate prompt_ref_candidate_04_000381_8p00s \
  --decision accepted \
  --exact-transcript exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_04_000381_8p00s.exact-transcript.txt \
  --ack-human-listened \
  --ack-own-voice-authorized \
  --ack-3-to-10s \
  --ack-clean-audio \
  --ack-no-heavy-filler \
  --ack-no-clipping \
  --ack-transcript-exact
```

If human listening selects a different prompt-ready reference, use that candidate stem consistently in both commands. Formal chunk generation now resolves the single accepted marker under `exports/smart-biomedicine-gpt-sovits/qa/reference-decisions/`.

Machine QA manifest:

- `exports/smart-biomedicine-gpt-sovits/qa/reference-quality/reference-quality-manifest.md`
- `exports/smart-biomedicine-gpt-sovits/qa/reference-quality/reference-quality-manifest.csv`
- `exports/smart-biomedicine-gpt-sovits/qa/reference-transcript-gate.md`
- `exports/smart-biomedicine-gpt-sovits/qa/reference-visual-qc/reference-visual-qc.md`
- `exports/smart-biomedicine-gpt-sovits/qa/reference-decisions/reference-decision-status.md`
- waveform and spectrogram PNGs under `exports/smart-biomedicine-gpt-sovits/qa/reference-visual-qc/`

Current machine-screened warning: all current extracted candidates reach digital full scale (`peak=32768`), so human listening must specifically check harsh consonants, clipping, and tail artifacts before acceptance.

Current human-listening order:

1. `prompt_ref_candidate_04_000381_8p00s`
2. `prompt_ref_candidate_01_000009_5p40s`
3. `prompt_ref_candidate_02_000036_8p00s`
4. `prompt_ref_candidate_03_000072_8p00s`
5. `prompt_ref_candidate_05_000480_8p00s`

If a candidate is rejected after listening, record it with `mark_reference_review_decision.py --decision rejected --ack-human-listened`, then rerun `reference_decision_status.py`.

Fallback adaptation review set:

- `exports/smart-biomedicine-gpt-sovits/reference/adaptation-clean-set-v1/adaptation_clean_set_v1_review_only.wav`
- Duration: `48.00s`
- Status: review-only, pending human listening and exact transcript bundle
- Purpose: fallback only if prompt-mode zero-shot voice identity is unstable.

## Commands Used

Candidate extraction pattern:

```bash
ffmpeg -hide_banner -y -ss <START> -t 12.00 \
  -i /home/jnclaw/Downloads/260528_0839_record.mp3 \
  -ac 1 -ar 16000 -sample_fmt s16 \
  exports/smart-biomedicine-gpt-sovits/reference/ref_candidate_<N>_<START>_12s.wav
```

Prompt-ready extraction pattern:

```bash
ffmpeg -hide_banner -loglevel error -y -ss <START> -t <3_TO_10_SECONDS> \
  -i /home/jnclaw/Downloads/260528_0839_record.mp3 \
  -ac 1 -ar 16000 -sample_fmt s16 \
  exports/smart-biomedicine-gpt-sovits/reference/prompt_ref_candidate_<N>_<START>_<DURATION>.wav
```

ASR runtime pattern:

```bash
CUDA_VISIBLE_DEVICES=0 \
LD_LIBRARY_PATH=/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/lib/python3.12/site-packages/nvidia/cublas/lib:/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/lib/python3.12/site-packages/nvidia/cudnn/lib:/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib \
/home/jnclaw/every_on_git_jnclaw/project_aura/.venv/bin/python <asr_script.py>
```
