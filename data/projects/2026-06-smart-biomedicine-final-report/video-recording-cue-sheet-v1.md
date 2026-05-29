# Video Recording Cue Sheet v1

Purpose: record the final `19-20` minute video by scrolling `markdown-report-v1.md` in sync with the accepted narration master.

Status: recording not yet opened. The active audio route is now BreezyVoice 26. Audio must first reach `14/14` BreezyVoice accepted chunks and one stitched WAV master.

Visual source:

- `data/projects/2026-06-smart-biomedicine-final-report/markdown-report-v1.md`

Preferred generated recording surface:

- `exports/smart-biomedicine-breezyvoice/recording/markdown-report-recording.html`

Audio source after stitching:

- `exports/smart-biomedicine-breezyvoice/stitching/smart-biomedicine-final-report-narration-v1.wav`

## Recording Rules

- Use the Markdown preview or a clean browser-rendered Markdown view, not the raw editor text pane.
- Keep browser/editor chrome minimal and readable.
- Use a stable `16:9` viewport, preferably `1920x1080`.
- Scroll deliberately; do not scroll while a sentence is introducing a figure.
- Hold every Mermaid diagram or source figure long enough for the figure-text explanation.
- If generated audio is shorter than the target visual hold, add still-screen time instead of adding filler narration.
- Record one full pass only after the audio master is accepted.
- Export video only after checking audio/video sync from beginning, middle, and end.

## Chunk-To-Screen Timeline

| Chunk | Target screen position | Visual element to hold | Target hold | Recording cue |
| --- | --- | --- | ---: | --- |
| `sbm_tts_01_opening` | Title, course, student identity, core question, thesis | Title block and thesis | `60-75s` | Start at the top. Do not scroll until the thesis has been spoken. |
| `sbm_tts_02_markdown_format` | `How To Present This Markdown Report` | Timing table | `60-75s` | Scroll slowly through the table; pause on the report format explanation. |
| `sbm_tts_03_definitions` | `Key Definitions` | Definitions table | `75-90s` | Keep the full table readable. If text is small, zoom before recording. |
| `sbm_tts_04_workflow_problem` | `The Real Workflow Problem` | First Mermaid workflow bottleneck diagram | `75-90s` | Hold the diagram while explaining the bottleneck loop. |
| `sbm_tts_05_speech_to_summary` | `Why Speech-To-Summary Is Attractive` | Second Mermaid speech-to-summary architecture | `75-90s` | Hold on the architecture until staff review and clinician-ready summary are explained. |
| `sbm_tts_06_evidence_landscape` | `Evidence Landscape` | Evidence design question blockquote | `60-75s` | Pause on the design question before moving to source figures. |
| `sbm_tts_07_hager_boundary` | `Source Figure 1 - Hager et al. Boundary Paper` | Hager title page figure | `75-90s` | Keep the paper title visible while explaining the boundary-setting role. |
| `sbm_tts_08_lang1_overview` | `Source Figure 2 - Lang1 Overview` | Lang1 overview figure | `75-90s` | Hold the whole figure; do not crop the pipeline labels if possible. |
| `sbm_tts_09_lang1_results` | Source Figures 3 and 4 | Zero-shot and finetuning figures | `90s` | Split the hold between the two source figures; leave the finetuning figure visible at the end. |
| `sbm_tts_10_architecture` | `Proposed System Architecture` | Mermaid architecture and review decision node | `90s` | Hold the decision node; this is the main design contribution. |
| `sbm_tts_11_scope_controls` | `What The System May Do` and `What The System Must Not Do` | Scope-control lists | `60-75s` | Scroll from may-do to must-not-do only after the contrast is clear. |
| `sbm_tts_12_synthetic_example` | `Synthetic Example Output` | Synthetic output table | `75-90s` | Keep the uncertainty flag and missing questions visible. |
| `sbm_tts_13_validation_risk` | `Validation Path` and `Risk And Scope-Control Matrix` | Validation Mermaid and risk matrix | `90s` | Hold the validation path first, then scroll to the risk matrix. |
| `sbm_tts_14_closing` | `Final Takeaway` and `References` | Final takeaway and reference list | `60-75s` | End on the reference list for a few seconds before stopping recording. |

## Expected Runtime

- Nominal spoken chunk time from the chunk plan: about `924s` / `15m24s`.
- Stitch gaps: about `6.5s` if using `0.5s` gaps across `13` joins.
- Visual hold extension and transition buffer: about `3-4m`.
- Target final video: `19-20m`.

If the accepted stitched WAV is substantially shorter than expected, use slower figure holds. If it is substantially longer, reduce dead time between scrolls rather than cutting explanation.

## Recording Pass Checklist

- [ ] All `14` audio chunks are accepted.
- [ ] Stitched WAV master exists.
- [ ] BreezyVoice recording gate has been checked:
  `python3 data/projects/2026-06-smart-biomedicine-final-report/tools/video_recording_gate_status.py --export-root exports/smart-biomedicine-breezyvoice --engine-label BreezyVoice-26`.
- [ ] Markdown preview renders all Mermaid diagrams.
- [ ] Recording HTML top screenshot exists for basic render proof.
- [ ] All four paper/source images render.
- [ ] Browser/editor zoom makes tables readable.
- [ ] Screen recording captures system audio or imported narration audio cleanly.
- [ ] No notification banners or unrelated windows appear.
- [ ] Opening identity, topic, and course are visible at the start.
- [ ] Final references are visible at the end.
