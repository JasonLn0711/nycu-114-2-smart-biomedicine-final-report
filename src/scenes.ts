export const FPS = 30;

export type Scene = {
  id: string;
  title: string;
  start: number;
  duration: number;
  image: string;
  sourceImages?: Array<{
    src: string;
    label: string;
    fit?: "contain" | "cover";
  }>;
  caption: string;
  captionZh: string;
};

export const scenes: Scene[] = [
  {
    id: "scene_001",
    title: "Opening thesis",
    start: 0,
    duration: 88.655,
    image: "images/scene_001.png",
    caption: "Patient speech can become a clinician-ready draft when staff review stays in control.",
    captionZh: "病人語音可以成為臨床可審閱草稿，前提是人員審核保留主控權。",
  },
  {
    id: "scene_002",
    title: "Inspectable Markdown surface",
    start: 88.655,
    duration: 73.608,
    image: "images/scene_002.png",
    caption: "The report surface should stay linear, visible, and easy to correct.",
    captionZh: "報告畫面保持線性、可檢查、可修正。",
  },
  {
    id: "scene_003",
    title: "Key definitions",
    start: 162.263,
    duration: 76.789,
    image: "images/scene_003.png",
    caption: "ASR transcribes, the LLM structures, and staff review turns the draft into usable intake.",
    captionZh: "ASR 負責轉錄，LLM 負責結構化，人員審核讓草稿成為可用 intake。",
  },
  {
    id: "scene_004",
    title: "Workflow bottleneck",
    start: 239.052,
    duration: 75.013,
    image: "images/scene_004.png",
    caption: "The first bottleneck is a fragmented patient story before clinical reasoning begins.",
    captionZh: "第一個瓶頸是臨床推理前，病人故事仍然破碎。",
  },
  {
    id: "scene_005",
    title: "Speech to summary",
    start: 314.065,
    duration: 34.854,
    image: "images/scene_005.png",
    caption: "Speech becomes useful when transcript, uncertainty, and missing questions travel together.",
    captionZh: "語音要有用，轉錄、不確定性與缺漏問題要一起前進。",
  },
  {
    id: "scene_006",
    title: "Evidence landscape",
    start: 348.919,
    duration: 77.37,
    image: "images/scene_006.png",
    caption: "Healthcare AI is realistic when each tool owns the right workflow layer.",
    captionZh: "醫療 AI 的可行性來自每個工具承擔正確的流程層。",
  },
  {
    id: "scene_007",
    title: "Clinical decision boundary",
    start: 426.289,
    duration: 67.211,
    image: "images/scene_007.png",
    sourceImages: [
      {
        src: "images/papers/hager-2024-title-page.png",
        label: "Hager et al., Nature Medicine boundary paper",
      },
    ],
    caption: "Clinical decision-making needs stronger validation than fluent medical text.",
    captionZh: "臨床決策需要比流暢醫療文字更強的驗證。",
  },
  {
    id: "scene_008",
    title: "Workflow-specific evaluation",
    start: 493.5,
    duration: 69.73,
    image: "images/scene_008.png",
    sourceImages: [
      {
        src: "images/papers/lang1-overview.png",
        label: "Lang1 overview: workflow-specific clinical model pipeline",
      },
    ],
    caption: "A useful clinical model is evaluated on the workflow job it claims to support.",
    captionZh: "有用的臨床模型，要用它聲稱支援的流程任務來評估。",
  },
  {
    id: "scene_009",
    title: "Adaptation path",
    start: 563.23,
    duration: 49.541,
    image: "images/scene_009.png",
    sourceImages: [
      {
        src: "images/papers/lang1-zero-shot-results.png",
        label: "Lang1 zero-shot results",
      },
      {
        src: "images/papers/lang1-finetuning-results.png",
        label: "Lang1 finetuned specialist results",
      },
    ],
    caption: "General ability opens the path, but task adaptation and review data make it dependable.",
    captionZh: "通用能力開路，任務適配與審核資料讓系統可靠。",
  },
  {
    id: "scene_010",
    title: "Proposed architecture",
    start: 612.771,
    duration: 72.598,
    image: "images/scene_010.png",
    caption: "The review decision node is the safety center of the whole architecture.",
    captionZh: "審核決策節點是整個架構的安全中心。",
  },
  {
    id: "scene_011",
    title: "Scope controls",
    start: 685.369,
    duration: 47.323,
    image: "images/scene_011.png",
    caption: "The system may prepare a review draft; clinical authority remains human.",
    captionZh: "系統可以準備審核草稿，臨床權責仍由人承擔。",
  },
  {
    id: "scene_012",
    title: "Synthetic review draft",
    start: 732.692,
    duration: 73.515,
    image: "images/scene_012.png",
    caption: "The useful output is a checkable patient story with uncertainty and missing questions.",
    captionZh: "有用輸出是可檢查的病人故事，包含不確定性與缺漏問題。",
  },
  {
    id: "scene_013",
    title: "Validation layers",
    start: 806.207,
    duration: 56.158,
    image: "images/scene_013.png",
    caption: "Trust comes from layered validation: ASR, structuring, review, workflow, and governance.",
    captionZh: "可信度來自分層驗證：ASR、結構化、審核、流程與治理。",
  },
  {
    id: "scene_014",
    title: "Closing implication",
    start: 862.365,
    duration: 78.53,
    image: "images/scene_014.png",
    caption: "The next validation path is staff-reviewed intake support, not an autonomous AI doctor.",
    captionZh: "下一步驗證路徑是人員審核的 intake 支援，而不是自主 AI 醫師。",
  },
];

export const TOTAL_DURATION_SECONDS = 940.895;
export const TOTAL_FRAMES = Math.ceil(TOTAL_DURATION_SECONDS * FPS);
