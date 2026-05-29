# GPT-SoVITS Narration Chunks v1

Use this file to produce the Smart Biomedicine final-report narration with GPT-SoVITS. The chunks are rewritten for TTS: shorter sentences, clearer pauses, explicit figure cues, and pronunciation-safe technical terms.

Source report surface: `markdown-report-v1.md`
Source human script: `markdown-report-20min-script-v2.md`
Reference candidates: `reference-audio-candidates-v1.md`
Production runbook: `gpt-sovits-production-runbook-v1.md`
Target video: about `19-20` minutes after scroll pauses, figure holds, and stitched chunk gaps
TTS target speaking pace: about `125-135` words per minute
Chunk count: `14` chunks
Per-chunk target length: `120-220` words

## Voice And Reference-Audio Policy

- Use Jason's own voice, or a voice with explicit permission for this course report.
- Do not use a teacher, classmate, public figure, YouTuber, commercial speaker, or any voice that was not clearly authorized.
- Authorized local source voice: `/home/jnclaw/Downloads/260528_0839_record.mp3`.
  - Verified local audio metadata: MP3, `16 kHz`, mono, about `11:42.86`, `24 kb/s`.
  - Use this as the source pool for Jason's own voice. Do not feed the whole file blindly as one reference prompt.
- Preferred reference audio: clean English formal-presentation voice.
- Acceptable fallback reference audio: clean Chinese-English mixed formal-presentation voice.
- Avoid reference audio with casual chat style, fatigue, strong room noise, laughter, music, breath noise, long silences, or unstable microphone distance.
- Keep the reference transcript exact. If the reference audio says a word differently from the transcript, re-record or fix the transcript.

## Reference-Audio Preparation Plan

1. Listen to `/home/jnclaw/Downloads/260528_0839_record.mp3` and mark `3-5` candidate clean segments.
2. Prefer segments that are formal, stable in volume, close-mic, low-noise, and free of laughter, long pauses, filler, and heavy code-switching.
3. Export candidate references as WAV under `exports/smart-biomedicine-gpt-sovits/reference/`.
4. Keep one short prompt reference inside GPT-SoVITS's accepted `3-10` second range for zero-shot / prompt-mode tests.
5. Keep one longer clean set around `45-90` seconds only if few-shot adaptation is needed and the local GPT-SoVITS workflow supports it cleanly.
6. Write exact prompt text for every selected reference segment before synthesis.
7. Reject any reference segment whose transcript cannot be written exactly.

## Generation And Stitching Settings

- Required runtime: RTX 4090 GPU, `CUDA_VISIBLE_DEVICES=0`.
- CPU fallback is not allowed for GPT-SoVITS generation or ASR transcript checks.
- Local ASR transcript support may use `breeze-asr-25` through the verified CUDA runtime recorded in `reference-audio-candidates-v1.md`.
- Local GPT-SoVITS runtime is prepared at `/home/jnclaw/every_on_git_jnclaw/GPT-SoVITS`; use `gpt-sovits-production-runbook-v1.md` for the current CUDA library path and smoke-test command.
- Generate one WAV per chunk. Do not synthesize the full `20` minute report in one pass.
- Planned output folder: `exports/smart-biomedicine-gpt-sovits/chunks/`.
- Planned stitched output: `exports/smart-biomedicine-gpt-sovits/smart-biomedicine-final-report-narration-v1.wav`.
- Add `0.35-0.7` seconds of silence between stitched chunks.
- Use longer visual holds for diagrams and paper figures: at least `45-90` seconds on each Mermaid diagram or source figure while the corresponding chunk plays.
- Use the upper end of the target visual-hold ranges when the generated audio is short. The total target visual duration at the upper end is about `19` minutes before small transition delays, which keeps the final video near `19-20` minutes.
- Keep output format as WAV during QA and stitching. Export compressed audio only after the final review passes.

## Pronunciation Pass

Use these forms in TTS text when needed:

| Written term | TTS-safe form | QA target |
| --- | --- | --- |
| ASR | `A. S. R.` | individual letters, not one word |
| LLM | `large language model` | spoken phrase; avoids unstable acronym reading |
| EHR | `E. H. R.` | individual letters |
| Hager | `HAY-ger` | first syllable like "hay" |
| Jiang | `Jee-ang` | clear two-part pronunciation |
| Lang1 | `Lang One` | do not say "Lang won" too quickly |
| ReMedE | `Reh-Med-Ee` | three clear syllables |
| AUROC | `A. U. R. O. C.` | individual letters |
| SoVITS | `Soh-Vits` | avoid "so-vights" |
| Mermaid | `Mermaid` | normal English word |
| Padlet | `Pad-let` | two syllables |

## Audio QA Checklist

For every chunk, mark each item before stitching:

- [ ] No missing words.
- [ ] No repeated words or repeated phrases.
- [ ] No swallowed final words.
- [ ] Technical terms are pronounced acceptably.
- [ ] No sudden speed jump.
- [ ] No unwanted emotion drift.
- [ ] No metallic artifact, clipping, popping, or tail residue.
- [ ] Volume is consistent with nearby chunks.
- [ ] Chunk ending leaves enough space for a natural stitch.
- [ ] Visual scroll position matches the spoken content.

## Fallback Plan

If GPT-SoVITS is unstable, record Jason's own voice for Chunk `01` and Chunk `14`, then use GPT-SoVITS for the middle chunks only. This keeps the report identity clear and reduces the feeling of a fully synthetic presentation.

## Chunk Manifest

| Chunk | Markdown screen position | Estimated audio | Target visual hold | Planned WAV |
| --- | --- | ---: | ---: | --- |
| `sbm_tts_01` | Title, report identity, core question | `66s` | `60-75s` | `chunks/sbm_tts_01_opening.wav` |
| `sbm_tts_02` | How to present this Markdown report | `68s` | `60-75s` | `chunks/sbm_tts_02_markdown_format.wav` |
| `sbm_tts_03` | Key definitions table | `68s` | `75-90s` | `chunks/sbm_tts_03_definitions.wav` |
| `sbm_tts_04` | Real workflow problem and first Mermaid diagram | `66s` | `75-90s` | `chunks/sbm_tts_04_workflow_problem.wav` |
| `sbm_tts_05` | Speech-to-summary Mermaid architecture | `64s` | `75-90s` | `chunks/sbm_tts_05_speech_to_summary.wav` |
| `sbm_tts_06` | Evidence landscape | `61s` | `60-75s` | `chunks/sbm_tts_06_evidence_landscape.wav` |
| `sbm_tts_07` | Hager et al. source figure | `60s` | `75-90s` | `chunks/sbm_tts_07_hager_boundary.wav` |
| `sbm_tts_08` | Lang1 overview figure | `60s` | `75-90s` | `chunks/sbm_tts_08_lang1_overview.wav` |
| `sbm_tts_09` | Lang1 zero-shot and finetuning figures | `61s` | `90s` | `chunks/sbm_tts_09_lang1_results.wav` |
| `sbm_tts_10` | Proposed system architecture Mermaid diagram | `69s` | `90s` | `chunks/sbm_tts_10_architecture.wav` |
| `sbm_tts_11` | May-do and must-not-do lists | `61s` | `60-75s` | `chunks/sbm_tts_11_scope_controls.wav` |
| `sbm_tts_12` | Synthetic example output table | `69s` | `75-90s` | `chunks/sbm_tts_12_synthetic_example.wav` |
| `sbm_tts_13` | Validation path and risk matrix | `68s` | `90s` | `chunks/sbm_tts_13_validation_risk.wav` |
| `sbm_tts_14` | Final takeaway and references | `73s` | `60-75s` | `chunks/sbm_tts_14_closing.wav` |

## TTS Chunks

### sbm_tts_01_opening

- Markdown position: title, report identity, core question, one-sentence thesis.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_01_opening.wav`.
- Pronunciation notes: `A. S. R.`, `large language model`, `Pad-let`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
Hello everyone. I am Jason. Today my report topic is speech intake to clinician summary. The report uses speech recognition and large language models for a smart biomedical workflow before the visit.

This report starts from one question. Can patient speech become a useful summary for clinicians before the visit, without making the artificial intelligence system a doctor?

My answer is yes. This works only under a clear operating scope. Automatic speech recognition turns speech into text. Large language model systems can create the strongest near term value when they support staff review before the visit. Patient speech is transcribed, structured, and summarized before the visit. Then staff check and correct the output before it influences care.

This is the main boundary of the report. I am not proposing autonomous diagnosis, automatic priority scoring, or treatment recommendation. I am proposing a practical workflow: artificial intelligence prepares a clinician review screen, and human staff keep final authority.
```

### sbm_tts_02_markdown_format

- Markdown position: `How To Present This Markdown Report`.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_02_markdown_format.wav`.
- Pronunciation notes: `Mermaid`, `Markdown`, `artificial intelligence`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
This report is not designed as a slide deck. It is designed as a single scrollable Markdown report.

That format matters. A slide deck often hides the connections between sections. This Markdown page keeps the full argument visible. It contains definitions, Mermaid diagrams, source figures from the selected papers, a proposed architecture, a synthetic example, a validation path, and a risk matrix.

During the video, the screen should not move too quickly. Each diagram or source figure needs enough time for the audience to see what it is doing. The narration should explain the figure, then pause briefly before moving to the next section.

This is also similar to my proposed system. The output should be linear, inspectable, and correctable. The goal is not a polished black box. The goal is to make the clinical workflow, the job of artificial intelligence, and the scope controls easy to review.
```

### sbm_tts_03_definitions

- Markdown position: `Key Definitions` table.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_03_definitions.wav`.
- Pronunciation notes: `A. S. R.`, `large language model`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
Let me define the main terms before the architecture.

Automatic speech recognition converts spoken language into text. In this report, speech recognition is a transcription layer. It is not clinical judgment.

A large language model can organize, summarize, and work with language. In this report, the large language model structures information. It does not become the clinical authority.

Before visit intake means information collection before the patient meets the clinician. This matters because a clinical encounter depends heavily on the information available before the visit and during the visit.

Staff review support means generated content must be checked by clinical staff. The artificial intelligence output is not final. Staff can accept it. Staff can edit it. Staff can reject it. Staff can use it to ask follow up questions.

This summary for clinicians is a concise intake note. It helps the clinician see the patient story, missing fields, and uncertainty. Staff review comes first. Automatic medical action is outside the scope.
```

### sbm_tts_04_workflow_problem

- Markdown position: `The Real Workflow Problem` and first Mermaid diagram.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_04_workflow_problem.wav`.
- Pronunciation notes: `Mermaid`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
Now I will move to the real intake workflow problem.

Useful clinical decisions require a usable patient story. That sounds simple, but in real practice, the story often arrives with time pressure and many fragments. A patient may describe symptoms out of order. They may forget medication names. They may report a recent event, but not explain the date. The date may be one day ago, one week ago, or two months ago.

In the first Mermaid diagram, patient concern becomes a messy spoken story. The story may be missing timeline, medication, severity, or context. Then the clinician must reconstruct the story during a short visit. Documentation and follow up burden increase. This leaves less attention for high value clinical judgment.

The key point is that the bottleneck appears before diagnosis. The first useful artificial intelligence target is not replacing the doctor. It is creating a clear intake surface before the visit.
```

### sbm_tts_05_speech_to_summary

- Markdown position: `Why Speech-To-Summary Is Attractive` and second Mermaid diagram.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_05_speech_to_summary.wav`.
- Pronunciation notes: `A. S. R.`, `large language model`, `Mermaid`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
Speech to summary is attractive because speech is natural for patients. For many patients, speaking is easier than filling out a long form.

But raw speech is not enough. A recording is hard to scan. It tends to be long, messy, and uncertain. The useful output is a structured draft for review.

In the second Mermaid diagram, a guided patient voice intake becomes a speech recognition transcript. The transcript is cleaned and marked with uncertainty. Then a large language model structures the content into chief complaint, symptom timeline, medication mentions, allergy mentions, patient concerns, and missing questions.

These outputs then go to staff review. They become a summary for clinicians before the visit only after staff review. Each technology has a bounded role. Speech recognition transcribes speech into text. The large language model organizes and drafts. Clinical staff check and correct the draft.
```

### sbm_tts_06_evidence_landscape

- Markdown position: `Evidence Landscape`.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_06_evidence_landscape.wav`.
- Pronunciation notes: `artificial intelligence`, `large language model`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
This idea connects to current healthcare artificial intelligence. Documentation tools are already entering clinical workflows. Ambient artificial intelligence tools can generate draft clinical notes from spoken clinical encounters. Turning speech into clinical notes is practical.

Even practical systems need a safety boundary. Documentation support is one task. Intake support before the visit is another task. Clinical decision making is a higher risk task. Triage is also a higher risk task. Treatment planning is also a higher risk task.

The design question is not only whether a large language model can write clear clinical writing. The better question is where speech recognition systems should sit in the clinical workflow. The next question is where large language model systems should sit, and what they should be allowed to own.

My answer is narrow and practical. They should prepare a review screen for intake. They should not make final care decisions. This is why the next two papers are important for the report.
```

### sbm_tts_07_hager_boundary

- Markdown position: `Source Figure 1 - Hager et al. Boundary Paper`.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_07_hager_boundary.wav`.
- Pronunciation notes: `HAY-ger`, `A. S. R.`, `large language model`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
The first source figure is the title page of the HAY-ger and colleagues paper in Nature Medicine. The title is, Evaluation and mitigation of the limitations of large language models in clinical decision-making.

This is the boundary-setting paper for my report. It does not directly study A. S. R. or previsit intake. Its value is that it explains why large language models should not be framed as autonomous clinical decision-makers in realistic clinical workflows.

Clinical decision-making requires information gathering, guideline alignment, robustness, instruction following, awareness of uncertainty, and integration into real workflows. Fluent medical text is not enough.

For my report, this paper supports a positive scope control. We can use large language models for structured, clinician-reviewed support. But the system must not make final diagnoses, assign definitive triage acuity, prescribe treatment, or bypass clinical review.
```

### sbm_tts_08_lang1_overview

- Markdown position: `Source Figure 2 - Lang1 Overview`.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_08_lang1_overview.wav`.
- Pronunciation notes: `Jee-ang`, `Lang One`, `E. H. R.`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
The second source figure comes from the Jee-ang and colleagues Lang One paper, Generalist Foundation Models Are Not Clinical Enough for Hospital Operations.

This overview figure shows a full-cycle modeling pipeline. It includes clinical and web text pretraining, next-token prediction, instruction finetuning, comparison with generalist models, and ablation studies across data mix, model scale, task type, hospital, and time.

For this report, the point is not that I need to build Lang One. The point is that healthcare artificial intelligence needs workflow-specific design and evaluation.

A generic model may be powerful, but hospital operations and clinical workflows require domain context. A previsit intake system should therefore be evaluated on the actual job it claims to do. That means faithful transcription, faithful structuring, missing-field detection, uncertainty preservation, staff correction patterns, and workflow usefulness.
```

### sbm_tts_09_lang1_results

- Markdown position: `Source Figure 3` and `Source Figure 4`.
- Target visual hold: `90s`.
- Planned WAV: `chunks/sbm_tts_09_lang1_results.wav`.
- Pronunciation notes: `Lang One`, `Reh-Med-Ee`, `A. U. R. O. C.`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
The third and fourth source figures show the difference between zero-shot use and task-specific adaptation.

The zero-shot figure supports the claim that broad language ability is not enough. Both generalist and specialist models can underperform when directly applied to clinical operations tasks without the right adaptation and evaluation.

The finetuning figure shows the forward path. Finetuned Lang One specialists can perform better on workflow-relevant Reh-Med-Ee tasks. The exact benchmark is not the center of my report. The lesson is the center.

If an A. S. R. plus large-language-model previsit intake system becomes a real clinical tool, it should not remain only a generic prompt demonstration. It should move toward supervised evaluation, workflow-specific training, temporal validation, and human review data.

This is why my proposal is an architecture and validation path, not a finished clinical product.
```

### sbm_tts_10_architecture

- Markdown position: `Proposed System Architecture` Mermaid diagram.
- Target visual hold: `90s`.
- Planned WAV: `chunks/sbm_tts_10_architecture.wav`.
- Pronunciation notes: `A. S. R.`, `large language model`, `Mermaid`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
Now I will walk through the proposed system architecture.

The workflow begins with patient consent. The patient should know that their voice will be used to create a previsit summary for staff review.

Next, the patient completes a guided voice interview. The questions can be simple. What is your main concern today? When did it start? What makes it better or worse? Are you taking any medications? Do you have allergies? What are you most worried about?

The A. S. R. system then creates a transcript. If a medication name, number, or time expression is unclear, the transcript should mark that uncertainty.

The large language model creates a structured intake draft and a missing-information question list. Then clinical staff review it. Staff can accept with edits, ask follow-up questions, or reject unsupported sections.

This decision node is the safety center of the architecture. The system is useful because it is reviewable and rejectable.
```

### sbm_tts_11_scope_controls

- Markdown position: `What The System May Do` and `What The System Must Not Do`.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_11_scope_controls.wav`.
- Pronunciation notes: `artificial intelligence`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
This section defines what the system may do, and what it must not do.

The system may convert patient voice into a transcript. It may mark uncertain words and unclear clinical entities. It may structure the patient story into intake fields. It may generate missing questions. It may produce a draft that staff can inspect, correct, accept, or reject.

But the system must not make a final diagnosis. It must not assign definitive triage acuity. It must not prescribe treatment. It must not bypass clinical staff review. It must not use real patient data in this course demo. It must not hide uncertainty behind fluent language.

This is not a weak design. This is a responsible design. The value comes from placing automation where it helps, while keeping clinical responsibility where it belongs.
```

### sbm_tts_12_synthetic_example

- Markdown position: `Synthetic Example Output` table.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_12_synthetic_example.wav`.
- Pronunciation notes: avoid making the example sound like medical advice.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
Now let me explain the synthetic example table. This example is fictional. It is included only to show the intended output shape.

Imagine a patient who reports recurring dizziness before a clinic visit. The symptom started about two weeks ago. It gets worse when standing quickly. The patient is worried because the episodes happened several times before work. The medication name is unclear in the audio.

A bad artificial intelligence system might produce a confident diagnosis. That is not what I propose.

A useful system should produce a structured review draft. It should list the chief concern, symptom timeline, patient concern, uncertainty flag, missing questions, and review status.

The missing questions are especially important. Staff may need to ask about episode duration, blood pressure history, recent medication changes, chest pain, shortness of breath, headache, or fainting.

The uncertainty flag is not a weakness. It is part of the safety design.
```

### sbm_tts_13_validation_risk

- Markdown position: `Validation Path` Mermaid diagram and `Risk And Scope-Control Matrix`.
- Target visual hold: `90s`.
- Planned WAV: `chunks/sbm_tts_13_validation_risk.wav`.
- Pronunciation notes: `A. S. R.`, `large language model`, `A. U. R. O. C.` if added verbally.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
To make the system trustworthy, we need layered validation.

The first layer is A. S. R. validation. We should not evaluate only general word error rate. We should evaluate clinically meaningful entity accuracy, including medication names, symptom duration, dosage, laterality, numbers, and negation.

The second layer is large language model structuring validation. We should measure faithfulness to the transcript, missing-field detection, hallucination rate, and whether uncertainty is preserved.

The third layer is human review validation. We should measure how often staff accept, correct, reject, or rewrite each section.

The fourth layer is workflow validation. We should ask whether the summary improves intake readiness, reduces information loss, reduces repeated questioning, or reduces documentation burden.

The fifth layer is governance validation. The system should track model version, prompt version, data scope, review responsibility, privacy rules, and audit trail.

Together, these controls turn the idea from a broad artificial intelligence promise into an evaluable smart-biomedicine workflow.
```

### sbm_tts_14_closing

- Markdown position: `Final Takeaway` and `References`.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_14_closing.wav`.
- Pronunciation notes: `A. S. R.`, `large language model`, `Pad-let`, `Soh-Vits`.
- QA status: `[ ] not generated` `[ ] generated` `[ ] listened` `[ ] accepted` `[ ] rejected`

```text
Let me close with the final takeaway.

A. S. R. plus a large language model is most useful in smart biomedicine when it prepares a better clinical review surface before the visit. The first responsible product shape is not an autonomous doctor. It is a staff-review previsit intake workflow that turns patient speech into structured, inspectable, and correctable information.

This design connects a real clinical bottleneck to a practical artificial intelligence architecture. It uses artificial intelligence for transcription, structuring, summarization, and missing-question generation. It keeps diagnosis, triage, and treatment under human clinical authority. It also defines validation layers before clinical expansion.

So my final answer to the opening question is yes. Patient speech can become a clinician-ready previsit summary, but only when the system is designed as reviewed workflow support, not as an artificial intelligence doctor.

After this narration passes the GPT, Soh-Vits audio QA checklist, the next step is recording the Markdown screen video and posting the final report to Pad-let.

Thank you for listening.
```
