# Video Recording QA Sheet v1

Use this after the full audiovisual report is recorded.

## Required Output

- Video length target: `19-20` minutes.
- Visual source: `markdown-report-v1.md`.
- Preferred visual surface: `exports/smart-biomedicine-breezyvoice/recording/markdown-report-recording.html`.
- Audio source: accepted stitched BreezyVoice 26 WAV master, or approved fallback mix.
- Submission path: upload to YouTube, then post to Padlet before `2026-06-13 23:00`.

## Technical QA

- [ ] Final video opens and plays locally from start to end.
- [ ] Generated recording HTML opens in Firefox or the chosen recording browser.
- [ ] Runtime is inside the target range or has a clear reason if slightly outside.
- [ ] BreezyVoice final-video gate has been run after export:
  `python3 data/projects/2026-06-smart-biomedicine-final-report/tools/final_video_gate_status.py --export-root exports/smart-biomedicine-breezyvoice`.
- [ ] Audio is present in both left and right playback channels or plays clearly in mono.
- [ ] Audio is not clipped, too quiet, or distorted.
- [ ] Video resolution is at least `1080p` if possible.
- [ ] Text is readable on a laptop screen.
- [ ] No desktop notifications, private files, terminal secrets, unrelated tabs, or personal messages appear.
- [ ] Mermaid diagrams render correctly.
- [ ] Paper figures render correctly.
- [ ] Tables are readable when discussed.

## Content QA

- [ ] Opening states topic, course context, name, and student number.
- [ ] The core question appears early.
- [ ] The thesis is clear: staff-review previsit intake support.
- [ ] ASR and large language model roles are defined.
- [ ] Hager et al. is used as a boundary paper, not overclaimed.
- [ ] Lang1 is used as workflow-specific design evidence, not treated as the system being built.
- [ ] Proposed architecture keeps clinical authority with humans.
- [ ] Synthetic example is clearly fictional.
- [ ] Validation path and risk controls are explained.
- [ ] Closing restates the responsible smart-biomedicine contribution.

## Sync QA

- [ ] Chunk `01`: top identity and thesis stay visible long enough.
- [ ] Chunk `03`: definitions table visible while terms are defined.
- [ ] Chunk `04`: first Mermaid diagram visible during bottleneck explanation.
- [ ] Chunk `05`: speech-to-summary Mermaid diagram visible during architecture explanation.
- [ ] Chunk `07`: Hager title page visible during boundary explanation.
- [ ] Chunk `08`: Lang1 overview figure visible during overview explanation.
- [ ] Chunk `09`: zero-shot and finetuning figures visible during results explanation.
- [ ] Chunk `10`: proposed architecture decision node visible during safety-center explanation.
- [ ] Chunk `12`: synthetic output table visible during example explanation.
- [ ] Chunk `13`: validation path and risk matrix visible during validation explanation.
- [ ] Chunk `14`: references visible before the recording ends.

## Submission QA

- [ ] YouTube upload completed.
- [ ] `youtube-url.txt` proof file exists after upload.
- [ ] YouTube playback checked after upload.
- [ ] Visibility setting is suitable for course submission.
- [ ] Padlet post includes student ID, name, and report title.
- [ ] `padlet-post-proof.md` proof file exists after posting.
- [ ] Padlet link opens correctly.
- [ ] Upload evidence captured in day note or project tracker.
- [ ] Peer engagement remains scheduled before `2026-06-17`.
- [ ] `peer-engagement-proof.md` exists after watching, commenting/questioning, and liking.
- [ ] Presenter-response check remains scheduled before `2026-06-20`.
- [ ] `presenter-response-proof.md` exists after checking and answering report questions.
