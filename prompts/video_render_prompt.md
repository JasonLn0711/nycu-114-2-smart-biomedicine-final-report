# Video Render Prompt

Use this repo as the Remotion video control repo.

## Inputs

- Audio: `public/audio/narration.wav`
- Script: `public/transcript/script.md`
- Segments: `public/transcript/script_segments.json`
- Scene images: `public/images/scene_001.png` through `public/images/scene_014.png`
- Scene data: `src/scenes.ts`

## Preview

```bash
npm run dev
```

## Quick Render Check

```bash
npm run render:quick
```

## Full Render

```bash
npm run render
```

Expected output:

```text
public/exports/final_report.mp4
```

Before claiming completion, verify that every scene image exists, Remotion loads `FinalReportVideo`, and the render command produces a playable MP4.
