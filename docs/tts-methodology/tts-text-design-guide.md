# TTS Text Design Guide

## 核心規則

model-facing text 是給模型念的，不是給人閱讀的稿。source text 可以正式、完整、論文化；model-facing text 應該短、穩、可念、可被 ASR 回轉錄驗證。

## 句子

- 每句控制在 `15-25` 個中文字左右；英文句子控制在 `8-18` 個單字左右。
- 技術長句拆成短句。
- 條列內容改成口語連貫句。
- 每句只承擔一個語意動作。
- 否定句、風險邊界句、責任歸屬句獨立成句。
- 避免一口氣塞入 `3` 個以上術語。

## 標點

- 逗號處理短停頓。
- 句號處理語意終點。
- 分號通常改成句號。
- 冒號後面的長條列改成獨立句。
- 避免括號、斜線、過密標點。
- 避免連續破折號或複雜插入語。

## 英文與縮寫

- `ASR` 固定寫成 `A-S-R` 或 `automatic speech recognition`。
- `LLM` 固定寫成 `L-L-M` 或 `large language model`。
- `FDA 510(k)` 固定寫成 `F-D-A five ten k`。
- `RAG` 固定寫成 `R-A-G`。
- 第一次出現用全名，後面才用縮寫。
- 若 ASR 回轉錄仍不穩，優先使用全名，不強迫模型念縮寫。
- 避免中英黏在一起，例如 `ASR轉錄`；改為 `A-S-R creates the transcript` 或 `語音辨識建立轉錄稿`。

## 數字

- `2026` 改成 `二零二六年` 或固定英文讀法 `twenty twenty six`。
- `15 minutes` 改成 `fifteen minutes`。
- `20-minute report` 改成 `twenty minute report`。
- `kHz`、`ms`、`GB`、`GPU` 要固定讀法。
- 長學號、電話、序號不建議放入 TTS；若必須朗讀，分段並建立 ASR gate。

## 醫療與研究術語

- 醫療詞、法規詞、模型詞都放入 pronunciation lexicon。
- 高風險詞前後加上下文，避免孤立術語。
- `triage` 若英文不穩，可改成 `patient priority sorting` 或依專案指定讀法。
- `clinical authority` 若不穩，可改成 `human staff make the final decision`。
- `care decision` 若不穩，可改成 `medical decision`，但要確認語意沒有偏移。

## 否定與邊界

高風險否定句不要放在長句尾端。建議寫成直接、短、可檢查的句子：

```text
The system does not make a diagnosis.
The system does not decide patient priority.
The system does not create a treatment plan.
Human staff check the draft first.
The doctor makes the medical decision.
```

## Chunk 開頭與結尾

- chunk 開頭先給短上下文，再進入 critical term。
- chunk 結尾不要停在 `and`、`but`、`because`、`such as`。
- chunk 結尾避免快速列舉。
- 每個 chunk 結尾保留完整語意句。

## 修稿優先順序

1. 拆句。
2. 改標點。
3. 補上下文。
4. 改術語讀法。
5. 改 chunk boundary。
6. 最後才改 TTS 參數。
