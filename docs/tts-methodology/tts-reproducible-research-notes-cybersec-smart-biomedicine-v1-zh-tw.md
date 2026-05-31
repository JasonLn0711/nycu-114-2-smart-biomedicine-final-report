# 跨專案 TTS 可重現研究筆記 v1

日期：2026-05-31
範圍：CYBERSEC / CDE 醫療資安演講 TTS production 經驗，以及智慧生醫概論期末報告 TTS production 經驗。
Canonical home：`docs/tts-methodology/` in this repo.
配套工具：`tools/run_tts_auto_qa.py`、`templates/tts-pronunciation-lexicon.csv`、`templates/tts-rights-manifest.yaml`、`qa/tts-auto-checks/`。

## First-principles conclusion

TTS 研究語音不是「把文字念出來」。它是一種受控研究材料製作流程。

因此，正式 gate 的判斷單位不是主觀聽感，而是一包可以重跑、可以比較、可以稽核的 evidence：

1. source text 是否凍結。
2. model-facing text 是否獨立保存。
3. TTS model、ASR model、runtime、command、seed、參數與 checkpoint 是否可追溯。
4. ASR back-transcription 是否保留。
5. CER / WER / critical term accuracy 是否達標。
6. 數字、否定詞、法規、臨床責任邊界是否沒有漂移。
7. 音訊品質是否沒有 clipping、長 silence、chunk loudness jump、sample-rate mismatch。
8. chunk boundary 是否沒有缺字、切尾、loop 或 output-prefix 漂移。
9. rights / consent / disclosure 是否通過目標用途。
10. final delivery 是否保存 hash、manifest、platform smoke check 與交付版本。

核心操作原則：

```text
source text != model-facing text != ASR transcript != final audio
```

研究級 TTS workflow 要把這四個物件分開存，分開 hash，分開 gate。

## Evidence map

### Case A：CYBERSEC / CDE 醫療資安演講

用途：長篇台灣華語醫療資安演講音檔，支援 CYBERSEC / CDE / Prof. Wu 相關簡報與討論。
主要模型路線：BreezyVoice / Breeze-ASR-25 warning path。
主要語言型態：台灣華語，混合 FDA、SBOM、K8S、Tesla、namespace、token 等醫療資安術語。
目標長度：最後 delivery target 改為約 70 分鐘。

本 repo family 的 tracked evidence：

- `../cybersec-2026-ai-samd-talk/docs/speaker-notes/breezyvoice/cde-2026-breezyvoice-tts-experiment-log-v1.md`
- `../cybersec-2026-ai-samd-talk/docs/speaker-notes/breezyvoice/README.md`
- `../cybersec-2026-ai-samd-talk/docs/speaker-notes/breezyvoice/model-ready/README.md`
- `../cybersec-2026-ai-samd-talk/logs/tts-experiments/EXP-20260528-001.md`
- `../cybersec-2026-ai-samd-talk/docs/tts-methodology/tts-model-comparison-summary.md`

已知 production facts：

| Item | Record |
| --- | --- |
| TTS model | `MediaTek-Research/BreezyVoice` / local BreezyVoice route |
| ASR model | `MediaTek-Research/Breeze-ASR-25` |
| Device | RTX 5080 |
| Main delivery target | approximately 70 minutes |
| Raw v3 stitch | `3476.290s` / `57.938min` |
| Final tempo-adjusted v3 master | `4199.983s` / `70.000min` |
| Final loudness-normalized v3 master | `4199.983s` / `70.000min` |
| Tempo strategy | one global `atempo=0.827687993`, computed after raw stitch |
| Loudness target | `ffmpeg loudnorm=I=-16:TP=-1.5:LRA=11` |
| ASR final warning pass | Breeze-ASR-25, `1060` chunks, `17478` text characters |
| Public repo boundary | generated audio, prompt audio, model caches, failed renders stay local-only |

重要經驗：

1. 台灣華語長篇 TTS 的第一個穩定化手段是 text conditioning，不是 audio post-processing。
2. CJK-English boundary 要明確。BreezyVoice / CDE 路線中，中文與英文 technical term 交界處加入 `、`，能降低術語黏連。
3. `token`、`namespace` 這類 standard technical term 要保留英文；一般英文片語則優先改成台灣繁體中文口語。
4. 案例段落要先用短 setup，再接 event path、clinical implication、review takeaway。這比把英文 slide note 直接翻成長句更穩。
5. 長音檔的 tempo 要用全檔單一比例，不要 section-by-section 改速，否則會破壞全場 pacing 一致性。
6. ASR 在這個 legacy CDE run 裡是 warning signal，不是 formal acceptance authority；未來研究用途需要補跑完整 auto-QA evidence package。
7. Dense sections，例如 K8S、Tesla、524B、SBOM、法規與 case-study 混在一起的段落，必須拆句、拆術語、拆責任邊界。
8. Reference voice 來自真人時，必須補 rights manifest、consent、allowed use、forbidden use、withdrawal mechanism。

目前判斷：

```text
CYBERSEC / CDE BreezyVoice route = production evidence rich, but legacy QA incomplete.
Future research reuse = must rerun auto-QA before accepted_auto_gate.
```

### Case B：智慧生醫概論期末報告

用途：英文課程報告 narration，主題為 ASR + LLM 在臨床前問診 workflow 的應用與邊界。
主要模型路線：BreezyVoice final route；F5-TTS candidate route；GPT-SoVITS historical repair route。
主要語言型態：英文 narration，含 ASR、LLM、clinical review、triage、summary、scope-control phrases。

本 repo 的 tracked evidence：

- `logs/tts-experiments/EXP-20260528-001.md`
- `logs/tts-experiments/EXP-20260528-002.md`
- `logs/tts-experiments/EXP-20260528-003.md`
- `qa/tts-auto-checks/EXP-20260531-001/qa_result.json`
- `qa/tts-auto-checks/EXP-20260531-001/qa_summary.md`
- `docs/tts-methodology/tts-model-comparison-summary.md`
- `data/projects/2026-06-smart-biomedicine-final-report/gpt-sovits-experiment-log-v1.md`
- `data/projects/2026-06-smart-biomedicine-final-report/f5tts-v2-generation-log-2026-05-28.md`

Auto-QA result for BreezyVoice final package:

| Metric | Value |
| --- | --- |
| Experiment ID | `EXP-20260531-001` |
| Profile | `teaching_material` |
| Status | `accepted_with_warnings` |
| CER | `0.0087` |
| WER | `0.0175` |
| Critical term accuracy | `1.0000` |
| Audio status | `pass` |
| Rights status | `pass` |
| Audio files checked | `14` chunk WAVs |
| Average integrated loudness | approximately `-15.24 LUFS` |
| Chunk loudness spread | approximately `1.09 dB` |

模型比較摘要：

| Model | Current evidence | Use decision |
| --- | --- | --- |
| BreezyVoice | Final route passed the runnable auto-QA MVP as `accepted_with_warnings`. | Current reference workflow for this repo family. |
| F5-TTS | Generated all `14` chunks on RTX 5080 with repeatable command and F5-TTS commit `2ae2c9b`, but no matching ASR/term/audio/chunk gate yet. | Candidate baseline only. |
| GPT-SoVITS | Produced high-value failure taxonomy and phrase-repair evidence; earlier route relied on historical chunk repair and did not transfer after model switch. | Repair evidence / future pilot baseline only. |

重要經驗：

1. High ASR ratio is not enough. Negation loss such as `not ready for automatic medical action` can reverse clinical meaning even when global similarity looks high.
2. Critical phrase gate must include clinical responsibility phrases, not only technical nouns.
3. Acronyms are fragile. `A. S. R.`、`ASR`、`LLM` should be controlled through lexicon aliases and model-facing text design.
4. Dense English phrases create homophone risks: `clinical authority / critical authority`、`surface / service`、`fluent / fluid`、`review / preview`。
5. Stale source is a real failure mode. If ignored exports contain old chunk text, regeneration can consume stale wording and be misdiagnosed as model failure.
6. Accepted audio is not portable across model switches. Once TTS model or source text changes, rerun ASR, term, audio, chunk, rights, and provenance gates.
7. Alias-aware critical term matching is required. Without aliases, acceptable ASR variants can create false reject.

目前判斷：

```text
Smart Biomedicine BreezyVoice route = accepted_with_warnings for teaching_material.
Research stimulus reuse = requires stricter profile, rights review, and possibly second-ASR audit.
```

## Reproducible workflow

### Required artifacts per experiment

Every experiment must have:

```text
source_text
model_facing_text
pronunciation_lexicon
rights_manifest
tts_command_or_runbook
tts_model_snapshot
asr_model_snapshot
runtime_environment
audio_outputs_local_or_private
asr_transcript
qa_result.json
qa_summary.md
term_error_list.csv
audio_quality_report.json
release_manifest.md
experiment_card.md
```

### Recommended folder routing

```text
docs/tts-methodology/              public methodology and QA docs
templates/                         reusable cards, lexicon, rights manifest
golden_pilots/                     stable cross-model pilot texts
logs/tts-experiments/              tracked experiment cards
qa/tts-auto-checks/                repo-safe QA summaries
assets/tts-local-only/             ignored local/private audio storage
exports/                           ignored generated media and local reports
```

### Minimum command pattern

```bash
python3 tools/run_tts_auto_qa.py \
  --source-text path/to/source.txt \
  --model-facing-text path/to/model_facing.txt \
  --asr-transcript path/to/asr_transcript_or_reports \
  --lexicon templates/tts-pronunciation-lexicon.csv \
  --audio-dir outputs/audio_chunks \
  --rights-manifest templates/tts-rights-manifest.yaml \
  --profile teaching_material \
  --experiment-id EXP-YYYYMMDD-001 \
  --out qa/tts-auto-checks/EXP-YYYYMMDD-001
```

### Profiles and thresholds

| Profile | CER | WER | Critical terms | Extra gate |
| --- | ---: | ---: | --- | --- |
| `internal_draft` | `<= 12%` | `<= 18%` | warning if non-critical missing | audio sanity and hash |
| `teaching_material` | `<= 8%` | `<= 12%` | `100%` for critical terms | platform smoke recommended |
| `research_stimulus` | `<= 5%` | `<= 8%` | `100%` for critical terms | second-ASR audit and IRB relevance |
| `public_external` | `<= 6%` | `<= 10%` | `100%` for critical terms | disclosure, rights, platform smoke |

For Chinese or mixed Chinese-English text, use normalized CER as primary and WER as secondary because Chinese has no reliable whitespace word boundary.

### Text similarity gate

Compare `model-facing text` with `ASR transcript`.

Required metrics:

- CER
- WER
- repeated sentence count
- missing sentence count
- numeric mismatch
- entity mismatch
- negation / responsibility boundary mismatch

Rule:

```text
Global CER/WER pass is necessary but not sufficient.
Any meaning-changing omission, number change, actor change, regulation change, or clinical responsibility reversal should reject.
```

### Critical term gate

The lexicon must support aliases:

```csv
term,preferred_reading,aliases,context,critical
ASR,A-S-R,"A S R|automatic speech recognition",technical,yes
LLM,L-L-M,"large language model|L L M",technical,yes
FDA 510(k),F-D-A five ten k,"FDA five ten k|F D A 510 K|FDA 510 K",regulation,yes
triage,triage,"分流|clinical triage",clinical,yes
RAG,R-A-G,"retrieval augmented generation|R A G",AI,yes
```

Rules:

- `critical=yes` must match `term` or any alias.
- Source-present critical terms only: if a term is not in the source/model-facing text, do not require it in ASR.
- Critical term missing => `rejected_term_error`.
- Non-critical term missing => warning.
- Term aliases must be versioned with the experiment because aliases change what counts as pass.

### Audio quality gate

Required checks:

- duration
- sample rate
- channel layout
- integrated loudness
- loudness spread across chunks
- true peak / sample peak
- clipping flag
- long silence count
- sudden loudness jump

Recommended thresholds:

```text
No clipping
No silence > 2.0 sec unless explicitly allowed
Same sample rate across chunks
Same channel layout across chunks
Integrated loudness around -16 LUFS for narration video
Chunk loudness difference <= 6 dB
```

Operational tools:

- `ffprobe` for stream metadata.
- `ffmpeg loudnorm` for EBU R128 loudness normalization.
- `ffmpeg silencedetect` for long silence detection.
- `ffmpeg ebur128` when a more explicit loudness scan is needed.

### Chunk consistency gate

Each chunk must record:

- chunk id
- output prefix
- source span or section id
- generation command
- output SHA256
- ASR report path
- start missing / end cut flag
- repeated-loop flag
- duration outlier flag
- local repair action

Failure examples:

- chunk starts after the first word.
- tail syllable is cut.
- same clause repeats.
- generated output uses old source text.
- loudness differs sharply from adjacent chunks.
- output prefix changes between reruns and breaks stitch order.

### Rights gate

Every voice experiment using a human reference voice must preserve:

```yaml
voice_source:
whose_voice:
consent_obtained:
allowed_use:
forbidden_use:
can_share_externally:
can_use_for_research:
synthetic_voice_disclosure_required:
irb_relevance:
storage_location:
deletion_or_withdrawal_mechanism:
```

Rules:

- `public_external` requires `can_share_externally=yes`.
- `research_stimulus` requires `can_use_for_research=yes`.
- Human reference voice without consent blocks research use.
- Synthetic voice disclosure should be treated as a delivery artifact, not hidden inside the generation log.
- Rights status must be evaluated before publishing or recruiting participants.

### Optional semantic drift gate

LLM-based semantic drift check is useful, but it should not be the only pass/fail authority.

Good use:

- detect wrong actor
- detect wrong responsibility
- detect wrong number
- detect wrong regulation
- detect clinical boundary drift
- detect unsupported claim
- detect negation loss

Decision rule:

```text
clinical / regulatory / numeric drift => reject
minor wording drift => warning
style drift only => no formal gate failure
```

## Web-verified technical stack, 2026-05-31

### TTS models

| Tool / model | Verified status | Recommended role in this repo family |
| --- | --- | --- |
| BreezyVoice | Official paper and Hugging Face model card describe a Taiwanese Mandarin TTS system adapted for polyphone disambiguation and code-switching. | Primary Taiwan Mandarin / mixed Mandarin-English candidate, especially for CYBERSEC / CDE style material. |
| F5-TTS | Official paper and GitHub describe flow-matching TTS with zero-shot and code-switching capability; current GitHub page reports official code and public checkpoints. | Cross-model pilot candidate and English/multilingual baseline; must pass the same auto-QA gate before production use. |
| GPT-SoVITS | Official GitHub describes zero-shot TTS from short samples, few-shot fine-tuning, cross-lingual support, and WebUI tooling. | Good candidate for few-shot voice experiments and failure-taxonomy learning; not accepted for final use without full evidence package. |
| CosyVoice 2 / CosyVoice 3 | Papers, official GitHub, and Fun-CosyVoice3 model card position CosyVoice as a multilingual zero-shot / streaming / in-the-wild speech synthesis family. CosyVoice 2 emphasizes low-latency streaming; CosyVoice 3 adds scale-up and post-training claims for content consistency, speaker similarity, prosody naturalness, broader language/dialect coverage, and 0.5B/1.5B routes. | Add CosyVoice 3 to the next golden-pilot test set, especially if latency, streaming, multilingual benchmarking, or in-the-wild robustness matters. Treat it as candidate-only until local QA evidence exists. |
| OpenAI Audio API / `gpt-4o-mini-tts` | Official OpenAI docs list `gpt-4o-mini-tts` for text-to-speech, built-in voices, streaming audio output, and required user disclosure that the voice is AI-generated. Official speech-to-text docs list `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, and diarization routes with file-size constraints. | Optional cloud baseline when data governance permits cloud processing. Record request JSON, model snapshot, voice, instructions, response hash, disclosure text, and second-ASR audit. Do not use for sensitive reference voices or research stimuli without an explicit data boundary. |

### ASR models and metrics

| Tool / model | Verified status | Recommended role |
| --- | --- | --- |
| Breeze-ASR-25 | Hugging Face model card records Taiwanese Mandarin / code-switching ASR benchmarks and usage through Transformers. | Current Taiwan Mandarin / mixed Mandarin-English ASR back-transcription baseline for these projects. |
| Breeze-ASR-26 / Breeze Taigi | 2026 model card and paper target Taiwanese Hokkien / Taigi ASR and benchmark methodology; it uses CER as primary metric and outputs Mandarin-character transcriptions. | Future Taigi or Taigi-Mandarin evaluation lane. Do not silently replace Breeze-ASR-25 for Taiwan Mandarin materials. |
| JiWER | Official docs and repository support WER and CER computation. | Good Python metric engine for English and normalized mixed-language QA. |

### Audio and provenance tools

| Tool / framework | Verified status | Recommended role |
| --- | --- | --- |
| FFmpeg `loudnorm` | Official FFmpeg docs define EBU R128 loudness normalization and target IL/LRA/TP options. | Primary loudness normalization and measurement route. |
| FFmpeg `silencedetect` / `ebur128` | Official FFmpeg filter docs provide silence and loudness scanning filters. | Long-silence detection and extra loudness audit. |
| C2PA | Official specification site now exposes `2.4`; the technical spec defines Content Credentials, claims, assertions, signatures, manifests, hard/soft bindings, and includes an `c2pa.ai-disclosure` assertion for machine-readable AI transparency. | Future delivery-layer provenance for public media or research stimuli where content credentials matter. Use it as provenance, not as proof that the audio is correct, consented, or clinically safe. |
| NIST AI RMF | Official NIST page provides a risk-management framework and GenAI profile resources. | Governance vocabulary for rights, disclosure, traceability, and risk controls. |

## Missing items to add next

These are the important pieces not fully solved by the current MVP.

### 1. Runtime environment manifest

Add a tracked template:

```text
templates/tts-run-environment.yaml
```

Required fields:

```yaml
os:
gpu:
gpu_driver:
cuda:
python:
pytorch:
transformers:
ffmpeg:
tts_repo:
tts_repo_commit:
tts_model_id:
tts_model_revision:
asr_model_id:
asr_model_revision:
generation_seed:
temperature:
top_p:
speed_or_tempo:
reference_audio_sha256:
source_text_sha256:
model_facing_text_sha256:
lexicon_sha256:
rights_manifest_sha256:
```

Reason: model names drift. A reproducible run needs snapshot ids and software versions, not just `BreezyVoice` or `F5-TTS`.

### 2. Second-ASR audit for research stimuli

For `research_stimulus`, use one primary ASR and one secondary ASR audit.

Recommended rule:

```text
primary ASR pass + secondary ASR no critical discrepancy
```

Reason: a single ASR can share blind spots with the TTS model or language domain.

### 3. Entity and responsibility gate

Add a structured table for:

- person / role
- organization
- drug / device / model name
- regulation
- percentage / date / numeric threshold
- negation phrase
- clinical responsibility phrase

Examples:

```text
"not ready for automatic medical action" must never become "ready for automatic medical action".
"FDA 524B" must not become "FDA 524".
"clinical staff check and correct" must not become "clinical staff incorrect".
```

### 4. Golden pilot regression test

Before a new TTS model enters a real project, run:

- `golden_001_opening.txt`
- `golden_002_mixed_terms.txt`
- `golden_003_case_story.txt`
- `golden_lexicon.csv`

Compare:

```text
model | CER | WER | critical term pass | audio pass | rights pass | status | notes
```

### 5. Research-validity note

For clinical, educational, or behavioral research stimuli, record whether TTS artifacts could affect the outcome.

Required question:

```text
Could accent, pace, prosody, syntheticness, clipping, or model-specific pronunciation become the experimental variable?
```

If yes, add:

- stimulus randomization plan
- speaker voice consistency plan
- loudness normalization proof
- participant disclosure wording
- IRB relevance note
- exclusion criteria for unstable audio

### 6. Delivery smoke gate

For YouTube, Padlet, Google Drive, LMS, or video platforms:

- upload final file
- download or stream once
- inspect platform transcode audio loudness
- verify subtitles if present
- preserve URL / screenshot / timestamp
- hash local final file and release manifest

This belongs in `docs/delivery/`, not the core TTS methodology.

### 7. C2PA / content-credential pilot

For public-facing synthetic voice artifacts, pilot a manifest path:

```text
final_media_hash
tts_model_id
tts_model_revision
source_text_hash
synthetic_voice_disclosure
rights_status
editorial responsibility
c2pa_spec_version
c2pa.ai-disclosure.modelType
c2pa.ai-disclosure.humanOversightLevel
```

This does not replace consent, IRB review, semantic QA, or platform disclosure.
It strengthens content provenance by making the generation route and human
oversight level machine-readable.

### 8. Energy, runtime, and cost log

Long-form TTS production can be expensive. Record:

- wall time
- GPU type
- average GPU utilization
- peak GPU memory
- estimated GPU energy
- number of failed chunks
- number of rerenders

The CYBERSEC / CDE log already shows this is useful for planning future production time.

### 9. Stale-source prevention

Before generation:

```text
hash tracked model-facing text
hash exported chunk text
compare
abort if mismatch
```

This should become a preflight in every generator wrapper.

### 10. Alias governance

Term aliases should be reviewed per domain.

Examples:

- `F D A five ten k` may be acceptable for narration.
- `FDA 510 K` may be acceptable in ASR transcript.
- `FDA 524B` is not interchangeable with `FDA 524`.
- `triage` may be accepted as `分流` in Chinese clinical context, but not in an English-only measurement unless specified.

### 11. Cloud API governance

If a future route uses a cloud TTS or ASR API, record more than the model name.

Required fields:

```yaml
provider:
endpoint:
model:
model_snapshot:
voice:
instructions:
request_json_sha256:
response_audio_sha256:
data_retention_policy:
patient_or_sensitive_data_present:
reference_voice_present:
synthetic_voice_disclosure:
second_asr_audit:
```

Reason: cloud services can change aliases, voices, model snapshots, safety
policy, request limits, and data-retention defaults. A cloud route can be a
useful benchmark, but it is not automatically more reproducible than a local
open-weight route unless the request, model snapshot, rights status, and output
hash are preserved.

## Current reproducibility decision

Use this decision table when starting a new TTS project.

| Question | Decision |
| --- | --- |
| Is the material Taiwan Mandarin or mixed Taiwan Mandarin-English? | Start with BreezyVoice + Breeze-ASR-25 pilot. |
| Is the material English/multilingual and needs a comparison baseline? | Run BreezyVoice, F5-TTS, CosyVoice 3, and optional cloud baseline on golden pilots. |
| Does it use a real human reference voice? | Fill rights manifest before generation, not after delivery. |
| Is the output for research participants? | Use `research_stimulus` profile and second-ASR audit. |
| Is the output public? | Add disclosure, delivery smoke, and content provenance manifest. |
| Is the output only an internal draft? | Use lower thresholds, but still keep hashes and commands. |
| Did any source/model/runtime change? | Rerun full gate; do not reuse old accepted status. |

## References checked on 2026-05-31

- BreezyVoice paper: <https://arxiv.org/abs/2501.17790>
- BreezyVoice model card: <https://huggingface.co/MediaTek-Research/BreezyVoice>
- Breeze-ASR-25 model card: <https://huggingface.co/MediaTek-Research/Breeze-ASR-25>
- Breeze-ASR-26 model card: <https://huggingface.co/MediaTek-Research/Breeze-ASR-26>
- Breeze Taigi paper: <https://arxiv.org/abs/2603.19259>
- F5-TTS paper: <https://arxiv.org/abs/2410.06885>
- F5-TTS official GitHub: <https://github.com/SWivid/F5-TTS>
- GPT-SoVITS official GitHub: <https://github.com/RVC-Boss/GPT-SoVITS>
- CosyVoice paper: <https://arxiv.org/abs/2407.05407>
- CosyVoice 2 paper: <https://arxiv.org/abs/2412.10117>
- CosyVoice 3 paper: <https://arxiv.org/abs/2505.17589>
- CosyVoice official GitHub: <https://github.com/FunAudioLLM/CosyVoice>
- Fun-CosyVoice3 model card: <https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512>
- OpenAI Audio guide: <https://platform.openai.com/docs/guides/audio>
- OpenAI Text to Speech guide: <https://platform.openai.com/docs/guides/text-to-speech>
- OpenAI Speech to Text guide: <https://platform.openai.com/docs/guides/speech-to-text>
- JiWER docs: <https://jitsi.github.io/jiwer/>
- JiWER GitHub: <https://github.com/jitsi/jiwer>
- FFmpeg filters: <https://ffmpeg.org/ffmpeg-filters.html>
- C2PA technical specification 2.4: <https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html>
- NIST AI Risk Management Framework: <https://www.nist.gov/itl/ai-risk-management-framework>
