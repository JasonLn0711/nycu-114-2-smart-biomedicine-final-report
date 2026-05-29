# Image Asset Manifest

All final scene images should be generated one-by-one through `$ian-xiaohei-illustrations` / `image_gen`, then placed under `public/images/`.

| Scene | File | Status | Use | Prompt Summary |
| --- | --- | --- | --- | --- |
| `scene_001` | `public/images/scene_001.png` | generated | Opening thesis | Patient voice becomes a reviewable clinical draft; AI doctor framing is compressed into staff-reviewed draft support. |
| `scene_002` | `public/images/scene_002.png` | generated | Report format | A long Markdown scroll is visible, linear, inspectable, and correctable. |
| `scene_003` | `public/images/scene_003.png` | generated | Definitions | ASR transcribes, LLM structures, and staff review converts the draft into usable intake. |
| `scene_004` | `public/images/scene_004.png` | generated | Workflow bottleneck | A fragmented patient story is untangled before clinical reasoning begins. |
| `scene_005` | `public/images/scene_005.png` | generated | Speech-to-summary | Transcript, uncertainty markers, and missing questions travel together to staff review. |
| `scene_006` | `public/images/scene_006.png` | generated | Evidence landscape | Healthcare AI tools sit on different workflow layers with bounded ownership. |
| `scene_007` | `public/images/scene_007.png` | generated | Hager boundary illustration backing | Fluent medical text stops at a clinical decision gate requiring stronger validation; the Remotion scene also overlays the Hager et al. title-page screenshot. |
| `scene_008` | `public/images/scene_008.png` | generated | Lang1 overview illustration backing | Clinical models are measured against workflow-specific jobs and review signals; the Remotion scene also overlays the Lang1 overview figure. |
| `scene_009` | `public/images/scene_009.png` | generated | Lang1 results illustration backing | General ability becomes dependable through adaptation, validation, and review data; the Remotion scene also overlays Lang1 zero-shot and finetuned result figures. |
| `scene_010` | `public/images/scene_010.png` | generated | Proposed architecture | Consent, voice intake, ASR, uncertainty, LLM draft, and review decision converge at a safety node. |
| `scene_011` | `public/images/scene_011.png` | generated | Scope controls | The system prepares drafts while diagnosis, triage, and treatment remain locked under clinical authority. |
| `scene_012` | `public/images/scene_012.png` | generated | Synthetic example | A fictional dizziness story becomes a checkable intake sheet with uncertainty and missing questions. |
| `scene_013` | `public/images/scene_013.png` | generated | Validation layers | ASR, structuring, human review, workflow, and governance form layered validation filters. |
| `scene_014` | `public/images/scene_014.png` | generated | Closing implication | Patient voice reaches a staff-review workbench and becomes a clinician-ready summary through the next validation path. |

## Generation Rules

- Use one separate `image_gen` call per scene.
- Preserve `16:9` horizontal layout and pure white background.
- Use sparse Traditional Chinese handwritten labels.
- Keep each image to one core concept.
- Use 小黑 as the default concept actor and 小拳 only where compression/execution or boundary enforcement is the scene's core action.
- Avoid dense PPT diagrams, realistic UI screenshots, formal flowcharts, and top-left title text.

Generated originals are retained under `/home/jnln3799/.codex/generated_images/019e73de-ab8e-7361-97b7-12686ee59e9a/`; copied delivery assets live under `public/images/`.

## Paper Screenshot And Figure Assets

These evidence assets are copied from the report source package and displayed directly in Remotion, not regenerated as illustrations.

| Required? | File | Source | Video Use |
| --- | --- | --- | --- |
| yes | `public/images/papers/hager-2024-title-page.png` | `data/projects/2026-06-smart-biomedicine-final-report/assets/report-markdown/hager-2024-title-page.png` | Scene 07 paper-cover evidence for the clinical decision-making boundary. |
| yes | `public/images/papers/lang1-overview.png` | `data/projects/2026-06-smart-biomedicine-final-report/assets/report-markdown/lang1-overview.png` | Scene 08 overview evidence for workflow-specific clinical AI evaluation. |
| yes | `public/images/papers/lang1-zero-shot-results.png` | `data/projects/2026-06-smart-biomedicine-final-report/assets/report-markdown/lang1-zero-shot-results.png` | Scene 09 result evidence for zero-shot limitations. |
| yes | `public/images/papers/lang1-finetuning-results.png` | `data/projects/2026-06-smart-biomedicine-final-report/assets/report-markdown/lang1-finetuning-results.png` | Scene 09 result evidence for task adaptation and finetuning. |
