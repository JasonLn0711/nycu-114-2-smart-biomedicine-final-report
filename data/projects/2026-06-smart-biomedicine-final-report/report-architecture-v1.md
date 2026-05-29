# Smart Biomedicine Final Report Architecture v1

## Report Identity

- Course: `【114 Spring】132603 智慧生醫概論 Introduction of Smart Biomedicine`
- Student ID: `513559004`
- Name: `林家聖`
- Topic: `從語音問診到醫師摘要：ASR + LLM 在智慧生醫臨床前問診中的應用與邊界`
- Working English title: `From Speech Intake to Clinician Summary: ASR and LLMs for Smart Biomedical Pre-visit Workflows`
- Target runtime: within `20` minutes
- Working runtime design: `16-18` minutes core talk plus `1-2` minutes buffer

## FIRST PRINCIPLE Read

- Scarce resource: audience attention, citation-backed trust, and the `20` minute runtime.
- Real report job: make classmates and teachers understand why ASR + LLM is attractive in smart biomedicine, while also understanding why the first responsible clinical shape is clinician-reviewed intake support.
- Canonical question:

```text
Can we turn patient speech into a useful clinician-ready previsit summary without pretending that the AI is the doctor?
```

## One-Sentence Thesis

ASR + LLM systems can create value in smart biomedicine when they are designed as `staff-review intake support`: patient speech is transcribed, structured, and summarized before the visit, then reviewed and corrected by clinical staff before it influences care.

## Audience Promise

By the end of the report, the audience should be able to answer four questions:

1. What real clinical workflow problem makes speech-to-summary attractive?
2. What solutions already exist, and what do they show?
3. Why are generic LLMs or ambient scribes still insufficient as the whole answer?
4. What is the safer and more useful architecture for near-term smart-biomedicine use?

## Narrative Spine

Use the repo-level evidence-led narrative rule:

```text
real problem -> cited current solutions -> evidence-backed gap -> Jason's viewpoint -> operating scope -> validation path
```

### Act 1 - The Real Problem: Clinical Information Is Collected Under Time Pressure

Core message:

- Before a physician can make a good decision, the system must first collect a usable story.
- In real clinics, patient narratives are messy, incomplete, and time-consuming to reconstruct.
- EHR and documentation work compete with direct clinical attention.

Evidence to cite:

- Sinsky et al. observed ambulatory physicians and reported that physicians spent `27.0%` of office time on direct clinical face time and `49.2%` on EHR / desk work; they also reported `1-2` hours of after-hours EHR-related work in diaries. [Sinsky2016]
- Murphy et al. documented EHR inbox notification burden in commercial EHRs. [Murphy2016]
- Hingle framed EHRs as an unfulfilled promise requiring action. [Hingle2016]

Opening hook:

```text
病人進診間前，真正的問題常常不是 AI 會不會診斷，而是醫師還沒有一份乾淨、可檢查、可追問的病人故事。
```

### Act 2 - The Existing Solution Landscape: AI Is Already Being Used To Draft Clinical Notes

Core message:

- This is not science fiction. Hospitals and clinics are already testing AI documentation and ambient scribe tools.
- The basic pipeline is attractive: conversation audio -> transcript -> draft clinical note.

Evidence to cite:

- Ma et al. studied a large language model-powered ambient AI scribe in an academic medical center, reporting use across `9,629` of `17,428` encounters and reductions in documentation / EHR time, while also noting individual heterogeneity and the need for further study. [Ma2025]
- Ambient listening technology has been described as generative AI that produces clinical notes from clinician-patient spoken conversation and can integrate into EHR workflows. [JGIM2024]

Framing:

```text
所以問題不是「能不能用 AI 幫忙寫病歷」。問題是：如果我們把語音、ASR、LLM 放進臨床流程，應該把它放在哪一個位置，負責哪一種任務？
```

### Act 3 - Why Current Approaches Are Not Enough

Core message:

- Existing systems show the direction is promising, but a generic "AI doctor" framing is too broad and too risky.
- Documentation support, autonomous decision-making, and hospital-operations prediction are different tasks.
- Passing broad language or medical-question benchmarks is not the same as succeeding in a clinical workflow.

Evidence to cite:

- Hager et al. evaluated LLMs in realistic clinical decision-making scenarios and concluded that current models require extensive clinician supervision before autonomous deployment. [Hager2024]
- Hager et al. also highlight failures around information gathering, guideline alignment, robustness, instruction following, and clinical supervision needs. [Hager2024]
- Jiang et al. argue that generalist foundation models are not clinical enough for hospital operations; their Lang1 / ReMedE work supports the need for in-domain pretraining, supervised finetuning, and real-world evaluation beyond proxy benchmarks. [Jiang2025]

Gap statement:

```text
我們不應該把 ASR + LLM 包裝成「自動看診」。比較合理的第一步，是把它設計成一個能被醫療人員檢查、修正、採納或拒絕的 previsit intake support layer。
```

### Act 4 - Jason's Proposed Viewpoint: Staff-Review Previsit Intake Support

Core message:

- The new viewpoint is not "AI replaces doctors".
- The useful near-term product shape is "AI prepares the clinical review surface".
- The system should convert patient speech into a structured draft that makes missing information visible and makes clinician review easier.

Proposed workflow:

```text
patient consent
-> guided patient speech / previsit voice interview
-> ASR transcript with uncertainty markers
-> transcript cleanup and segmentation
-> LLM structured intake summary
-> missing-information question list
-> clinician / staff review and correction
-> clinician-ready previsit summary
```

What the LLM may do:

- organize chief complaint, symptom timeline, medication / allergy mentions, prior history, and patient concerns
- flag missing intake fields as questions
- produce a staff-only structured summary
- preserve uncertainty where ASR or patient wording is unclear

What the LLM must not do in this report:

- make final diagnosis
- assign definitive triage acuity
- prescribe treatment
- bypass clinician review
- use real patient data

### Act 5 - Validation Path: How This Becomes Trustworthy

Core message:

- The architecture is attractive because it targets a real bottleneck.
- It is trustworthy because each risky claim is assigned to a validation layer before clinical expansion.

Validation layers:

1. ASR layer:
   - Word error rate is not enough; clinically meaningful entities such as drug names, symptom duration, laterality, dosage, and negation must be checked.
2. LLM structuring layer:
   - Evaluate missing-field detection, symptom timeline correctness, hallucination rate, and whether uncertainty is preserved.
3. Human review layer:
   - Measure how often clinicians correct, reject, or accept each section.
4. Workflow layer:
   - Measure whether previsit summaries reduce information loss, after-hours documentation pressure, and intake time.
5. Governance layer:
   - Track version, model, prompt, data scope, review responsibility, privacy, and audit trail.

Closing claim:

```text
Smart biomedicine does not need to start by asking AI to replace the doctor. A more useful first step is to let AI prepare a better, reviewable clinical surface before the visit.
```

## 20-Minute Report Structure

| Time | Section | Slide title | Main job | Citation function |
| ---: | --- | --- | --- | --- |
| `0:00-1:00` | Title | From Speech Intake to Clinician Summary | Introduce identity, topic, and one guiding question. | No citation needed. |
| `1:00-2:30` | Hook | The Missing Story Before the Visit | Show the real problem: clinicians need a usable patient story before deciding. | Sinsky2016, Murphy2016. |
| `2:30-4:00` | Burden | Clinical Attention Is Competing With Documentation | Quantify EHR / documentation burden and why it matters. | Sinsky2016, Hingle2016. |
| `4:00-5:30` | Existing solution | AI Scribes Are Already Here | Explain ambient AI scribes and speech-to-note systems. | Ma2025, JGIM2024. |
| `5:30-7:00` | Temptation | Why ASR + LLM Looks Like the Obvious Answer | Show why speech recognition plus summarization is attractive. | Ma2025. |
| `7:00-9:00` | Boundary | The AI Doctor Framing Breaks Too Early | Explain why autonomous clinical decision-making is not the right first frame. | Hager2024. |
| `9:00-10:30` | Generalist gap | Generalist Models Are Not Clinical Enough | Show why broad benchmark strength does not equal hospital workflow readiness. | Jiang2025. |
| `10:30-12:00` | Reframe | The Better First Product Shape | Introduce `staff-review intake support`. | Synthesis from Hager2024 and Jiang2025. |
| `12:00-14:00` | Architecture | Patient Speech -> Clinician-Ready Summary | Walk through the proposed pipeline. | Architecture slide; cite Hager2024 for scope control. |
| `14:00-15:30` | Example | What the Output Should Look Like | Show a synthetic structured summary and missing-question list. | No real patient data; cite scope rule. |
| `15:30-17:00` | Safety | Where Errors Can Enter | Explain ASR errors, LLM hallucination, missing context, and review responsibility. | Hager2024; optional ASR review source. |
| `17:00-18:30` | Validation | How We Would Prove It Works | Present layered evaluation: ASR, LLM, human review, workflow, governance. | Jiang2025 for real-world evaluation principle. |
| `18:30-19:30` | Takeaway | Smart Biomedicine As Reviewable Workflow | Return to opening problem and state the contribution. | No new citation. |
| `19:30-20:00` | Buffer | References / Closing | End cleanly or absorb timing overrun. | Reference slide. |

## Suggested Visuals

### Figure 1 - Problem Loop

Purpose: make the opening problem visible.

```text
messy patient story -> time pressure -> incomplete intake -> documentation burden -> less clinical attention -> more reconstruction work
```

### Figure 2 - Existing Solutions Map

Purpose: show that current AI work is promising but fragmented.

```text
Ambient AI scribe
  - strength: draft visit note
  - gap: still needs review; mainly after / during encounter

Clinical decision LLM
  - strength: broad reasoning and summarization
  - gap: unsafe as autonomous decision-maker

Hospital operations foundation model
  - strength: domain-specific operational prediction
  - gap: needs in-domain data, finetuning, and real-world evaluation
```

### Figure 3 - Proposed Workflow

Purpose: make Jason's viewpoint concrete.

```text
Patient voice
-> ASR transcript
-> uncertainty markers
-> LLM structuring
-> missing-question list
-> clinician review
-> previsit summary
```

## Core Positioning

### What This Report Contributes

- It connects a real clinical workflow problem to smart-biomedicine AI design.
- It uses ASR + LLM as a useful workflow-support concept, not as an autonomous medical authority.
- It translates LLM safety concerns into positive product scope controls.
- It proposes a practical architecture that can be evaluated before clinical expansion.

### What Makes The Report Worth Watching

- The opening starts from a real pressure point: clinicians need the patient story but are overloaded by EHR and documentation work.
- The report shows that AI scribes already exist, so the topic feels real.
- The report then creates tension: useful AI documentation is not the same as safe autonomous clinical reasoning.
- The proposed answer is concrete: use AI to prepare a reviewable clinical surface before the visit.

## Scope Controls

Use these phrases consistently:

- `staff-review intake support`
- `clinician-reviewed summary`
- `previsit workflow support`
- `human review workflow`
- `validation path before clinical expansion`
- `course-level architecture, not production medical software`

Avoid these claims:

- autonomous diagnosis
- autonomous triage
- treatment recommendation
- production clinical safety
- replacement of physicians
- validation on real patient data

## Citation Backbone

| Citation ID | Use in report | Full reference |
| --- | --- | --- |
| `Sinsky2016` | Quantify EHR / desk-work burden and lost clinical attention. | Sinsky C, Colligan L, Li L, Prgomet M, Reynolds S, Goeders L, Westbrook J, Tutty M, Blike G. `Allocation of Physician Time in Ambulatory Practice: A Time and Motion Study in 4 Specialties`. Annals of Internal Medicine. 2016;165(11):753-760. DOI: `10.7326/M16-0961`. |
| `Murphy2016` | Support EHR inbox / information-burden problem. | Murphy DR, Meyer AND, Russo E, Sittig DF, Wei L, Singh H. `The Burden of Inbox Notifications in Commercial Electronic Health Records`. JAMA Internal Medicine. 2016;176(4):559-560. DOI: `10.1001/jamainternmed.2016.0209`. |
| `Hingle2016` | Frame EHR as a still-unfulfilled promise and clinical workflow problem. | Hingle S. `Electronic Health Records: An Unfulfilled Promise and a Call to Action`. Annals of Internal Medicine. 2016;165(11):818-819. DOI: `10.7326/M16-1757`. |
| `Ma2025` | Show existing ambient AI scribe solution and measured documentation-time impact. | Ma SP, et al. `Ambient artificial intelligence scribes: utilization and impact on documentation time`. Journal of the American Medical Informatics Association. 2025;32(2):381-385. DOI: `10.1093/jamia/ocae304`. |
| `JGIM2024` | Explain ambient listening technology as generative AI that creates clinical notes from spoken encounters. | `Impact of an Artificial Intelligence-Based Solution on Clinicians' Clinical Documentation Experience: Initial Findings Using Ambient Listening Technology`. Journal of General Internal Medicine. 2024. DOI: `10.1007/s11606-024-08924-2`. |
| `Hager2024` | Boundary paper: current LLMs require supervision and should not be framed as autonomous clinical decision-makers. | Hager P, et al. `Evaluation and mitigation of the limitations of large language models in clinical decision-making`. Nature Medicine. 2024. DOI: `10.1038/s41591-024-03097-1`. |
| `Jiang2025` | Forward path: generalist models are not enough for hospital operations; domain adaptation and real-world evaluation matter. | Jiang LY, et al. `Generalist Foundation Models Are Not Clinical Enough for Hospital Operations`. arXiv: `2511.13703v1`. 2025. |

## First 90 Seconds Draft

```text
大家好，我是林家聖，學號 513559004。我的題目是：從語音問診到醫師摘要：ASR + LLM 在智慧生醫臨床前問診中的應用與邊界。

我想先從一個很實際的問題開始。很多時候，臨床 AI 的討論會直接跳到「AI 能不能診斷」。但在醫師診斷之前，還有一件更基本的事情：醫師要先得到一份可信、完整、可追問的病人故事。

問題是，真實臨床工作並不是在乾淨的資料表裡發生。病人的敘述可能很長、很跳躍、夾雜生活事件、用藥記憶、症狀時間線，而且醫師同時還要面對 EHR、病歷書寫、訊息通知和時間壓力。Sinsky 等人的 time-motion study 顯示，門診醫師在 office day 中直接面對病人的時間只有 27.0%，但 EHR 與 desk work 佔 49.2%。所以，這份報告真正想問的不是：AI 能不能取代醫師。而是：ASR + LLM 能不能先幫我們把病人的語音整理成一份醫師可以檢查、修正、採納或拒絕的 previsit summary？
```

## Next Build Step

- Turn this architecture into a slide-level outline with one visual plan and one citation per slide.
- Then draft the `16-18` minute speaking script.
