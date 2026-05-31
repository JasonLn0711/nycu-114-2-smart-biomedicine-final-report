# TTS Automated QA Rubric

## 目的

本 rubric 定義 TTS 研究語音材料的 automated / semi-automated acceptance gate。它取代「人工聽起來可以」的主觀 gate。人可以閱讀 QA 報告並決定是否修復，但不可用主觀聽感直接覆蓋機器 gate。

## ASR Back-Transcription

接受門檻：

- `CER <= 8%`
- `WER <= 12%`
- `Critical term accuracy = 100%`
- No meaning-changing omission
- No repeated sentence loop
- No negation loss
- No responsibility-boundary reversal

若當前工具只提供 transcript similarity ratio，必須同時保留 critical-term gate。高 similarity 不代表語意安全。

## Pronunciation Lexicon Check

- 所有 `critical=yes` 的 terms 必須出現在 ASR transcript。
- preferred reading 可以是英文拼讀、中文讀法、或專案指定替代句。
- 錯誤術語列入 `term_error_list.csv`。
- critical term 錯誤直接 reject。
- 若術語反覆錯，優先改 model-facing text 或 preferred reading。

## Audio Quality Check

接受門檻：

- No clipping.
- No abnormal long silence `> 2.0 sec`.
- No sudden loudness jump `> 6 dB`.
- Integrated loudness target: around `-16 LUFS` for video narration.
- Same sample rate across chunks, unless conversion is explicitly documented.
- Same channel layout across chunks.
- No empty output.
- No truncated final word.

建議報告欄位：

- sample rate
- channel layout
- duration
- peak level
- integrated LUFS
- maximum silence duration
- clipping count
- output SHA256

## Chunk Consistency

接受門檻：

- chunk 開頭不得缺字。
- chunk 結尾不得被切斷。
- output prefix 必須穩定。
- chunk ID、source section、output file 必須一一對應。
- failed chunk 可以局部重生。
- accepted chunk 若被覆蓋，必須重跑 ASR 和 audio gate。

## Provenance Gate

接受門檻：

- source text SHA256 exists.
- model-facing text SHA256 exists.
- generation command exists.
- model/checkpoint exists.
- ASR model exists.
- device/runtime exists.
- output SHA256 exists.
- QA result exists.
- accepted/rejected decision exists.

缺少 provenance 的音檔不可作為研究材料。

## Final Acceptance

```text
CER <= 8%
WER <= 12%
Critical term accuracy = 100%
No clipping
No abnormal silence > 2.0 sec
No broken chunk boundary
No meaning-changing omission
Provenance complete
```

## Reject Conditions

任何一項出現即 reject：

- critical term missing or wrong
- negation missing
- diagnosis/triage/treatment boundary reversed
- repeated sentence loop
- hallucinated sentence
- output generated from stale source text
- reference voice rights missing
- clipping or severe loudness discontinuity
- chunk boundary cuts off words
