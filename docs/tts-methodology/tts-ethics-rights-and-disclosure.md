# TTS Ethics, Rights, And Disclosure Record

Use this record whenever a TTS experiment uses a real person's voice as
reference audio, adaptation audio, prompt audio, or evaluation material.

## Required Fields

```text
Voice source:
Whose voice:
Consent obtained:
Allowed use:
Forbidden use:
Can be shared externally:
Can be used in research:
Need synthetic voice disclosure:
IRB relevance:
Storage location:
Deletion / withdrawal mechanism:
```

## Operating Rules

- If the voice belongs to a real person, keep the raw reference audio in
  `assets/tts-local-only/` or another private storage location.
- Do not commit raw voice, generated WAV/MP3/M4A, failed samples, or model
  artifacts to the public repo.
- Public docs may include hash, duration, sample rate, route, and QA status.
- External sharing requires a clear allowed-use record.
- Research reuse requires a separate research-use record and IRB review when
  applicable.
- If a final video uses synthetic or cloned voice, include a disclosure when
  required by the venue, IRB, course, journal, or platform.

## Minimal Disclosure Sentence

```text
This narration was generated with an authorized synthetic voice workflow for
research/course presentation purposes.
```

Adjust the wording for each project, but do not imply consent or authorization
unless it is documented.
