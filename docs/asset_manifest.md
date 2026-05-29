# Image Asset Manifest

All final scene images should be generated one-by-one through `$ian-xiaohei-illustrations` / `image_gen`, then placed under `public/images/`.

| Scene | File | Status | Use | Prompt Summary |
| --- | --- | --- | --- | --- |
| `scene_001` | `public/images/scene_001.png` | pending generation | Opening thesis | Patient voice becomes a reviewable clinical draft; AI doctor framing is compressed into staff-reviewed draft support. |
| `scene_002` | `public/images/scene_002.png` | pending generation | Report format | A long Markdown scroll is visible, linear, inspectable, and correctable. |
| `scene_003` | `public/images/scene_003.png` | pending generation | Definitions | ASR transcribes, LLM structures, and staff review converts the draft into usable intake. |
| `scene_004` | `public/images/scene_004.png` | pending generation | Workflow bottleneck | A fragmented patient story is untangled before clinical reasoning begins. |
| `scene_005` | `public/images/scene_005.png` | pending generation | Speech-to-summary | Transcript, uncertainty markers, and missing questions travel together to staff review. |
| `scene_006` | `public/images/scene_006.png` | pending generation | Evidence landscape | Healthcare AI tools sit on different workflow layers with bounded ownership. |
| `scene_007` | `public/images/scene_007.png` | pending generation | Hager boundary | Fluent medical text stops at a clinical decision gate requiring stronger validation. |
| `scene_008` | `public/images/scene_008.png` | pending generation | Lang1 overview | Clinical models are measured against workflow-specific jobs and review signals. |
| `scene_009` | `public/images/scene_009.png` | pending generation | Lang1 results | General ability becomes dependable through adaptation, validation, and review data. |
| `scene_010` | `public/images/scene_010.png` | pending generation | Proposed architecture | Consent, voice intake, ASR, uncertainty, LLM draft, and review decision converge at a safety node. |
| `scene_011` | `public/images/scene_011.png` | pending generation | Scope controls | The system prepares drafts while diagnosis, triage, and treatment remain locked under clinical authority. |
| `scene_012` | `public/images/scene_012.png` | pending generation | Synthetic example | A fictional dizziness story becomes a checkable intake sheet with uncertainty and missing questions. |
| `scene_013` | `public/images/scene_013.png` | pending generation | Validation layers | ASR, structuring, human review, workflow, and governance form layered validation filters. |
| `scene_014` | `public/images/scene_014.png` | pending generation | Closing implication | Patient voice reaches a staff-review workbench and becomes a clinician-ready summary through the next validation path. |

## Generation Rules

- Use one separate `image_gen` call per scene.
- Preserve `16:9` horizontal layout and pure white background.
- Use sparse Traditional Chinese handwritten labels.
- Keep each image to one core concept.
- Use 小黑 as the default concept actor and 小拳 only where compression/execution or boundary enforcement is the scene's core action.
- Avoid dense PPT diagrams, realistic UI screenshots, formal flowcharts, and top-left title text.
