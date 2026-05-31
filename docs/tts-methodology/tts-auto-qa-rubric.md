# TTS Automated QA Rubric

## 目的

本 rubric 定義 TTS 研究語音材料的 automated / semi-automated acceptance gate。它取代「人工聽起來可以」的主觀 gate。人可以閱讀 QA 報告並決定是否修復，但不可用主觀聽感直接覆蓋機器 gate。

## ASR Back-Transcription

依 profile 決定文字相似度門檻：

| Profile | CER | WER | 使用情境 |
| --- | ---: | ---: | --- |
| `internal_draft` | `<= 12%` | `<= 18%` | 私下快速測試 |
| `teaching_material` | `<= 8%` | `<= 12%` | 課程、教學、簡報、demo |
| `research_stimulus` | `<= 5%` | `<= 8%` | 研究刺激材料 |
| `public_external` | `<= 6%` | `<= 10%` | 對外公開影片或音檔 |

預設 teaching / demo 接受門檻：

- `CER <= 8%`
- `WER <= 12%`
- `Critical term accuracy = 100%`
- No meaning-changing omission
- No repeated sentence loop
- No negation loss
- No responsibility-boundary reversal

若當前工具只提供 transcript similarity ratio，必須同時保留 critical-term gate。高 similarity 不代表語意安全。

## Pronunciation Lexicon Check

- 所有在 source/model-facing text 中出現的 `critical=yes` terms，必須在
  ASR transcript 中命中 canonical term、preferred reading、或 aliases。
- preferred reading 可以是英文拼讀、中文讀法、或專案指定替代句。
- aliases 用 `|` 分隔，例如 `FDA five ten k|F D A 510 K|FDA 510 K`。
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

## Rights Gate

接受門檻：

- `public_external` 需要 `can_share_externally: yes`。
- `research_stimulus` 需要 `can_use_for_research: yes`。
- 真人 reference voice 若缺 consent，研究使用狀態為 `research_use_blocked`。
- synthetic voice disclosure 是否需要揭露必須明確記錄。

rights gate 只記錄授權與使用範圍，不把 raw reference audio 放進公開 repo。

## Optional Semantic Drift Check

LLM semantic-drift check 可以作為輔助檢查，但不單獨決定通過。它適合抓：

- meaning-changing omission
- wrong actor
- wrong responsibility
- wrong number
- wrong regulation
- clinical boundary drift
- unsupported claim

涉及 clinical、regulatory、numeric claim 的錯誤可以形成 reject reason。其他語氣差異
以 warning 處理。

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
