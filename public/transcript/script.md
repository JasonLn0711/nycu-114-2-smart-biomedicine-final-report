# 20-Minute English Script For Markdown Report v2

Use this script with `markdown-report-v1.md`. The speaking flow follows the Markdown sections and figures, not a slide deck.

## Opening: Title, Question, And Thesis

Hello everyone. My name is Jason Chia-Sheng Lin, and my student ID is 513559004. Today my report topic is `From Speech Intake to Clinician Summary: ASR and LLMs for Smart Biomedical Pre-visit Workflows`.

This report is about one central question: can patient speech become a useful clinician-ready previsit summary without making the AI the doctor?

My answer is yes, but only under a clear operating scope. ASR and LLM systems create the strongest near-term smart-biomedicine value when they are designed as staff-review previsit intake support. In this workflow, patient speech is transcribed, structured, and summarized before the visit. Then clinical staff review and correct the generated content before it influences care.

This distinction is important. I am not arguing that an AI system should diagnose patients, assign final triage, or prescribe treatment. I am arguing for a more practical and safer product shape: AI prepares the clinical review surface, and humans remain responsible for clinical interpretation and action.

## How To Read This Markdown Report

Instead of using a slide deck, this report is designed as a single scrollable Markdown page. The page contains definitions, workflow diagrams, source figures from the selected papers, a proposed architecture, a synthetic output example, and a validation path.

The format itself also reflects the argument. A Markdown report is linear, inspectable, and easy to revise. That is similar to the system I am proposing: the output should be structured, reviewable, and correctable. The goal is not to hide complexity behind a polished interface. The goal is to make the clinical workflow, the AI role, and the scope controls visible.

## Key Definitions

Let me first define the main terms.

ASR means automatic speech recognition. It converts spoken language into text. In this report, ASR is not a clinical decision-maker. It is a transcription layer.

LLM means large language model. It can organize, summarize, and transform language. In this report, the LLM is not the clinical authority. It is a structuring layer that turns a transcript into a draft intake summary.

Previsit intake means collecting information before the patient meets the clinician. This matters because the quality of the clinical encounter depends heavily on the quality of the information available before and during the visit.

Staff-review support means that generated content must be checked by clinical staff. The AI output is not final. It is accepted, edited, rejected, or used to ask follow-up questions.

Finally, a clinician-ready summary is a concise, structured intake note that helps the clinician see the patient story, missing fields, and uncertainty. It is ready for review, not automatically ready for medical action.

These definitions create the boundary for the whole report.

## The Real Workflow Problem

Now I will move to the real workflow problem.

Good clinical decisions require a usable patient story. That sounds simple, but in practice the patient story often arrives under time pressure and in fragments. A patient may describe symptoms out of order. They may forget medication names. They may say that something happened recently, but not specify whether recently means yesterday, last week, or two months ago. They may mention an important symptom casually near the end of the conversation.

This creates work for clinical staff. Before the clinician can reason about the case, someone must reconstruct the timeline, clarify missing information, and identify which details are clinically meaningful.

Please look at the first Mermaid diagram. It shows a loop: patient concern becomes a messy spoken story; the story has missing timeline, medication, severity, and context; the clinician reconstructs the story during a short visit; documentation and follow-up burden increase; and this reduces attention for high-value clinical judgment.

The important point is that the bottleneck appears before diagnosis. The first problem is not always that the clinician lacks a model prediction. The first problem is that the clinical team does not yet have a clean, checkable patient story.

That is why the first useful AI target should be a cleaner intake surface before the visit.

## Why Speech-To-Summary Is Attractive

Speech-to-summary is attractive because speech is natural for patients. Many patients can describe their concern more easily by speaking than by filling out a long form.

But raw speech is not enough. A raw recording is hard to scan. A transcript is better, but it can still be long, messy, and uncertain. The useful output is a structured review draft.

The second Mermaid diagram shows the basic idea. A guided patient voice intake becomes an ASR transcript. The transcript is cleaned and marked with uncertainty. Then an LLM structures the content into chief complaint, symptom timeline, medication and allergy mentions, patient concerns, and missing questions. These outputs then go to staff review, and only after review do they become a clinician-ready previsit summary.

This is the core architecture of the report. Each technology has a bounded role. ASR listens and transcribes. The LLM organizes and drafts. Clinical staff review and correct. The clinician receives a cleaner summary, not an unreviewed AI decision.

## Evidence Landscape

This idea is not disconnected from current healthcare AI. AI documentation tools are already entering clinical workflows. Ambient AI scribes can generate draft clinical notes from spoken clinical encounters. That makes the speech-to-note direction realistic.

However, realism does not remove the safety boundary. Documentation support, previsit intake support, clinical decision-making, triage, and treatment planning are different tasks. They carry different risks.

So the key design question is not simply: can an LLM write fluent clinical text? The better question is: where should ASR and LLMs sit in the clinical workflow, and what should they be allowed to own?

My answer is that they should own preparation of a reviewable intake surface. They should not own final clinical authority.

## Source Figure 1: Hager et al.

The first source figure is the title page of the Hager et al. Nature Medicine paper: `Evaluation and mitigation of the limitations of large language models in clinical decision-making`.

This is the boundary-setting paper for my report. The paper does not directly study ASR or previsit intake, but it is highly relevant because it evaluates limitations of LLMs in realistic clinical decision-making.

The main lesson I use is this: clinical decision-making is more demanding than fluent medical text generation. It requires information gathering, guideline alignment, robustness, instruction following, awareness of uncertainty, and integration into real workflows.

Therefore, this paper supports a positive scope control. We can use LLMs for structured, clinician-reviewed support, but we should not frame the system as an autonomous clinical decision-maker.

In this report, that means the ASR plus LLM system must not make final diagnoses, assign definitive triage acuity, prescribe treatment, or bypass clinical review.

## Source Figure 2: Lang1 Overview

The second source figure comes from Jiang et al.'s Lang1 paper, `Generalist Foundation Models Are Not Clinical Enough for Hospital Operations`.

The overview figure shows a full-cycle modeling pipeline: clinical and web text pretraining, next-token prediction, instruction finetuning, comparison with generalist models, and ablation studies across data mix, model scale, task type, hospital, and time.

For this report, the point is not that we need to build Lang1 for a course project. The point is that healthcare AI needs workflow-specific design and evaluation.

A generic model may be powerful, but hospital operations and clinical workflows require domain context. A previsit intake system should therefore be evaluated on the actual job it claims to do: faithful transcription, faithful structuring, missing-field detection, uncertainty preservation, staff correction patterns, and workflow usefulness.

## Source Figures 3 And 4: Zero-Shot And Finetuned Results

The third and fourth source figures show another important lesson from the Lang1 paper.

The zero-shot figure supports the claim that broad language ability is not enough. Both generalist and specialist models can underperform when directly applied to clinical operations tasks without the right adaptation and evaluation.

The finetuning figure shows the forward path. Finetuned specialists can perform better on workflow-relevant tasks. For my report, this suggests that if an ASR plus LLM previsit intake system becomes a real tool, it should not remain just a generic prompt demonstration. It should move toward supervised evaluation, workflow-specific training, temporal validation, and human review data.

This is why I describe my proposal as an architecture and validation path, not as a finished clinical product.

## Proposed System Architecture

Now I will walk through the proposed system architecture.

The workflow begins with patient consent. The patient should know that their voice will be used to create a previsit summary for staff review.

Next, the patient completes a guided voice interview. The questions can be simple: What is your main concern today? When did it start? What makes it better or worse? Are you taking any medications? Do you have allergies? What are you most worried about?

The ASR system then creates a transcript. Importantly, the transcript should include uncertainty markers. If a medication name, number, or time expression is unclear, the system should not hide that uncertainty.

The LLM then creates a structured intake draft. It can organize the transcript into chief complaint, timeline, medication mentions, allergy mentions, relevant history, and patient concerns. It can also create a missing-information question list.

The most important part of the architecture is the review decision. Clinical staff can accept the draft with edits, ask the patient follow-up questions, or reject unsupported generated sections.

This decision node is the safety center of the workflow. The system is useful only because it is reviewable and rejectable.

## What The System May And Must Not Do

The system may convert patient voice into a transcript. It may mark uncertain words and unclear clinical entities. It may structure the patient story into intake fields. It may generate missing questions. It may produce a draft that staff can inspect, correct, accept, or reject.

But the system must not make a final diagnosis. It must not assign definitive triage acuity. It must not prescribe treatment. It must not bypass clinical staff review. It must not use real patient data in a course demo. And it must not hide uncertainty behind fluent language.

This is not a weak design. This is a responsible design. The value comes from placing automation where it helps, while keeping clinical responsibility where it belongs.

## Synthetic Example Output

Now let me explain the synthetic example table.

Imagine a fictional patient who reports recurring dizziness before a clinic visit. The symptom started about two weeks ago and gets worse when standing quickly. The patient is worried because the episodes happened several times before work. The medication name is unclear in the audio.

A bad AI system might produce a confident diagnosis. That is not what I propose.

A useful system should produce a structured review draft. It should list the chief concern, symptom timeline, patient concern, uncertainty flag, missing questions, and review status.

The missing questions are especially important. The staff may need to ask about episode duration, blood pressure history, recent medication changes, chest pain, shortness of breath, headache, or fainting.

This table shows the practical center of the report. The AI output is valuable because it makes the story easier to check. The uncertainty flag and missing-question list are not embarrassing weaknesses. They are part of the safety design.

## Validation Path

To make the system trustworthy, we need layered validation.

The first layer is ASR validation. We should not evaluate only general word error rate. We should evaluate clinically meaningful entity accuracy, including medication names, symptom duration, dosage, laterality, numbers, and negation.

The second layer is LLM structuring validation. We should measure faithfulness to the transcript, missing-field detection, hallucination rate, and whether uncertainty is preserved.

The third layer is human review validation. We should measure how often staff accept, correct, reject, or rewrite each section. Correction patterns can show where the model is weak.

The fourth layer is workflow validation. We should ask whether the summary improves intake readiness, reduces information loss, reduces repeated questioning, or reduces documentation burden.

The fifth layer is governance validation. The system should track model version, prompt version, data scope, review responsibility, privacy rules, and audit trail.

This validation path turns the idea from a broad AI promise into an evaluable smart-biomedicine workflow.

## Risk And Scope-Control Matrix

The risk matrix summarizes the main design controls.

ASR errors matter because drug names, numbers, negation, and timing can be clinically important. The control is uncertainty marking and staff verification.

LLM hallucination matters because fluent summaries can create false confidence. The control is faithfulness evaluation and uncertainty preservation.

Missing context matters because patients may omit details they do not know are relevant. The control is the missing-question list.

Workflow mismatch matters because a technically good output may still fail in real clinical work. The control is staff correction analysis and intake-time evaluation.

Privacy and responsibility matter because clinical data requires governance. The control is consent, audit trails, and data-scope control.

Together, these controls define the operating scope of the system.

## Closing

Let me close with the final takeaway.

ASR plus LLM is most useful in smart biomedicine when it prepares a better clinical review surface before the visit. The first responsible product shape is not an autonomous doctor. It is a staff-review previsit intake workflow that turns patient speech into structured, inspectable, and correctable information.

This design connects a real clinical bottleneck to a practical AI architecture. It uses AI for transcription, structuring, summarization, and missing-question generation. It keeps diagnosis, triage, and treatment under human clinical authority. And it defines validation layers before clinical expansion.

So my final answer to the opening question is yes: patient speech can become a clinician-ready previsit summary, but only when the system is designed as reviewed workflow support, not as an AI doctor.

Thank you for listening.
