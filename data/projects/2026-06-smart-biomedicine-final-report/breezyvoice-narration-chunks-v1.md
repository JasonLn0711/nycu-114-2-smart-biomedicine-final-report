# BreezyVoice Narration Chunks v1

Purpose: hold the active BreezyVoice 26 narration source for the Smart Biomedicine final report after the TTS route moved away from GPT-SoVITS.

Canonical report surface: `markdown-report-v1.md`
Base English script: `markdown-report-20min-script-v2.md`
Legacy chunk source: `gpt-sovits-narration-chunks-v1.md`
Active artifact root: `exports/smart-biomedicine-breezyvoice/`
Runtime rule: RTX `5080` CUDA only; no CPU fallback and no non-5080 fallback.

## FIRST PRINCIPLE

Scarce resource: credible clinical-boundary meaning in the spoken English report, not fast chunk count.

Chunk `01` is the production gate. The system should not generate chunk `02` until chunk `01` has a BreezyVoice-specific WAV, a `breeze-asr-25` CUDA transcript report, and a semantic sweep that preserves:

- patient speech becomes a draft summary before the visit,
- artificial intelligence does not act as a doctor,
- human staff check the draft,
- the draft is checked before any care decision,
- the doctor keeps final authority,
- no system diagnosis, automatic scoring, patient priority decision, or treatment recommendation.

## Chunk Manifest

| Chunk | Markdown screen position | Planned WAV | BreezyVoice status |
| --- | --- | --- | --- |
| `sbm_tts_01_opening` | Title, report identity, core question | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_01_opening.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_02_markdown_format` | How to present this Markdown report | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_02_markdown_format.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_03_definitions` | Key definitions table | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_03_definitions.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_04_workflow_problem` | Real workflow problem and first Mermaid diagram | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_04_workflow_problem.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_05_speech_to_summary` | Speech-to-summary Mermaid architecture | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_05_speech_to_summary.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_06_evidence_landscape` | Evidence landscape | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_06_evidence_landscape.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_07_hager_boundary` | Hager et al. source figure | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_07_hager_boundary.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_08_lang1_overview` | Lang1 overview figure | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_08_lang1_overview.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_09_lang1_results` | Lang1 zero-shot and finetuning figures | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_09_lang1_results.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_10_architecture` | Proposed system architecture Mermaid diagram | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_10_architecture.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_11_scope_controls` | May-do and must-not-do lists | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_11_scope_controls.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_12_synthetic_example` | Synthetic example output table | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_12_synthetic_example.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_13_validation_risk` | Validation path and risk matrix | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_13_validation_risk.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |
| `sbm_tts_14_closing` | Final takeaway and references | `exports/smart-biomedicine-breezyvoice/chunks/sbm_tts_14_closing.wav` | accepted through RTX `5080` generation, Breeze-ASR-25 CUDA gate, and semantic sweep |

## TTS Chunks

### sbm_tts_01_opening

- Markdown position: title, report identity, core question, one-sentence thesis.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_01_opening.wav`.
- Repair basis: previous BreezyVoice pass confused `staff review`, `transcribed`, `summarized`, `care`, and `practical process`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
Hello everyone. I am Jason.

Today my report is about patient voice intake before a clinical visit.

The goal is to turn patient speech into a clear draft summary for a clinician.

This report asks one question.

Can patient speech become useful before the visit, without asking artificial intelligence to act like a doctor?

My answer is yes.

This only works with a clear boundary.

Automatic speech recognition turns speech into written text.

A large language model can organize that text into a draft.

The draft is not final.

Human staff check the draft before the visit.

Human staff can correct it.

Human staff can ask follow up questions.

Human staff can reject it.

The draft is checked before any care decision.

The doctor keeps the final authority.

This is the main boundary of the report.

I am not asking the system to make a diagnosis.

I am not proposing automatic scoring.

I am not deciding patient priority.

I am not proposing a treatment recommendation.

I am proposing a step by step process.

The system creates a review screen.

Human staff check the screen.

The doctor makes the medical decision.
```

### sbm_tts_02_markdown_format

- Markdown position: `How To Present This Markdown Report`.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_02_markdown_format.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
This report is not designed as a slide deck.

It is designed as one scrollable Markdown report.

The format is important.

A slide deck can hide the connection between sections.

The Markdown page keeps the full argument visible.

It contains source figures from the selected papers.

It contains a proposed architecture.

It contains a synthetic example.

It contains a validation plan and a risk matrix.

During the video, the screen should not move too quickly.

Each source figure needs enough time for the audience to see what it is doing.

The narration explains each figure.

The video stops for a moment before moving to the next section.

This also matches the system I propose.

The output should be clear and linear.

The output should be easy to check.

The output should be easy to correct.

The goal is not a polished black box.

The goal is to make the clinical process easy to see.

The goal is to make the scope controls easy to review.
```

### sbm_tts_03_definitions

- Markdown position: `Key Definitions` table.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_03_definitions.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
Let me define the main terms before the architecture.

Automatic speech recognition converts spoken language into text.

In this report, speech recognition is a transcription layer.

It is not clinical judgment.

A large language model can organize, summarize, and work with language.

In this report, the large language model structures information.

It does not become the clinical authority.

Pre visit intake means collecting information before a clinic visit.

This matters because the visit depends on information that is ready before and during the visit.

Staff review support means generated content must be checked by clinical staff.

The artificial intelligence output is not final.

Staff can accept it.

Staff can edit it.

Staff can reject it.

Staff can use it to ask follow up questions.

This summary for the doctor is a concise intake note.

It helps the doctor see the patient story, missing fields, and uncertainty.

Staff review comes first.

The system does not take medical action by itself.
```

### sbm_tts_04_workflow_problem

- Markdown position: `The Real Workflow Problem` and first Mermaid diagram.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_04_workflow_problem.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
Now I will move to the real intake problem.

Useful clinical decisions require a clear patient story.

This sounds simple.

But in real practice, the story often arrives with time pressure and many findings.

A patient may describe symptoms in the wrong order.

A patient may forget medication names.

A patient may report a recent event, but not explain the date.

The date may be one day ago, one week ago, or two months ago.

Patient concern becomes a messy broken story.

The story may be missing timeline, medication details, severity, or context.

Then the doctor must reconstruct the story during a short clinic visit.

Documentation and follow up burden increase.

This leaves less attention for high value clinical judgment.

The key point is that the bottleneck appears before the doctor makes a diagnosis.

The first useful artificial intelligence target is not replacing the doctor.

It is creating a clear intake surface before the appointment.
```

### sbm_tts_05_speech_to_summary

- Markdown position: `Why Speech-To-Summary Is Attractive` and second Mermaid diagram.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_05_speech_to_summary.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
Speech is natural for patients.

Many patients can speak more easily than they can use a long form.

But raw speech is not enough.

A recording is hard to review.

The output is a review chart.

A guided voice session becomes a transcript.

The transcript becomes a review chart.

The model organizes the draft.

The output goes to staff review.

It becomes a reviewed summary only after staff review.
```

### sbm_tts_06_evidence_landscape

- Markdown position: `Evidence Landscape`.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_06_evidence_landscape.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
This idea connects to current healthcare artificial intelligence.

Documentation tools are already entering clinical work.

Ambient artificial intelligence tools can generate clinical notes from spoken clinical encounters.

Turning speech into clinical notes is practical.

Even practical systems need a safety boundary.

Documentation support is one task.

Intake support before the visit is another task.

Clinical decision making is a higher risk task.

Patient priority is also a higher risk task.

Making a treatment plan is also a higher risk task.

The design question is not only whether a large language model can create clinical writing.

The better question is where speech recognition systems should sit in clinical work.

The next question is where large language model systems should sit, and what they should be allowed to own.

The safe answer is practical.

They should prepare a review screen for intake.

They should not make final care decisions.

This is why the next two papers are important for the report.
```

### sbm_tts_07_hager_boundary

- Markdown position: `Source Figure 1 - Hager et al. Boundary Paper`.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_07_hager_boundary.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
The first source figure is the title page of the Hager and colleagues paper in Nature Medicine.

The title is Evaluation and mitigation of the limitations of large language models in clinical decision making.

This is the boundary setting paper for my report.

Its value is that it explains why large language models should not act as autonomous clinical decision makers in realistic clinical work.

Clinical decision making requires information gathering.

It requires guidance.

It requires awareness of uncertainty.

Medical text alone is not enough.

For my report, this paper supports a positive scope control.

We can use large language models for structural support with human review.

But the system must not make final diagnoses.

It must not decide which patient goes first.

It must not prescribe treatment.

It must not skip clinical review.
```

### sbm_tts_08_lang1_overview

- Markdown position: `Source Figure 2 - Lang1 Overview`.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_08_lang1_overview.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
The second source figure comes from a paper about hospital operations.

The paper argues that broad foundation models are not enough for hospital operations.

This overview figure shows a full cycle modeling pipeline.

It includes clinical text training.

It includes next token prediction.

It includes model comparison.

It includes ablation studies across data mix, model scale, task type, hospital, and time.

For this report, the point is not that I need to build that model.

The point is that healthcare tools need design for the real world.

A broad model may be powerful.

But hospital operations need local context.

An intake system should be tested on its real job.

Can it transcribe faithfully?

Can it organize faithfully?

Can it find missing fields?

Can it keep uncertainty?

Can staff correct it?

Is it useful in daily work?
```

### sbm_tts_09_lang1_results

- Markdown position: `Source Figure 3` and `Source Figure 4`.
- Target visual hold: `90s`.
- Planned WAV: `chunks/sbm_tts_09_lang1_results.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
The next source figures compare basic use and task adaptation.

The first point is simple.

General language ability alone is limited.

Without adaptation and evaluation, tasks can fail in clinical operations.

Training and testing should match the real task.

The benchmark name is not the center.

The lesson is this.

If the system becomes real, it should not stay as a simple demo.

It should use supervision now.

They should choose training for the real task to help.

It should use validation over time.

It should use human review.

The validation point comes next.

```

### sbm_tts_10_architecture

- Markdown position: `Proposed System Architecture` Mermaid diagram.
- Target visual hold: `90s`.
- Planned WAV: `chunks/sbm_tts_10_architecture.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
Now I will walk through the proposed system architecture.

The process begins with patient consent.

The patient should know that their voice will be used to create a visit summary for clinical team review.

Next, the patient completes a guided voice interview.

The questions can be simple.

What is your main concern today?

When did it start?

What makes it better or worse?

Are you taking any medications?

Do you have allergies?

What are you most worried about?

The speech recognition system then creates a transcript.

If a drug name, number, or time phrase is unclear, the transcript should mark that uncertainty.

The large language model creates a structured draft and a list of missing questions.

Then clinical staff check the draft.

Staff can accept it with edits.

Staff can ask follow up questions.

Staff can reject the draft.

This decision point is the safety center of the architecture.

The system is useful because it is reviewable and rejectable.
```

### sbm_tts_11_scope_controls

- Markdown position: `What The System May Do` and `What The System Must Not Do`.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_11_scope_controls.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
This section defines what the system may do, and what it must not do.

The system may convert patient voice into a transcript.

It may mark unclear words.

It may structure the patient story into fields.

It may generate missing questions.

It may produce a draft that staff can inspect, correct, accept, or reject.

But the system must not make a final diagnosis.

It must not decide which patient goes first.

It must not prescribe treatment.

It must not skip clinical review.

It must not use real patient data in this course example.

It must not hide uncertainty behind smooth language.

This is a responsible design.

Clinical responsibility stays where it belongs.
```

### sbm_tts_12_synthetic_example

- Markdown position: `Synthetic Example Output` table.
- Target visual hold: `75-90s`.
- Planned WAV: `chunks/sbm_tts_12_synthetic_example.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
Now let me explain the example table.

This example is fictional.

It is included only to show the intended output shape.

Imagine a patient who reports recurring dizziness before a clinic visit.

The symptom started about two weeks ago.

It happens when the patient stands up quickly.

The patient is worried about going to work.

The medication name is unclear in the audio.

A bad artificial intelligence system might produce a confident diagnosis.

That is not what I propose.

A useful system should produce a review draft.

Staff can inspect and correct the draft.

It should list the chief concern.

It should list the symptom timeline.

It should list the patient concern.

It should list the uncertainty flag.

It should list missing questions.

The missing questions are important.

Staff may need to ask how long each episode lasts.

Staff may also ask about chest pain, shortness of breath, headache, or fainting.

Showing uncertainty supports safety.
```

### sbm_tts_13_validation_risk

- Markdown position: `Validation Path` Mermaid diagram and `Risk And Scope-Control Matrix`.
- Target visual hold: `90s`.
- Planned WAV: `chunks/sbm_tts_13_validation_risk.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
To make the system trustworthy, I use five checks.

Check one is the speech recognition check.

It checks medicine names, symptom time, dose, numbers, and negation.

Check two is summary accuracy.

The draft must match the transcript.

It keeps empty fields and uncertain words visible.

Check three is review.

Staff can accept, change, reject, or rewrite each part.

Check four is clinical process.

We ask whether it reduces lost information, repeated questions, and documentation burden.

Check five is governance.

We record what data is allowed.

We record patient privacy rules.

We keep review notes.

Each check keeps the system testable.
```

### sbm_tts_14_closing

- Markdown position: `Final Takeaway` and `References`.
- Target visual hold: `60-75s`.
- Planned WAV: `chunks/sbm_tts_14_closing.wav`.
- QA status: `[x] generated on RTX 5080` `[x] breeze-asr-25 CUDA gate passed` `[x] semantic sweep passed` `[x] accepted`

```text
Let me close with the final takeaway.

Speech recognition plus a large language model is most useful when it prepares a better clinical review surface before the visit.

This safe product is not an autonomous doctor.

Before the visit, staff review comes first.

The system can transform patient information into a structured draft.

Clinical staff can inspect that information.

Staff can edit that information.

This design connects a real clinical bottleneck to a practical artificial intelligence architecture.

The system uses artificial intelligence for transcription, structuring, summarization, and missing question generation.

Doctors and nurses are in charge of diagnosis and treatment.

My final answer is this.

Patient information can become a clinical review summary.

Only staff review makes this design safe.

It should not be designed as an autonomous doctor.

After audio Q and A, the next step is recording the screen video and posting the final report to the class site.

Thank you for listening.
```
