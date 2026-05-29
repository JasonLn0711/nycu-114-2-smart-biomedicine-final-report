# Smart Biomedicine Final Report Video Plan

## Role Of This Repo

This repository is the video control repo for the NYCU 114-2 Smart Biomedicine final report. It owns the Remotion timeline, narration placement, transcript copies, scene storyboard, image asset manifest, and render evidence.

The image-generation skill owns illustration production only. Generated image files are placed under `public/images/` so Remotion can render them, while source prompts and scene intent remain documented here.

## Current Timeline

- Target format: `1920x1080`, `16:9`, `30 fps`.
- Narration source: `public/audio/narration.wav`.
- Narration provenance: `exports/smart-biomedicine-breezyvoice/stitching/smart-biomedicine-final-report-narration-v1.wav`.
- Total duration: `940.895s`, about `15:41`.
- Scene count: `14`.
- Timing authority: accepted BreezyVoice chunk WAV durations plus `0.5s` stitch gaps between chunks.

## Render Surface

The Remotion video uses one scene image per narration chunk. Each image is held for the corresponding audio chunk, with a restrained slow zoom and a bilingual caption band. The English caption supports the spoken report; the Traditional Chinese caption records the course-facing concept and keeps the visual intent inspectable.

## Tracked Source Package

- `docs/storyboard.md`: scene-by-scene visual plan.
- `docs/asset_manifest.md`: image asset status and prompt summaries.
- `src/scenes.ts`: Remotion scene data.

## Local Render Inputs

These files live under ignored `public/` paths because they are generated,
copied, or media-heavy render inputs:

- `public/audio/narration.wav`: copied local narration master.
- `public/transcript/script.md`: copied narration script for render review.
- `public/transcript/script_segments.json`: optional scene timing and captions.
- `public/transcript/subtitles.srt`: optional scene-level subtitle file.
- `public/images/scene_001.png` through `public/images/scene_014.png`:
  generated illustration assets.
- `public/exports/final_report.mp4`: final rendered video.

## Verification Plan

1. Confirm `public/audio/narration.wav` exists and matches the accepted BreezyVoice stitched narration duration.
2. Confirm every scene listed in `src/scenes.ts` has a matching `public/images/scene_###.png`.
3. Run `npm install` if dependencies are missing.
4. Run `npm run render:quick` to verify Remotion can load the composition and assets.
5. Run `npm run render` for the full `public/exports/final_report.mp4` render.
6. Inspect render output and record final evidence under the existing QA/export surfaces.
