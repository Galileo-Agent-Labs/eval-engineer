# Evidence Provenance

Eval Engineer must say where scores came from before using them to diagnose or
claim improvement.

## Provenance Classes

- `galileo_fetched`: evidence fetched from Galileo traces, sessions, log
  streams, experiments, or server-side metric results.
- `local_existing`: an existing local packet, fixture, or deterministic eval
  artifact that was present before the current agent run.
- `local_generated`: a packet, harness, or score file created during the
  current agent run.
- `mixed`: a comparison that combines Galileo-fetched evidence with local
  verification evidence.
- `unknown`: evidence with insufficient metadata.

## Required Metadata For Galileo-Backed Claims

Do not call scores Galileo-backed unless the packet or artifact has enough
source metadata to identify the hosted evidence:

- `source` or equivalent provenance field identifying Galileo
- `project_id`
- one of `log_stream_id`, `experiment_id`, `session_id`, or `trace_id`
- scorer or metric names
- fetch timestamp or run timestamp

If these are missing, describe the packet as local or unknown even when it
lives under `.galileo/`.

## Required Evidence Block

Every diagnosis, fix plan, verification plan, and final summary that mentions
scores should include one compact block:

```text
Evidence provenance:
- hosted Galileo evidence used: yes/no
- score source: galileo_fetched/local_existing/local_generated/mixed/unknown
- missing before Galileo-backed claim: none/<specific IDs or metrics>
```

## Local Evidence Language

Use explicit wording for local evidence:

- "local deterministic evaluation only"
- "local generated verification packet"
- "Galileo evidence has not been fetched"

Do not say or imply that local metrics are server-side Galileo scorer results.

## Local Harness Guardrail

Do not create a new eval harness, candidate packet, or `.galileo/current`
debug packet as a substitute for Galileo evidence unless the user explicitly
asks for fixture generation or confirms local-only evaluation.

If only local evidence exists and the user asked for Galileo-backed evaluation,
the next step is to ask for a Galileo URL/ID or run `/eval-fetch`, not to report
the workflow complete.
