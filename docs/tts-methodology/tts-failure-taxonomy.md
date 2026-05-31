# TTS Failure Taxonomy

## Text-Side Failure

長句、標點錯、縮寫太多、術語堆疊、中英黏在一起、否定詞位置太弱、條列太密、source text 直接拿去給模型念。

常見修復：

- 拆句。
- 用全名取代縮寫。
- 把符號改成可念文字。
- critical term 前後補上下文。
- 將邊界句改成獨立短句。

## Model-Side Failure

吞字、重複、幻覺音節、聲音飄移、語氣突然改變、尾音消失、字詞被模型自動替換。

常見修復：

- 降低長句複雜度。
- 產多個 pilot clips。
- 換 seed 或 temperature。
- 換 reference segment。
- 改用更適合該語言的模型。

## Reference-Side Failure

reference audio 太吵、太短、語氣不合、音質不穩、授權不清楚、情緒或語速不適合目標材料。

常見修復：

- 換乾淨 reference。
- 縮短或重新裁切 reference。
- 記錄 consent/rights。
- 建立 local-only reference archive。

## Chunk-Side Failure

切段位置不自然、上下文斷裂、段落開頭怪、critical term 在 chunk 第一個詞、chunk 尾端被切掉。

常見修復：

- 調整 chunk boundary。
- 在 chunk 開頭補 setup sentence。
- 在 chunk 結尾補完整收束句。
- failed chunk 局部重生。

## Stitching-Side Failure

接縫突兀、音量不一致、尾音被切掉、silence gap 太長或太短、sample rate 不一致。

常見修復：

- 統一 sample rate。
- loudnorm。
- 加固定 gap。
- 檢查每段開頭與結尾 silence。
- 重跑 full master 的 audio-quality gate。

## Delivery-Side Failure

YouTube 壓縮、手機喇叭聽不清、影片音量太小、背景音樂蓋過旁白、字幕與語音不同步。

常見修復：

- video narration target around `-16 LUFS`。
- 上傳後再檢查平台播放。
- 保留字幕或 transcript。
- 保存 final mux command。

## Research-Side Failure

TTS artifact 影響研究刺激材料效度。例如聲音不自然造成受試者注意力偏移、術語錯誤造成錯誤理解、不同 chunk 音色差異造成條件不一致。

常見修復：

- 研究刺激材料先跑 pilot gate。
- 記錄所有 TTS artifacts。
- 每個 experimental condition 使用一致聲音與一致 loudness。
- 將 TTS artifact 作為研究 limitation 或 exclusion criterion。
