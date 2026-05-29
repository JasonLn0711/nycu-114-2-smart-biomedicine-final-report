# 智慧生醫概論期末報告影片 Storyboard

總長：`15:41`
風格：小黑 / 小拳手繪內文配圖式教學影片
畫面比例：`16:9`
語氣：正式、清楚、容易理解
主控 repo：本 repo
產圖角色：`$ian-xiaohei-illustrations`

## Scene 01

時間：`00:00-01:29`
主題：開場與核心論點
畫面：小黑站在一個「病人語音」漏斗旁，語音碎片被整理成一張可審閱的臨床草稿；小拳在旁邊把「AI 醫師」牌子壓扁成「審核草稿」。
字幕重點：Patient speech can become a clinician-ready draft when staff review stays in control.

## Scene 02

時間：`01:29-02:42`
主題：Markdown 報告作為可檢查畫面
畫面：小黑拉開一卷長長的 Markdown 紙帶，上面只有幾個可檢查的節點；旁邊有可修正鉛筆與透明標籤。
字幕重點：The report surface should stay linear, visible, and easy to correct.

## Scene 03

時間：`02:42-03:59`
主題：關鍵定義與權責分層
畫面：三層小工作台：ASR 只接語音、LLM 只整理欄位、人員審核拿紅筆確認；小黑在層與層之間搬運一張草稿。
字幕重點：ASR transcribes, the LLM structures, and staff review turns the draft into usable intake.

## Scene 04

時間：`03:59-05:14`
主題：真實流程瓶頸
畫面：病人故事像打結的線團，裡面混著時間、藥名、症狀與擔心；小黑拿著小梳子把線團先整理成可問問題的形狀。
字幕重點：The first bottleneck is a fragmented patient story before clinical reasoning begins.

## Scene 05

時間：`05:14-05:49`
主題：Speech-to-summary 的基本流向
畫面：語音泡泡、逐字稿、不確定標記與缺漏問題一起坐在同一台小推車上，送往 staff review 櫃台。
字幕重點：Speech becomes useful when transcript, uncertainty, and missing questions travel together.

## Scene 06

時間：`05:49-07:06`
主題：醫療 AI 證據地景
畫面：小黑站在醫療流程地圖前，把「scribe」「documentation」「decision」「triage」放到不同高度的架子上，顯示每個工具有自己的位置。
字幕重點：Healthcare AI is realistic when each tool owns the right workflow layer.

## Scene 07

時間：`07:06-08:14`
主題：Hager et al. 的臨床決策邊界
畫面：主畫面放入 Hager et al. Nature Medicine 論文封面截圖，旁邊以淡化的小黑 / 小拳插畫作為 scope-control 背景；一台看起來很會寫字的 LLM 打字機停在 decision gate 前，小拳把閘門關住，旁邊標示 guideline、uncertainty、workflow。
論文素材：`public/images/papers/hager-2024-title-page.png`，必放。
字幕重點：Clinical decision-making needs stronger validation than fluent medical text.

## Scene 08

時間：`08:14-09:23`
主題：Lang1 與 workflow-specific evaluation
畫面：主畫面放入 Lang1 overview figure，顯示 clinical/web text、instruction finetuning、comparison 與 hospital/time/task ablation 的整體管線；插畫背景中，小黑把通用模型放進醫院流程的量尺裡量測。
論文素材：`public/images/papers/lang1-overview.png`。
字幕重點：A useful clinical model is evaluated on the workflow job it claims to support.

## Scene 09

時間：`09:23-10:13`
主題：從通用能力到任務適配
畫面：主畫面並排放入 Lang1 zero-shot results 與 finetuned specialist results，讓觀眾看到 zero-shot 與 finetuning 的差異；插畫背景是一條從 general ability 走向 task adaptation 的橋。
論文素材：`public/images/papers/lang1-zero-shot-results.png`、`public/images/papers/lang1-finetuning-results.png`。
字幕重點：General ability opens the path, but task adaptation and review data make it dependable.

## Scene 10

時間：`10:13-11:25`
主題：提案架構與審核決策節點
畫面：病人語音經過 ASR、uncertainty marking、LLM draft，最後全部停在一個大型審核開關；小黑和臨床人員一起操作 accept / clarify / reject。
字幕重點：The review decision node is the safety center of the whole architecture.

## Scene 11

時間：`11:25-12:13`
主題：系統可做與不可承擔的邊界
畫面：小拳把「prepare draft」放進工具箱，把 diagnosis、triage acuity、treatment plan 放在上鎖的臨床權責櫃。
字幕重點：The system may prepare a review draft; clinical authority remains human.

## Scene 12

時間：`12:13-13:26`
主題：合成案例輸出
畫面：虛構頭暈病人的故事被整理成一張檢查單；小黑用藍筆圈出 uncertainty，用橘線連到 missing questions。
字幕重點：The useful output is a checkable patient story with uncertainty and missing questions.

## Scene 13

時間：`13:26-14:22`
主題：分層驗證與風險控制
畫面：五層驗證濾網從上到下排列：ASR、structuring、human review、workflow、governance；小黑把草稿依序通過每一層。
字幕重點：Trust comes from layered validation: ASR, structuring, review, workflow, and governance.

## Scene 14

時間：`14:22-15:41`
主題：結尾與下一步驗證路徑
畫面：小黑把「patient voice」交給 staff-review 工作台，最後變成 clinician-ready summary；遠處有一條標示 next validation path 的清楚小路。
字幕重點：The next validation path is staff-reviewed intake support, not an autonomous AI doctor.
