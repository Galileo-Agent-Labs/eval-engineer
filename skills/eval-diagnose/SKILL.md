---
name: eval-diagnose
description: Use when Galileo evidence is available and the user asks why a trace, session, log stream, experiment, metric, or AI app behavior failed, regressed, or became unsafe.
---

# Eval Diagnose

Use this skill for evidence-backed RCA once a packet, URL-derived evidence, or
trace/session/log-stream context is available.

## Required Reference

Use `skills/eval-engineer/references/rca-recipe.md`,
`skills/eval-engineer/references/debug-packets.md`,
`skills/eval-engineer/references/evidence-provenance.md`, and
`skills/eval-engineer/assets/diagnosis-template.md`.

## Do

- Start from fetched evidence, not source-code guesses.
- Name the failing metric contract and what it proves.
- Label hosted Galileo evidence separately from local deterministic packets
  before making metric or score claims.
- Inspect traces, spans, sessions, tool calls, retrieval context, and scorer
  status to classify the fix surface.
- Classify the fix surface: prompt, tool schema, adapter, retriever, ranker,
  guardrail, metric, dataset, or SDK wiring.
- Write diagnosis and bounded fix plan only when evidence supports it.
- Honor read-only requests. If the user says read-only, dry run, no edits, or
  "do not edit files", do not write `.galileo/` artifacts. Return the RCA
  inline and include a short "Would write" list for any suggested artifact
  paths.

## Gotchas

- Fetched debug packets are the RCA source of truth when scorer jobs are still
  settling or runner output disagrees with fetched metrics.
- A prompt diff, local score, or code diff is not proof of improvement without
  before/after Galileo evidence.
- Bare correctness or factuality can be a smoke test only. Prefer the metric
  contract tied to the case risk.
- Safe final wording is not enough for source-authority cases if unsafe or
  forbidden retrieved context entered the task surface.

## Validation Loop

Before finalizing:

1. Run `python3 skills/eval-engineer/scripts/summarize_debug_packet.py <packet>`
   unless a compact summary is already available.
2. Check that every RCA claim names supporting metric, trace, span, session,
   experiment, dataset, or log-stream evidence.
3. Confirm the fix surface is bounded and allowed by `.galileo/config.yml`.
4. If any claim lacks evidence, downgrade it to a hypothesis or route to
   `/eval-fetch` or `/eval-measure`.

## Output

Unless the request is read-only, produce `.galileo/current/diagnosis.md` and, when justified,
`.galileo/current/fix-plan.md`. If evidence is insufficient, route to
`/eval-fetch` or `/eval-measure`.
