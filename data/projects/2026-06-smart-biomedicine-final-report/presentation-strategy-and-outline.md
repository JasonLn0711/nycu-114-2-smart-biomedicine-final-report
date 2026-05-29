# Smart Biomedicine Final Report Presentation Strategy

## Topic

`從語音問診到醫師摘要：ASR + LLM 在智慧生醫臨床前問診中的應用與邊界`

## Runtime Constraint

- Target length: finish within `20` minutes.
- Working target: `16-18` minutes of main content plus `1-2` minutes of buffer.
- Production format: slide-supported video, uploaded to YouTube and posted to Padlet.
- Detailed architecture: `data/projects/2026-06-smart-biomedicine-final-report/report-architecture-v1.md`

## Core Narrative Principle

The report should be stable and evidence-based, but it must also be worth watching. The presentation should not begin as a flat paper summary. It should begin with a real problem that is happening now, or a problem we can reasonably expect to happen soon, and every problem claim must have citation support.

This strategy now follows the repo-level evidence-led narrative rule: real problem -> cited current solutions -> evidence-backed gap -> Jason's new viewpoint -> operating scope -> next validation path.

## Argument Shape

1. Reality hook:
   - Start with a concrete clinical workflow problem.
   - Candidate problem: physicians and clinical teams must gather messy patient narratives, handle EHR / documentation burden, and make workflow decisions under time pressure.
   - Evidence requirement: cite literature such as Sinsky et al. on physician time / EHR burden, plus Hager et al. on realistic clinical decision-making complexity.
2. Existing solution:
   - People are already exploring LLMs for clinical decision support, diagnostic dialogue, documentation, EHR prediction, and hospital operations.
   - Evidence requirement: cite Hager et al. for autonomous clinical-decision evaluation and Jiang et al. / Lang1 for hospital-operations modeling.
3. Why current approaches are not enough:
   - Generic LLMs may perform well on exams or broad text benchmarks, but realistic clinical workflows require information gathering, guideline alignment, instruction following, robustness, workflow integration, and temporal validation.
   - Hager et al. support the claim that current LLMs are not ready for autonomous clinical decision-making.
   - Lang1 supports the claim that generalist foundation models are not specialized enough for hospital operations without in-domain pretraining, supervised finetuning, and real-world evaluation.
4. Jason's viewpoint:
   - The right near-term clinical AI product shape is not an autonomous doctor.
   - The useful shape is a `staff-review intake support` workflow:
     patient speech -> ASR transcript -> LLM structuring -> clinician-reviewed summary.
   - This preserves the attractive product idea while keeping the clinical boundary honest.
5. Closing implication:
   - ASR + LLM can make smart biomedicine more useful when it is designed as workflow support, not as unreviewed clinical authority.

## Citation Map

| Claim | Citation / source to use |
| --- | --- |
| Physicians and clinical teams face documentation and EHR burden | Sinsky et al. `Allocation of physician time in ambulatory practice`; Murphy et al. `The burden of inbox notifications in commercial electronic health records`; Hingle `Electronic health records: An unfulfilled promise and a call to action` |
| Real clinical decision-making requires information gathering, guidelines, workflow integration, and robustness | Hager et al. `Evaluation and mitigation of the limitations of large language models in clinical decision-making` |
| Current LLMs should not be framed as autonomous clinical decision-makers | Hager et al. |
| Hospital operations need specialized evaluation beyond broad medical benchmarks | Jiang et al. / arXiv `2511.13703`, `Generalist Foundation Models Are Not Clinical Enough for Hospital Operations` |
| Domain-specific clinical models and supervised finetuning are important for practical healthcare AI | Jiang et al. / Lang1 paper |
| Jason's proposed system should remain clinician-reviewed | Synthesis from Hager et al. plus course-safe scope-control reasoning |

## 20-Minute Slide Plan

| Time | Slide / section | Purpose |
| ---: | --- | --- |
| `0:00-1:00` | Title and identity | State topic, name, student ID, and the core question. |
| `1:00-3:00` | Reality hook | Explain clinical intake / documentation burden and why speech-to-summary is a real workflow problem. |
| `3:00-5:30` | Why generic AI is tempting | Show the appeal: ASR captures speech, LLMs summarize language, clinicians need better previsit context. |
| `5:30-8:00` | Boundary paper: Hager et al. | Current LLMs are not ready for autonomous clinical decision-making; use this to set safety scope. |
| `8:00-11:00` | Next paper: Lang1 | Generalist foundation models are not clinical enough for hospital operations; specialized training and evaluation matter. |
| `11:00-14:00` | Proposed workflow | Patient speech -> ASR -> transcript cleanup -> LLM structured intake -> clinician review. |
| `14:00-16:00` | Why this is better scoped | It solves an intake and documentation problem without claiming autonomous diagnosis / triage / treatment. |
| `16:00-18:00` | Limitations and validation path | ASR errors, missing context, bias, privacy, domain shift, clinician correction, real-world evaluation. |
| `18:00-19:30` | Takeaway | Smart biomedicine should combine attractive AI workflow design with human-review scope controls. |
| `19:30-20:00` | Buffer | Closing sentence / transition / citation slide. |

## Tone Rule

Use a confident, positive-scope voice:

- Lead with the capability: ASR + LLM can reduce information loss and create a better clinician review surface.
- Then state the scope control: this is intake support, not autonomous clinical decision-making.
- Keep the report engaging by showing the problem, the current solution attempt, the gap, and the new workflow viewpoint.

## Do Not Claim

- Do not claim autonomous diagnosis.
- Do not claim validated triage.
- Do not claim treatment recommendation.
- Do not claim production clinical safety.
- Do not use real patient data.

## Next Build Step

Turn `report-architecture-v1.md` into a slide outline with citations per slide, then draft a `16-18` minute speaking script.
