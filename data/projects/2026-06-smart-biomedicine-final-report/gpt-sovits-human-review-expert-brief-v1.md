# GPT-SoVITS Human Review Expert Brief v1

Packet purpose: human review for the Smart Biomedicine final-report GPT-SoVITS narration workflow.

Course report topic: `From Speech Intake to Clinician Summary: ASR and LLMs for Smart Biomedical Pre-visit Workflows`

## What We Need Reviewed Now

The current production blocker is the GPT-SoVITS prompt-reference gate.

We need a human reviewer to:

1. Listen to the prompt-reference candidates.
2. Decide whether `prompt_ref_candidate_04_000381_8p00s.wav` is acceptable as the first GPT-SoVITS prompt reference.
3. If it is acceptable, write the exact transcript for the selected prompt WAV.
4. If it is not acceptable, record why it should be rejected and move to the next candidate in the listening order.

Listening order:

1. `prompt_ref_candidate_04_000381_8p00s`
2. `prompt_ref_candidate_01_000009_5p40s`
3. `prompt_ref_candidate_02_000036_8p00s`
4. `prompt_ref_candidate_03_000072_8p00s`
5. `prompt_ref_candidate_05_000480_8p00s`

## Files To Open First

Open this file in a browser:

```text
review-packet/reference-listening-workbook/index.html
```

The workbook contains:

- original prompt-reference audio,
- slowed `0.85x` / `-3 dB` transcript-aid audio,
- timed ASR draft text,
- plain ASR draft text,
- exact transcript entry field,
- accept command,
- reject command.

The slowed audio is only a hearing aid for transcript writing. Production still uses the original prompt WAV plus a human-confirmed exact transcript.

## Review Criteria

Accept a prompt reference only if all of the following are true:

- The voice is Jason's own authorized voice.
- The audio is between `3-10` seconds.
- The speaking style is usable for a formal course report.
- The volume is stable enough.
- There is no obvious clipping, harsh consonant distortion, popping, room noise, laughter, long pause, or heavy filler.
- The exact transcript can be written with confidence.
- The transcript matches the audio exactly.

Reject a prompt reference if any of the following are true:

- The exact transcript cannot be written confidently.
- The audio sounds clipped or harsh.
- The style is too casual, tired, or unstable.
- There is a long pause or too much filler.
- The candidate would make GPT-SoVITS voice identity unstable.

## What Not To Do

- Do not accept ASR draft text as exact transcript without listening.
- Do not use the full `11:42` source MP3 as a GPT-SoVITS prompt.
- Do not accept more than one prompt reference.
- Do not proceed to all `14` narration chunks until chunk `01` has been generated and accepted.
- Do not use CPU fallback for ASR or GPT-SoVITS production.

## Expected Reviewer Output

Return one of these two outcomes.

### Outcome A: Accept Candidate

Candidate:

```text
prompt_ref_candidate_04_000381_8p00s
```

Exact transcript:

```text
<write exact transcript here>
```

Reviewer notes:

```text
<quality notes, pronunciation concerns, or no concerns>
```

### Outcome B: Reject Candidate

Candidate:

```text
prompt_ref_candidate_04_000381_8p00s
```

Reason for rejection:

```text
<clipping / harsh consonants / transcript mismatch / unstable style / other>
```

Next candidate to review:

```text
prompt_ref_candidate_01_000009_5p40s
```

## After Review

If the candidate is accepted, run the workbook-generated `create_exact_transcript.py` command, then run the workbook-generated `advance_after_reference_review.py` command.

If the candidate is rejected, run the workbook-generated `mark_reference_review_decision.py --decision rejected` command, then run:

```bash
python3 data/projects/2026-06-smart-biomedicine-final-report/tools/reference_decision_status.py
```

This updates the next recommended candidate.
