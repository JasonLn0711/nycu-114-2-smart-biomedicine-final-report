# GPT-SoVITS Experiment Log v1

Purpose: preserve complete production evidence for the Smart Biomedicine final-report GPT-SoVITS narration workflow.

## Logging Rule

Every generation, ASR gate, repair, rerun, and acceptance decision must record:

- timestamp or sequence,
- chunk id,
- command or tool,
- runtime proof,
- output file,
- ASR ratio and decision,
- transcript mismatch,
- likely cause,
- repair applied,
- effect after repair,
- next action.

Generated logs and machine reports live under `exports/smart-biomedicine-gpt-sovits/qa/`. This tracked Markdown file records the human-readable experiment narrative.

## Chunk `01` Repair History

| Attempt | Result | ASR ratio | Main mismatch | Likely cause | Repair | Effect |
| --- | --- | ---: | --- | --- | --- | --- |
| `01-a` | rejected | `0.912` | Missing `My answer is yes`; `A. S. R.` heard as `A. Our`; student number normalized differently. | Acronym punctuation and long opening identity sentence caused TTS/ASR instability. | Split `My answer is yes`; changed `A. S. R.` to `A S R`; replaced hyphenated terms with spaced terms. | Critical phrase and acronym improved in later attempts. |
| `01-b` | rejected | `0.938` | `Lin` heard as `Wen`; student number heard as `513-559-559-504`. | Identity and numeric sequence were too fragile in synthetic narration. | Shortened opening identity; split student number cadence. | Acronym improved, but number remained unstable. |
| `01-c` | rejected | `0.952` | `zero zero four` heard as `sorrow sorrow for`; opening identity still unstable. | Digit sequence remained unreliable in TTS voice. | Removed spoken student number from narration; keep it in visual/Padlet text instead. | Identity section became shorter and more stable. |
| `01-d` | rejected | `0.941` | `clinical staff review and correct...` heard as `collect the output before it is shared`. | Long sentence with similar consonants changed meaning. | Rewrote as `staff check and correct the output before it influences care`. | Staff-review meaning became stable. |
| `01-e` | rejected | `0.971` | `autonomous urgency ranking` heard as `autonomous surgery ranking`; `human clinicians` heard as `human conditions`. | High-risk medical homophones and consonant clusters. | Rewrote boundary as `automatic priority scoring`; changed authority phrase toward simpler staff wording. | Boundary phrase improved, but authority phrase still needed repair. |
| `01-f` | rejected | `0.961` | `A S R` heard as `P S R`; `clinical authority` heard as `critical authority`. | Letter-by-letter acronym and `clinical` were unstable in this voice/reference. | Removed acronym pronunciation requirement from chunk `01`; used full phrase `Automatic speech recognition`; changed `clinical authority` to `final authority`. | Acronym and authority errors removed in next pass. |
| `01-g` | accepted by machine gate, needs polish repair | `0.994` | `designed as staff review intake support` heard as `designed to staff review intake support`. | `designed as staff review intake support` is grammatically dense and easy to slur. | Planned repair: replace with `support staff review before the visit`. | Pending rerun. |
| `01-h` | accepted | `0.990` | ASR transcript preserved the opening, scope control, speech-recognition definition, staff review, no-autonomous-diagnosis boundary, and final-authority point. Minor wording shifts remained acceptable: `structured, then summarized` for `structured, and summarized`; `workflow where` for `workflow:`. | Shorter sentences and full-form terminology were more stable than acronyms, numbers, and dense noun phrases. | Kept the simplified chunk text and accepted marker. | Chunk `01` is now accepted by the Breeze-ASR-25 gate and chunk `02` may be generated. |

## Machine Log Paths

- Generation JSONL: `exports/smart-biomedicine-gpt-sovits/qa/experiment-logs/chunk-generations.jsonl`
- ASR gate JSONL: `exports/smart-biomedicine-gpt-sovits/qa/experiment-logs/chunk-asr-gates.jsonl`
- Per-chunk ASR reports: `exports/smart-biomedicine-gpt-sovits/qa/chunk-asr/`
- Per-chunk repair plans: `exports/smart-biomedicine-gpt-sovits/qa/chunk-repairs/`

## Chunk `02` Repair History

| Attempt | Result | ASR ratio | Main mismatch | Likely cause | Repair | Effect |
| --- | --- | ---: | --- | --- | --- | --- |
| `02-a` | rejected | `0.976` | `artificial intelligence role` heard as `artificial intelligence rule`; `system I am proposing` heard as `system. My output`. | Dense phrase and `role/rule` homophone made the scope sentence unstable. The critical-phrase checker also overmatched `clinical review screen` across non-contiguous source tokens, which needed tool repair. | Rewrote as `my proposed system` and `the job of artificial intelligence`; fixed critical-phrase detection to require contiguous phrase matches. | Pending rerun. |
| `02-b` | accepted | `0.993` | ASR preserved the Markdown-report format, Mermaid/source figure list, scroll-pacing guidance, inspectable output, and reviewable workflow/scope-control point. Minor wording shift: `That format matters` heard as `But format matters`. | Shorter scope phrase removed the `role/rule` homophone risk. | Kept repaired text. | Chunk `02` accepted by Breeze-ASR-25 gate. |

## Chunk `03` Repair History

| Attempt | Result | ASR ratio | Main mismatch | Likely cause | Repair | Effect |
| --- | --- | ---: | --- | --- | --- | --- |
| `03-a` | rejected | `0.978` | `A. S. R.` was heard as separated `A` and `R`, with the `S` missing. | Letter-by-letter acronym remains unstable in the cloned voice. | Removed spoken acronym from chunk `03`; use `Automatic speech recognition` and `speech recognition` instead. | Pending rerun. |
| `03-b` | machine accepted but manually blocked | `0.971` | Final sentence changed from `ready for review, not automatically ready for medical action` to `ready for medical action`. | Negation and scope-control phrase was too compressed, and the gate did not yet treat negation loss as critical. | Added negation/scope-control critical phrases to `chunk_asr_qa.py`; rewrote as two sentences: `ready for staff review` and `not ready for automatic medical action`. | Pending rerun. |
| `03-c` | rejected | `0.948` | Negation phrase passed, but `clinician ready summary` was heard as `Acredition Ready summary`; large-language-model definition dropped `means a model`. | Dense definition sentence and `clinician ready` phrase were unstable. | Rewrote as shorter sentences: `A large language model can...`; replaced `clinician ready summary` with `summary for clinicians`. | Pending rerun. |
| `03-d` | rejected | `0.957` | `not ready for automatic medical action` was again heard as positive `ready for automatic medical action`; `transform language` heard as `transfer language`. | The TTS voice swallowed the negation before `ready`; `transform` and `transfer` were too close acoustically. | Rewrote the scope control as command-form `Do not use it for automatic medical action`; changed `transform language` to `work with language`; added this command phrase to the critical gate. | Pending rerun. |
| `03-e` | machine accepted but manually blocked | `0.984` | Scope-control ending passed, but ASR omitted `rejected` from `accepted, edited, rejected, or used...`. | The four-item list was compressed and the reject option was swallowed. | Split into short staff-action sentences and added `staff can reject it` to the critical gate. | Pending rerun. |
| `03-f` | rejected | `0.966` | `Previsit intake` heard as `Pre-usage intake`; `A summary for clinicians` heard as `His summary for clinicians`; `before and during` compressed into `beforehand during`. | `Previsit` and opening article `A` were unstable; timing phrase was too compressed. | Rewrote as `Before visit intake`; changed `A summary` to `This summary`; expanded timing to `before the visit and during the visit`. | Pending rerun. |
| `03-g` | rejected | `0.969` | Tail scope-control phrase fused into `It is ready for somatic medical action`. | Tail-position negation and `staff review / automatic medical action` blended together. | Rewrote as affirmative scope-control: `Staff review comes first. Automatic medical action is outside the scope.` Added both phrases to the critical gate. | Pending rerun. |
| `03-h` | accepted | `0.997` | ASR preserved definitions for speech recognition, large language model, before-visit intake, staff review support, rejectability, and medical-action scope control. | Short declarative sentences and affirmative scope-control wording were stable. | Kept repaired text. | Chunk `03` accepted by Breeze-ASR-25 gate. |

## Chunk `04` Repair History

| Attempt | Result | ASR ratio | Main mismatch | Likely cause | Repair | Effect |
| --- | --- | ---: | --- | --- | --- | --- |
| `04-a` | machine accepted but manually blocked | `0.976` | `less attention remains` heard as `unless attention remains`, reversing the workflow-burden meaning. | The phrase `and less` blended into `unless`. | Rewrote as two sentences: `Documentation and follow up burden increase. This leaves less attention for high value clinical judgment.` | Pending rerun. |
| `04-b` | rejected | `0.955` | `workflow` heard as `word flow`; `under time pressure and in fragments` heard as `time pressured and fragments`; `whether recently means` heard as `what a recently means`. | Dense workflow and timing phrases were unstable. | Rewrote as `real intake workflow problem`, `with time pressure and many fragments`, and kept `whether recently means` in a simpler sentence. | Pending rerun. |
| `04-c` | machine accepted but manually blocked | `0.976` | `say something happened recently` heard as `see something happened recently`; `whether recently means` still unstable; `cleaner intake surface` heard as `clear intake surface`. | `say/see` and `whether recently` were acoustically fragile. | Rewrote as `report a recent event, but not explain the date`; changed final phrase to `clear intake surface`. | Pending rerun. |
| `04-d` | machine accepted but manually blocked | `0.993` | Date example repeated `last week, last week`. | Short list item repeated during synthesis/ASR. | Rewrote date examples as `one day ago, one week ago, or two months ago`. | Pending rerun. |
| `04-e` | accepted | `1.000` | ASR preserved the intake workflow problem, fragmented patient story, date ambiguity, Mermaid diagram explanation, documentation burden, and clear-intake-surface point. | Numeric-style date examples were more stable than repeated calendar phrases. | Kept repaired text. | Chunk `04` accepted by Breeze-ASR-25 gate. |

## Chunk `05` Repair History

| Attempt | Result | ASR ratio | Main mismatch | Likely cause | Repair | Effect |
| --- | --- | ---: | --- | --- | --- | --- |
| `05-pre` | preventive text repair before generation | `n/a` | Source text contained `A. S. R.` and `clinician-ready previsit summary`, both known unstable patterns from chunks `01-04`. | Letter acronyms and `previsit` phrasing repeatedly caused ASR/TTS mismatch. | Rewrote to `speech recognition transcript`, `summary for clinicians before the visit`, and `Speech recognition listens and transcribes`. | Pending first generation. |
| `05-a` | rejected | `0.963` | `structured review draft` heard as `structured preview draft`; `medication and allergy mentions` heard as `medication anthology mentions`; `Only after review do` heard as `Only after review due`; `listens and transcribes` heard as `written and transcribed`. | Dense noun phrases and `do/due`, `allergy/anthology`, `listens/written` were unstable. | Rewrote as `structured draft for review`; split medication and allergy into separate list items; moved `only after staff review` to sentence end; changed `listens and transcribes` to `transcribes speech into text`. | Pending rerun. |
| `05-b` | machine accepted but manually blocked | `0.983` | Opening `speaking than by` heard as `speaking them by`; final `review and correct` heard as `review incorrect`. | `than by` and `and correct` were phonetically unstable, and `incorrect` reverses the final staff-review meaning. | Marked the chunk rejected; rewrote opening as `speaking is easier than filling out`; rewrote final sentence as `Clinical staff check and correct the draft`; added that phrase to the critical gate. | Pending rerun. |
| `05-c` | rejected by threshold only | `0.969` | ASR preserved the full workflow meaning and staff-review control, but compressed `A transcript is better, but it can still be...` into `It tends to be...`. | The shorter spoken sentence was semantically acceptable and more stable than the original comparative sentence. | Updated source text to match the stable spoken sentence: `It tends to be long, messy, and uncertain`; no audio regeneration needed before rerunning ASR gate. | Pending rerun. |
| `05-d` | accepted | `1.000` | ASR preserved speech-to-summary motivation, structured draft for review, speech recognition transcript, uncertainty marking, structured fields, staff review, bounded roles, and clinical staff correction. | Aligning the source text to the stable spoken sentence removed the last threshold mismatch. | Kept repaired text and accepted marker. | Chunk `05` accepted by Breeze-ASR-25 gate. |

## Chunk `06` Repair History

| Attempt | Result | ASR ratio | Main mismatch | Likely cause | Repair | Effect |
| --- | --- | ---: | --- | --- | --- | --- |
| `06-pre` | preventive text repair before generation | `n/a` | Source text contained `A. S. R.`, `previsit`, `speech-to-note`, and `clinical decision-making`, all known risk forms for this voice/gate. | Acronyms, hyphenated terms, and compressed clinical phrases repeatedly caused mismatch in earlier chunks. | Rewrote to `speech recognition`, `before visit intake support`, `speech to note`, and `clinical decision making`; capitalized initial `Artificial intelligence`. | Pending first generation. |
| `06-a` | machine accepted but manually blocked | `0.983` | `reviewable intake surface` heard as `reviewable intake service`; `fluent clinical text` heard as `fluid clinical text`; risk-task list compressed awkwardly. | `surface/service` and `fluent/fluid` were acoustically fragile; long task list made punctuation boundaries weak. | Marked rejected; rewrote as `review screen for intake`, `clear clinical text`, and split documentation/intake support from decision making, triage, and treatment planning. Added final-authority phrases to critical gate. | Pending rerun. |
| `06-b` | rejected | `0.951` | `speech to note` heard as `speech to no`; `realism` heard as `realis`; documentation/intake support sentence collapsed into `Documentation supporting before visit intakes report...`; `next two papers` lost `two`. | Abstract noun sequence and hyphen-like phrase were unstable. | Rewrote as shorter spoken units: `speech into notes direction practical`; `practical use`; separate sentences for documentation support, intake support, and higher-risk tasks. | Pending rerun. |
| `06-c` | rejected by source/export audit | `0.843` | Generated audio still reflected old exported chunk text after the tracked source had already been repaired. | The ignored `exports/.../chunk-text/` file was stale, so generation consumed old wording. | Reran `export_tts_chunks.py` before regeneration and checked the exported chunk text against the tracked source. | Prevented stale-source regeneration from being mistaken for a model-quality failure. |
| `06-d` | machine accepted but manually blocked | `0.990` | `speech into notes practical` was heard as `speech into those practical use`. | `notes practical` did not provide enough local semantic context and blurred across the sentence boundary. | Rewrote as `Turning speech into clinical notes is practical.` | Evidence-landscape sentence became clearer in the next run. |
| `06-e` | machine accepted but manually blocked | `0.987` | `Ambient artificial intelligence scribes can generate...` was heard as `Ambient artificial intelligence scripts in generate...`. | `scribes can` was phonetically fragile in the cloned voice. | Rewrote to `Ambient artificial intelligence tools can generate...`. | The documentation-tool sentence became stable. |
| `06-f` | machine accepted but manually blocked | `0.993` | `Triage and treatment planning` was heard as `Tried-and-treatment planning`. | The paired clinical task phrase was too compressed. | Split into `Triage is also a higher risk task.` and `Treatment planning is also a higher risk task.` | Clinical task boundaries became stable. |
| `06-g` | rejected by critical phrase gate | `0.981` | `final clinical authority` was heard as `vital clinical authority`; `clear clinical text` was heard as `clear clinical tests`; `speech recognition and large language models` collapsed into `speech recognition in large language models`. | Authority phrase, `text/tests`, and long conjunctions were unstable. | Rewrote to `clear clinical writing`, split speech-recognition and large-language-model placement into separate sentences, replaced authority wording with `They should not make final care decisions`, and added that phrase to the critical gate. | Pending rerun. |
| `06-h` | accepted | `0.984` | ASR preserved the evidence-landscape setup, clinical-notes direction, safety boundary, documentation/intake support split, clinical decision making, triage, treatment planning, review screen for intake, and final-care-decision scope control. Minor non-critical shifts remained: `workflow` singular, omitted articles, and `next papers` for `next two papers`. | Local context and text-prosody repairs stabilized the meaning-critical phrases. | Kept repaired text and accepted marker. | Chunk `06` accepted by Breeze-ASR-25 gate; next production gate is chunk `07`. |

## Important Additions We Must Keep

- `Gate score is not enough`: a high ASR ratio can still hide a meaning-changing phrase. Any phrase that changes clinical meaning must trigger repair even if the gate passes.
- `Critical phrase list`: maintain a chunk-specific list for terms that must be preserved, including scope-control phrases, clinical responsibility phrases, and report title terms.
- `Version trace`: every regenerated chunk must keep the ASR report, decision marker, and repair plan for auditability.
- `No silent overwrite`: if a chunk is regenerated after acceptance, rerun ASR and replace the decision marker with the new result.
- `Visual identity fallback`: student ID and full name can remain in the Markdown report / Padlet text if spoken TTS makes them unstable.
- `Disclosure`: final recording notes should disclose that narration was generated with Jason-authorized voice cloning for a course report.
- `Stop rule`: if the same chunk fails after repeated wording simplification, switch that chunk to real-voice fallback rather than endlessly tuning text.
- `ASR context window`: when a chunk is short or semantically dense, ASR needs local before-and-after context. Add a setup sentence or consequence sentence around high-risk terms before lowering thresholds.
- `Text prosody`: encode `抑、揚、頓、挫` with supported text structure: short sentences, commas, clear pause boundaries, and standalone scope-control statements.
- `Context repair before synonym churn`: if ASR confuses `surface/service`, `fluent/fluid`, `review/preview`, or similar pairs, first add meaning context around the phrase. Do not keep swapping synonyms without giving ASR a clearer local semantic frame.
