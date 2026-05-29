# Galileo Integration Intake

Use this checklist before creating local eval evidence when the user expects
Galileo-backed diagnosis, measurement, or verification.

## Required Inputs

At least one hosted Galileo locator is required before claiming Galileo evidence
is available:

- `GALILEO_CONSOLE_URL`
- Galileo project URL or project ID
- log stream URL/ID, experiment URL/ID, session ID, or trace ID
- time window, trace filter, or latest-N selection when a log stream is broad
- metric/scorer names to read, enable, or recompute

The user may instead choose an explicit local-only workflow. Record that choice
before creating local packets, scripts, or scores.

## Intake Question

When required inputs are missing, ask one concise question that names the
minimum unblocker:

```text
I need a Galileo project/log-stream/experiment/session/trace URL or ID before I
can use hosted Galileo evidence. Should I fetch hosted Galileo evidence, or are
you asking for a local-only eval instead?
```

If credentials may be missing, ask the user to confirm availability without
printing secret values:

```text
Please confirm `GALILEO_API_KEY` is available in this shell and provide the
Galileo project or evidence URL/ID to inspect.
```

## Do Not Substitute

Do not create any of these as a substitute for missing Galileo integration
inputs unless the user explicitly chooses local-only evaluation:

- `.galileo/current/debug-packet.json`
- `.galileo/current/verification-debug-packet.json`
- `scripts/evaluate_*`
- local judge/scorer output presented as Galileo metric scores
- synthetic traces presented as hosted sessions

Local evidence can be useful, but it must be labeled as local-only and cannot
support claims about hosted Galileo metrics, log streams, experiments, sessions,
or traces.

## Status

Every setup, diagnosis, measurement, or verification response that depends on
evidence should use the evidence provenance block from
`references/evidence-provenance.md`. For intake, make sure the block names
whether hosted Galileo evidence is available, which Galileo inputs are missing,
and whether the user explicitly chose local-only evaluation.
