# TTS Platform Delivery QA

TTS auto-QA decides whether the generated research audio is acceptable. Delivery
QA decides whether a final video or audio package survives the target platform.
Keep these layers separate.

## Platform Smoke Checks

- Final media opens without error.
- Audio stream exists after upload or platform processing.
- Subtitle/transcript file is attached when available.
- Cover page and attribution page are visible long enough to read.
- Mobile playback is intelligible through phone speakers.
- Platform compression does not make the narration too quiet.
- The uploaded file or URL matches the release manifest hash when a direct file
  hash can be verified.

## Delivery Failure Status

Use `rejected_platform_smoke` only when the rendered or uploaded delivery asset
fails a platform check. Do not use this status for raw TTS chunk failures; those
belong to text, term, audio, chunk-boundary, or rights gates.

## Evidence To Preserve

- final media filename and SHA256
- duration, resolution, FPS, audio stream summary
- uploaded URL
- upload timestamp
- screenshot path in local/private storage
- course submission post URL
- subtitle/transcript attachment status
