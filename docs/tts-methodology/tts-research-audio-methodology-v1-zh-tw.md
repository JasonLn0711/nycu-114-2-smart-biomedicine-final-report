# TTS 研究語音製作方法論 v1

## 目的

本方法論用於研究、教學、簡報、臨床前問診模擬、ASR/LLM demo 的合成語音製作。目標不是只得到「人類大致聽得懂」的語音，而是建立可記錄、可比較、可重現、可自動檢查的研究級 TTS production workflow。

本 repo 的未來 TTS 接受標準改為「全自動／半自動 QA gate」。TTS 生成後，必須用 ASR 回轉錄、術語比對、音訊品質檢查、chunk consistency、hash/provenance 來判斷是否可接受。人工可以閱讀 QA 報告並決定是否重跑，但不以主觀聽感作為 production acceptance gate。

## 基本原則

1. `source text` 與 `model-facing text` 分開。前者保留人類閱讀與研究語意，後者專門給 TTS 模型朗讀。
2. 先修文字，再修音訊。若 ASR 反覆錯同一類字詞，先改寫 model-facing text，而不是只改參數。
3. 先 pilot render，再 full render。每個模型或 voice route 先產 `1-3` 個短 clip。
4. ASR back-transcription 作為主要 QA gate。ASR transcript 必須回頭驗證 source intent、critical terms、否定詞、數字與邊界句。
5. 所有輸出都保存 provenance。至少保存 command、模型版本、runtime、source hash、output hash、QA result。
6. 真人 reference voice 必須記錄來源、授權與使用範圍。
7. 公開 repo 只放方法、參數、hash、QA 結果。reference audio、生成音檔、失敗樣本放 local/private storage。
8. 失敗樣本要分類保存。失敗樣本是下一次改寫文本與設計 gate 的主要資料。
9. 長語音以 chunk 為單位生成、檢查、修復、接受，再進行 stitching。
10. 接受條件必須事先寫清楚，不在結果不好時臨時降低標準。

## Pipeline

```text
source text
-> model-facing text
-> pronunciation lexicon
-> chunking
-> pilot render
-> ASR back-transcription
-> automated QA
-> local repair
-> full render
-> loudness/stitching
-> final package
-> archive
```

## 資料夾責任

```text
docs/tts-methodology/
```

保存方法論、規則、rubric、failure taxonomy、倫理與授權說明。這些文件可公開追蹤。

```text
templates/
```

保存每次實驗必填卡、pronunciation lexicon 模板、未來可擴充的 QA config。

```text
logs/tts-experiments/
```

保存 repo-safe experiment cards。卡片只記錄路徑、hash、參數、QA 結果與修復策略，不保存 private audio。

```text
qa/tts-auto-checks/
```

保存 repo-safe automated QA 摘要，例如模型比較、通過/未通過原因、門檻設定、critical-term coverage。

```text
assets/tts-local-only/
```

local/private storage。放 reference audio、generated WAV/MP3/M4A、failed samples、不可公開的聲音資料。此資料夾被 `.gitignore` 排除。

## Source Text 與 Model-Facing Text

`source text` 是研究內容的權威文本，保留正式用語、引用、表格、報告語意與人類可讀結構。

`model-facing text` 是朗讀稿，目標是讓 TTS 和後續 ASR 都穩定。它可以：

- 拆短句。
- 改寫縮寫。
- 把符號改成可念文字。
- 把容易誤聽的術語改成較穩定讀法。
- 將高風險邊界句改成獨立短句。
- 將數字、單位、年份改為固定讀法。

model-facing text 不需要看起來像正式論文稿。它是給模型念的，不是給人閱讀的稿。

## Pilot Render Gate

每個新的模型、reference voice、語言、領域或講稿風格都先做 pilot：

1. 選 `1-3` 段，包含開場、技術詞密集段、風險邊界段。
2. 生成短 clip。
3. 跑 ASR back-transcription。
4. 跑 pronunciation lexicon check。
5. 跑 clipping/silence/loudness/sample-rate check。
6. 若 pilot 未通過，不進入 full render。

## Automated QA Gate

每個 chunk 必須至少產出：

- source text hash。
- model-facing text hash。
- generation command。
- output file hash。
- ASR transcript。
- CER/WER 或等價 transcript similarity 指標。
- critical-term accuracy。
- audio-quality report。
- chunk-boundary report。
- accepted/rejected result。

接受條件：

```text
CER <= 8%
WER <= 12%
Critical term accuracy = 100%
No clipping
No broken chunk boundary
No meaning-changing omission
```

若系統暫時沒有 CER/WER 計算器，必須先記錄替代 gate，例如 ASR ratio、critical phrase check、term coverage。下一版工具應補上 CER/WER。

## Repair Order

修復順序固定如下：

1. 改 model-facing text：拆句、換標點、換讀法、補上下文。
2. 更新 pronunciation lexicon：補 critical term 與 preferred reading。
3. 調整 chunk boundary：避免在術語、否定詞、條列中間切段。
4. 調整 TTS 參數：speed、temperature、top-p、seed。
5. 更換 reference voice 或 reference segment。
6. 更換模型或 route。

不要先靠大量參數嘗試掩蓋文本設計問題。

## Chunking 原則

- 每個 chunk 只承擔一個主題單元。
- 高風險術語前後保留語意上下文。
- 否定句與臨床邊界句單獨成句。
- 避免 chunk 開頭第一個詞就是 critical term。
- 避免 chunk 結尾停在未完成語意或連接詞。
- failed chunk 可以局部重生，不需要重生整段 master。

## Provenance 最小欄位

每次生成至少記錄：

- experiment ID。
- timestamp。
- project。
- model and checkpoint。
- ASR model。
- device and runtime。
- source text path and SHA256。
- model-facing text path and SHA256。
- reference audio path and SHA256。
- generation command。
- output path and SHA256。
- QA report path。
- accepted/rejected。
- repair action。

## 隱私與授權

只要 reference voice 來自真人，就必須填寫 `tts-ethics-rights-and-disclosure.md` 的欄位。未填寫前，語音資料只能保存在 local/private storage，不得外部分享。

若語音會進入研究、公開展示、課程影片或 dataset，必須另外記錄是否需要 synthetic voice disclosure、IRB relevance、刪除或撤回機制。

## 本次專案轉換出的規則

這次 Smart Biomedicine final report 的經驗支持以下規則：

- 全英文長報告不要假設模型一次就能穩定朗讀。
- ASR 回轉錄能比主觀聽感更早發現 meaning-changing error。
- 縮寫、數字、否定詞、醫療責任邊界是高風險區。
- 高 ASR ratio 仍可能藏有臨床意義錯誤，所以 critical-term gate 必須獨立存在。
- BreezyVoice 對本專案可用，但需要短句、局部上下文、避免壓縮英文名詞片語。
- F5-TTS 可產出候選聲音，但未通過相同 automated QA 前不得直接進入 final package。
- GPT-SoVITS 的失敗紀錄是有效的 text-repair 訓練資料，即使模型 route 後來被替換。
