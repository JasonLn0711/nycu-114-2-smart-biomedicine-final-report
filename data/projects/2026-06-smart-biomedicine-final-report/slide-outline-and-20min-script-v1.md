# Slide Outline And 20-Minute English Script v1

## Report Identity

- Course: `Introduction of Smart Biomedicine`
- Student: `Jason Chia-Sheng Lin`
- Student ID: `513559004`
- Topic: `From Speech Intake to Clinician Summary: ASR and LLMs for Smart Biomedical Pre-visit Workflows`
- Target runtime: about `20` minutes
- Production format: slide-supported video, uploaded to YouTube, then posted to Padlet
- Operating scope: course-level architecture and evidence-backed workflow proposal, not production medical software

## Concrete Production Plan

### Phase 1 - Build The Deck

Target output: `12` slides.

Recommended slide count and timing:

| Slide | Title | Target time | Main job |
| ---: | --- | ---: | --- |
| 1 | Title And Core Question | `1:00` | Introduce identity, topic, and guiding question. |
| 2 | The Missing Patient Story | `1:30` | Frame the real clinical workflow problem. |
| 3 | Documentation Competes With Clinical Attention | `1:30` | Show why the problem matters. |
| 4 | Why Speech-To-Summary Is Attractive | `1:30` | Explain why ASR plus LLM is a natural smart-biomedicine idea. |
| 5 | AI Scribes Are Already Entering Clinical Workflows | `1:45` | Show that the solution landscape already exists. |
| 6 | The Boundary: A Useful Assistant Is Not An Autonomous Doctor | `2:00` | Use Hager et al. to set the clinical decision-making boundary. |
| 7 | Why Generalist Models Are Not Enough | `1:45` | Use Jiang et al. / Lang1 to explain workflow-specific evaluation. |
| 8 | Proposed Architecture | `2:00` | Present the staff-review previsit intake support pipeline. |
| 9 | What The Output Should Look Like | `1:45` | Show a synthetic structured summary and missing-question list. |
| 10 | Where Errors Can Enter | `1:30` | Explain ASR, LLM, context, privacy, and review risks. |
| 11 | Validation Path | `1:45` | Show layered evaluation before clinical expansion. |
| 12 | Takeaway And References | `1:30` | Close with the thesis and reference list. |

Deck-building checklist:

- [ ] Create one clean title slide with name, student ID, course, and English topic.
- [ ] Add one workflow diagram: `patient speech -> ASR transcript -> LLM structured intake -> staff review -> clinician-ready summary`.
- [ ] Add one synthetic example slide. Use clearly fictional content only.
- [ ] Add one validation slide with five layers: ASR, LLM structuring, human review, workflow, governance.
- [ ] Add one reference slide with the main papers and supporting sources.
- [ ] Keep all report slides in English.
- [ ] Avoid claims of autonomous diagnosis, autonomous triage, treatment recommendation, or production clinical safety.

### Phase 2 - Rehearse And Tighten

Target output: a stable `19-20` minute recording.

- Run one full rehearsal with the script below.
- If the recording is over `21` minutes, shorten Slides 2, 5, and 9 first.
- If the recording is under `18` minutes, slow down on Slides 8 and 11 instead of adding new claims.
- Keep speaking pace around `125-135` words per minute.
- Keep the final spoken report entirely in English.

### Phase 3 - Record, Upload, And Close Gates

- Record the slide-supported video.
- Export the video file.
- Upload the video to YouTube.
- Post the YouTube link on Padlet with:

```text
Student ID: 513559004
Name: Jason Chia-Sheng Lin
Report title: From Speech Intake to Clinician Summary: ASR and LLMs for Smart Biomedical Pre-visit Workflows
```

- Capture upload evidence in the project tracker or daily note.
- Before `2026-06-17`, watch at least one classmate report, leave a comment or question, and give a like.
- Before `2026-06-20`, check Jason's own Padlet thread and answer questions.

## Slide-Level Content

### Slide 1 - Title And Core Question

On-slide bullets:

- From Speech Intake to Clinician Summary
- ASR and LLMs for Smart Biomedical Pre-visit Workflows
- Jason Chia-Sheng Lin, Student ID 513559004
- Core question: Can patient speech become a clinician-ready summary without making the AI the doctor?

Visual:

- Simple pipeline preview with five boxes.

### Slide 2 - The Missing Patient Story

On-slide bullets:

- Good clinical decisions need a usable patient story.
- Patient narratives are often incomplete, messy, and time-pressured.
- The first opportunity for AI support may be before the visit.

Visual:

- Patient story fragments flowing into a structured intake summary.

### Slide 3 - Documentation Competes With Clinical Attention

On-slide bullets:

- Clinical care includes both patient interaction and documentation work.
- EHR and inbox workload can reduce available attention.
- Smart biomedicine should improve workflow, not only model accuracy.

Evidence:

- Sinsky et al. on physician time allocation.
- Murphy et al. on EHR inbox notification burden.
- Hingle on the EHR promise and implementation challenge.

### Slide 4 - Why Speech-To-Summary Is Attractive

On-slide bullets:

- ASR can capture patient speech.
- LLMs can structure and summarize language.
- A previsit summary can make missing information visible.
- The value is a better review surface for clinical staff.

Visual:

- `voice -> transcript -> structured summary -> questions to ask`.

### Slide 5 - AI Scribes Are Already Entering Clinical Workflows

On-slide bullets:

- Ambient AI scribes can produce draft notes from spoken encounters.
- Early studies show workflow promise.
- The important question is where and how to place the AI in care.

Evidence:

- Ma et al. on LLM-powered ambient AI scribe adoption and documentation time.
- JGIM discussion of ambient listening technology for clinical notes.

### Slide 6 - The Boundary: A Useful Assistant Is Not An Autonomous Doctor

On-slide bullets:

- Summarizing intake is different from making medical decisions.
- Hager et al. evaluate LLM limits in clinical decision-making.
- The responsible scope is clinician-reviewed support.

Scope controls:

- No final diagnosis.
- No definitive triage.
- No treatment prescription.
- No bypassing clinical review.

### Slide 7 - Why Generalist Models Are Not Enough

On-slide bullets:

- Broad language ability is not the same as clinical workflow readiness.
- Hospital operations require domain knowledge and real-world evaluation.
- Domain adaptation and supervised evaluation matter.

Evidence:

- Jiang et al., `Generalist Foundation Models Are Not Clinical Enough for Hospital Operations`.

### Slide 8 - Proposed Architecture

On-slide bullets:

- Patient consent and guided previsit voice intake.
- ASR transcript with uncertainty markers.
- LLM structuring into intake fields.
- Missing-information question list.
- Staff review and correction.
- Clinician-ready previsit summary.

Visual:

```text
Patient speech
-> ASR transcript
-> uncertainty markers
-> LLM structured intake
-> missing-question list
-> staff review
-> clinician-ready summary
```

### Slide 9 - What The Output Should Look Like

On-slide bullets:

- Structured chief complaint.
- Symptom timeline.
- Medication and allergy mentions.
- Patient concerns.
- Missing questions.
- Uncertainty flags.

Synthetic example:

```text
Chief concern: recurring dizziness before clinic visit.
Timeline: started about two weeks ago; worse when standing quickly.
Uncertainty: medication name unclear in audio.
Missing questions: duration of each episode, blood pressure history, recent medication changes.
Review status: staff review required before clinical use.
```

### Slide 10 - Where Errors Can Enter

On-slide bullets:

- ASR may misrecognize drug names, numbers, negation, or timing.
- LLMs may over-summarize or infer unsupported details.
- Patient speech may omit clinically important context.
- Privacy, consent, audit trail, and responsibility must be explicit.

### Slide 11 - Validation Path

On-slide bullets:

- ASR layer: clinically meaningful entity accuracy.
- LLM layer: correctness, missing-field detection, hallucination rate.
- Human review layer: correction, rejection, and acceptance patterns.
- Workflow layer: intake time, information loss, documentation burden.
- Governance layer: versioning, prompt, model, data scope, audit trail.

### Slide 12 - Takeaway And References

On-slide takeaway:

- ASR plus LLM is valuable when it creates a reviewable clinical surface.
- The first responsible product shape is staff-review previsit intake support.
- Smart biomedicine should combine useful automation with clear validation layers.

Core references:

- Hager et al., `Evaluation and mitigation of the limitations of large language models in clinical decision-making`, Nature Medicine, 2024.
- Jiang et al., `Generalist Foundation Models Are Not Clinical Enough for Hospital Operations`, arXiv, 2025.
- Sinsky et al., physician time allocation and EHR burden.
- Ma et al., LLM-powered ambient AI scribe in an academic medical center.
- Murphy et al., EHR inbox notification burden.
- Hingle, EHR promise and call to action.

## Full English Speaking Script

### Slide 1 - Title And Core Question

Hello everyone. My name is Jason Chia-Sheng Lin, and my student ID is 513559004. Today my report topic is: From Speech Intake to Clinician Summary: ASR and LLMs for Smart Biomedical Pre-visit Workflows.

The core question of this report is simple: can we turn patient speech into a useful clinician-ready summary without pretending that the AI is the doctor?

This question is important because smart biomedicine is not only about building powerful models. It is also about placing those models in the right part of a healthcare workflow. A model can be technically impressive, but if it is used in the wrong position, it can create risk. On the other hand, if we design the workflow carefully, AI can support clinicians by reducing information loss, preparing better context, and making review easier before the patient enters the consultation room.

My main argument is that ASR and LLM systems can create value in smart biomedicine when they are designed as staff-review intake support. In this role, patient speech is transcribed, organized, and summarized before the visit. Then clinical staff review and correct the output before it influences care.

### Slide 2 - The Missing Patient Story

Let me start from the clinical workflow problem.

Before a physician can make a good decision, the system first needs a usable patient story. That sounds obvious, but in real clinical practice, the patient story is often incomplete, messy, or scattered. A patient may describe symptoms out of order. They may forget the exact medication name. They may say that a symptom happened recently, but not specify whether recently means two days, two weeks, or two months. They may mention a serious clue casually near the end of the conversation.

This is not a small problem, because clinical reasoning begins with information gathering. If the initial story is unclear, the physician or clinical staff must spend time reconstructing the timeline, checking missing details, and separating important signals from noise.

So the first opportunity for AI support may not be autonomous diagnosis. A more practical first opportunity is earlier and narrower: help create a cleaner, reviewable patient story before the visit.

In other words, the goal is not to replace the clinical encounter. The goal is to prepare a better surface for that encounter.

### Slide 3 - Documentation Competes With Clinical Attention

The second reason this topic matters is documentation burden.

Clinical care does not happen only through face-to-face conversation. It also includes EHR documentation, inbox work, chart review, order entry, and follow-up tasks. Sinsky and colleagues studied physician time allocation in ambulatory practice and reported that physicians spent a large share of their work time on EHR and desk work. Other studies and commentaries also describe EHR inbox notifications and documentation burden as major sources of clinical workload.

For smart biomedicine, this means that we should not only ask whether an AI model can answer a medical question. We should ask whether it improves the actual workflow. Does it reduce unnecessary reconstruction work? Does it help clinicians see the patient story earlier? Does it make missing information visible? Does it preserve time and attention for the parts of care that require professional judgment?

This is why speech intake is interesting. Speech is natural for patients. Many patients can explain their concern more easily by talking than by filling out a long form. But raw speech is not yet clinically useful. It needs to be transcribed, structured, checked, and reviewed.

That is where ASR and LLMs become relevant.

### Slide 4 - Why Speech-To-Summary Is Attractive

ASR means automatic speech recognition. It can convert spoken language into text. LLMs, or large language models, can process language, summarize content, extract structure, and generate organized text.

If we combine these two technologies, we get an attractive idea: patient voice can become a structured intake summary.

For example, a patient could answer guided previsit questions by voice. The ASR system creates a transcript. Then an LLM organizes the transcript into sections such as chief complaint, symptom timeline, medication mentions, allergies, prior history, and patient concerns. The system can also produce a list of missing questions, such as: How long does each episode last? Was there fever? Did the symptom happen on the left side or the right side? Was there any recent medication change?

This is attractive because the output is not just a paragraph. It can be a review surface. Clinical staff can check it, correct it, and decide what information should be carried into the visit.

So the value of the system is not that it gives a final answer. The value is that it prepares the right questions and organizes the patient story.

### Slide 5 - AI Scribes Are Already Entering Clinical Workflows

This idea is also realistic because AI documentation tools are already entering clinical workflows.

Ambient AI scribes are one example. These systems listen to clinician-patient conversations and generate draft clinical notes. Recent studies have reported promising workflow results, including adoption in real encounters and possible reductions in documentation time. Discussions in the medical literature also describe ambient listening technology as a generative AI approach for producing clinical notes from spoken conversation.

This matters for my report because it shows that speech-to-note is not science fiction. The healthcare system is already experimenting with this direction.

However, the existence of AI scribes does not automatically answer the design question. If AI can draft clinical notes, should it also make clinical decisions? If it can summarize a conversation, should it be trusted to triage a patient? If it can produce fluent text, does that mean it understands the workflow, the guideline, and the clinical responsibility?

My answer is no. These are different tasks. Documentation support, previsit intake support, clinical decision-making, triage, and treatment planning have different levels of risk. A responsible smart-biomedicine design must separate them.

That is why the boundary paper by Hager and colleagues is important.

### Slide 6 - The Boundary: A Useful Assistant Is Not An Autonomous Doctor

Hager and colleagues evaluated the limitations of large language models in clinical decision-making. The important lesson for this report is not that LLMs are useless. The lesson is that realistic clinical decision-making is much more demanding than fluent medical text generation.

Clinical decision-making requires information gathering, guideline alignment, robustness, instruction following, awareness of uncertainty, and integration into real workflows. A model may answer a medical exam question well, but still fail when the problem is incomplete, ambiguous, or embedded in a real clinical process.

This gives us a clear boundary for the ASR plus LLM report topic.

The system should not be framed as an autonomous doctor. It should not make a final diagnosis. It should not assign definitive triage acuity. It should not prescribe treatment. It should not bypass clinician review.

But this boundary does not make the idea weak. It actually makes the idea stronger. A well-scoped system can provide value by doing the work that fits its capability: transcribing speech, organizing information, preserving uncertainty, and preparing a clinician-reviewed summary.

The correct first product shape is not autonomous clinical decision-making. The correct first product shape is staff-review previsit intake support.

### Slide 7 - Why Generalist Models Are Not Enough

The second major reference is the work by Jiang and colleagues, titled Generalist Foundation Models Are Not Clinical Enough for Hospital Operations.

This paper supports another important point: broad language ability is not the same as clinical workflow readiness. Generalist foundation models can be very powerful, but hospital operations require domain-specific knowledge, temporal patterns, patient-flow context, EHR structure, and realistic evaluation.

For my report, the implication is clear. We should not treat a generic chatbot as a complete clinical system. If we want AI to support healthcare workflows, we need workflow-specific design and evaluation.

In a previsit intake system, the target is not simply to produce a nice summary. The target is to produce a summary that is faithful to the patient speech, useful for clinical review, clear about uncertainty, and safe within its operating scope.

This also means the evaluation should be practical. We should ask: Did the ASR system correctly capture medication names, symptom duration, negation, and numbers? Did the LLM preserve uncertainty instead of inventing certainty? Did clinical staff correct many fields? Did the workflow reduce information loss or documentation pressure?

These questions are more meaningful than asking only whether the model sounds fluent.

### Slide 8 - Proposed Architecture

Now I will present my proposed architecture.

The workflow begins with patient consent. The patient knows that their voice will be used to prepare a previsit summary for staff review.

Next, the patient completes a guided voice intake. This could be a simple set of questions, such as: What is your main concern today? When did it start? What makes it better or worse? Are you taking any medication? Do you have allergies? What are you most worried about?

Then the ASR system converts speech into a transcript. Importantly, the transcript should include uncertainty markers when the speech is unclear. For example, if a drug name is uncertain, the system should not hide that uncertainty.

After that, the transcript is cleaned and segmented. The LLM then transforms the transcript into structured intake fields. It can organize the chief complaint, symptom timeline, medication mentions, allergy mentions, relevant history, and patient concerns.

The system also creates a missing-information question list. This is one of the most useful outputs, because missing information is often what slows down the clinical encounter.

Finally, clinical staff review and correct the summary. Only after this review does the output become a clinician-ready previsit summary.

So the pipeline is: patient speech, ASR transcript, uncertainty markers, LLM structured intake, missing-question list, staff review, and clinician-ready summary.

### Slide 9 - What The Output Should Look Like

Let me show a simple synthetic example. This is not real patient data.

Suppose a patient says that they have been feeling dizzy, especially when standing up quickly. They think it started about two weeks ago, but they are not completely sure. They mention a medication name, but the audio is unclear. They are worried because the dizziness has happened several times before work.

A useful system should not produce a confident diagnosis. Instead, it should produce a structured review draft.

For example:

Chief concern: recurring dizziness before clinic visit.

Timeline: started about two weeks ago; worse when standing quickly.

Patient concern: worried about repeated episodes before work.

Uncertainty flag: medication name unclear in audio.

Missing questions: duration of each episode; blood pressure history; recent medication changes; associated symptoms such as chest pain, shortness of breath, headache, or fainting.

Review status: staff review required before clinical use.

This example shows the design principle. The system is useful because it organizes the story and reveals what needs checking. It does not cross the boundary into diagnosis or treatment.

### Slide 10 - Where Errors Can Enter

This architecture also has risks, and they should be visible.

First, ASR errors can matter clinically. A speech recognition system may misrecognize drug names, dosages, numbers, laterality, timing, or negation. For example, confusing "no chest pain" with "chest pain" would be dangerous. Therefore, clinically meaningful entity accuracy is more important than word error rate alone.

Second, LLMs can over-summarize. They may remove uncertainty, infer unsupported details, or make a story sound cleaner than it really is. In clinical work, a clean but unsupported summary can be more dangerous than a messy transcript, because it creates false confidence.

Third, patient speech may omit important information. The patient may not know what is clinically relevant. This is why the missing-question list is part of the architecture.

Fourth, privacy and responsibility must be explicit. The system needs consent, data-scope control, audit trail, model versioning, and a clear human review workflow.

These risks do not mean the system should not exist. They mean the system must be designed as a bounded support layer, with validation before clinical expansion.

### Slide 11 - Validation Path

To make this system trustworthy, I propose five validation layers.

The first layer is the ASR layer. We should not evaluate only general word error rate. We should evaluate clinically meaningful entities, including medication names, symptom duration, dosage, laterality, numbers, and negation.

The second layer is the LLM structuring layer. We should measure whether the summary is faithful to the transcript, whether it detects missing fields, whether it preserves uncertainty, and whether it avoids hallucinated clinical details.

The third layer is the human review layer. We should measure how often staff accept, correct, reject, or rewrite each section. High correction rates may reveal where the model is weak.

The fourth layer is the workflow layer. We should ask whether the summary reduces intake time, reduces information loss, improves readiness for the visit, or reduces after-hours documentation pressure.

The fifth layer is the governance layer. The system should track model version, prompt version, data scope, review responsibility, privacy rules, and audit trail.

This validation path is important because it turns the idea from a broad AI promise into an evaluable smart-biomedicine workflow.

### Slide 12 - Takeaway And References

Let me close with the main takeaway.

ASR plus LLM is valuable in smart biomedicine when it creates a reviewable clinical surface. The strongest first use case is not autonomous diagnosis or autonomous triage. The strongest first use case is staff-review previsit intake support.

This workflow can help convert patient speech into a structured summary, make missing information visible, preserve uncertainty, and prepare clinicians for a better encounter. At the same time, the design keeps clinical authority in the human review workflow.

In this report, Hager and colleagues help define the decision-making boundary: current LLMs should not be treated as autonomous clinical decision-makers. Jiang and colleagues help define the forward path: healthcare AI needs domain-specific design and real-world evaluation. The ASR plus LLM previsit workflow combines these two lessons. It uses AI where it is useful, and it validates the system before expanding clinical scope.

So my final answer to the core question is yes: patient speech can become a clinician-ready summary, but only if the system is designed as reviewed workflow support, not as an AI doctor.

Thank you for listening.

## Short Version If The Recording Runs Long

If the first rehearsal is longer than `21` minutes, cut these passages first:

- Slide 3: shorten the EHR burden explanation to two sentences.
- Slide 5: remove the detailed comparison between documentation support and triage.
- Slide 9: shorten the synthetic example by removing the patient concern line.
- Slide 11: compress the five validation layers into one sentence each.

Keep these parts:

- The core question.
- The thesis: staff-review previsit intake support.
- The boundary: no autonomous diagnosis, triage, or treatment.
- The proposed architecture.
- The validation path.
