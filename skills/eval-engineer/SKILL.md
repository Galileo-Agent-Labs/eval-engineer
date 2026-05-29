---
name: eval-engineer
description: Use when a user is unsure which Eval Engineer command to run for AI agents/RAG apps, needs onboarding/status for a .galileo workspace, or asks where to start.
---

# Eval Engineer

Use this skill as the front door for Galileo-backed eval engineering. Keep it
as a router: inspect current project readiness, educate the user only enough to
choose the workflow, and route to the focused command skill that matches the
job.

If a focused skill clearly applies, use that focused skill directly instead of
running the full core loop here.

## Current Project State

Start by checking what the user gave you and what the project already has:

- Galileo URL, project/log-stream/experiment/session/trace ID, or symptom
- `.galileo/config.yml`
- `.galileo/current/debug-packet.json`
- `.galileo/current/verification-debug-packet.json`
- configured verification commands
- metric profile or expected-output contract

Then report one compact status block:

```text
Eval Engineer works by closing the loop:
evidence -> diagnosis -> bounded change -> verification.

Current project state:
- workspace: ready/missing
- evidence: ready/missing/ambiguous
- measurement: ready/missing
- best next command: /eval-...
```

Do not dump general docs. Name the smallest useful next step.

## Route

- Use `/eval-setup` when `.galileo/` or verification config is missing.
- Use `/eval-fetch` when the user provides a Galileo URL/ID or needs evidence
  pulled into `.galileo/current/debug-packet.json`.
- Use `/eval-dataset` when the user wants to create, review, accept, reject,
  or improve eval cases under `.galileo/eval-dataset/`.
- Use `/eval-measure` when the question is whether metrics, rubrics, or
  expected-output contracts are correct.
- Use `/eval-diagnose` when a debug packet or fetched evidence is ready and the
  user wants root cause.
- Use `/eval-cost` when the goal is token, latency, model-routing, tool-loop, or
  evaluator-cost reduction.
- Use `/eval-audit` when the user wants a launch, safety, OWASP, security,
  coverage, or production-readiness review.

If the right route is uncertain, ask one clarifying question. If evidence is
missing, explain exactly what is missing and how `/eval-fetch` or `/eval-setup`
will get it.

## Core Loop

1. **Find the working set.**
   - Prefer `.galileo/current/debug-packet.json`.
   - Treat `.galileo/current/debug-packet.json` as the baseline or active
     packet being diagnosed.
   - Treat `.galileo/current/verification-debug-packet.json` as the optional
     after-change packet used for comparison.
   - Read `.galileo/config.yml` for agent type, editable files, blocked files,
     metrics, and verification commands.
   - Read `.galileo/learnings.md` if it exists.
   - If no current packet exists, use a user-provided packet path or help import
     Galileo evidence before diagnosing.

2. **Summarize evidence before reasoning.**
   - Run:
     `python3 skills/eval-engineer/scripts/summarize_debug_packet.py <packet>`
   - Use raw traces only when the compact packet is missing required evidence.
   - Classify score provenance using
     `references/evidence-provenance.md` before treating metrics as Galileo
     evidence. A packet under `.galileo/` is not automatically hosted Galileo evidence.

3. **Diagnose from Galileo concepts.**
   - Use metrics to identify what degraded.
   - Use traces/spans to identify where behavior diverged.
   - For new eval cases, fixture expansion, or tokenomics work, use
     `references/metric-profile-checklist.md` before changing behavior.
   - For cost, latency, or token-efficiency work, use
     `references/tokenomics-rca.md` and compare cost evidence against quality
     metrics before proposing optimization.
   - Check whether the issue is in the app, the test case, the metric, or the
     Galileo integration before proposing code changes.
   - Use the RCA recipe in `references/rca-recipe.md` to select the smallest
     evidence-backed fix surface.
   - Prefer Galileo-specific reasoning: datasets, metrics, experiments, log
     streams, traces, spans, sessions, custom metrics, and run comparison.
   - Treat experiments as controlled sample evals and log streams as production
     or live-traffic RCA sources.

4. **Write bounded artifacts.**
   - Write or update `.galileo/current/diagnosis.md`.
   - Write or update `.galileo/current/fix-plan.md`.
   - Write or update `.galileo/current/verification-plan.md`.
   - Use the templates in `assets/` for expected artifact shape.
   - Preserve Galileo evidence links or stable IDs in every RCA artifact.
   - Include this compact block in RCA artifacts that mention metrics:

     ```text
     Evidence provenance:
     - hosted Galileo evidence used: yes/no
     - score source: galileo_fetched/local_existing/local_generated/mixed/unknown
     - missing before Galileo-backed claim: none/<specific IDs or metrics>
     ```
   - Keep edits inside allowed paths from `.galileo/config.yml`.
   - If useful, append a concise general pattern to `.galileo/learnings.md`.

5. **Create candidate eval cases carefully.**
   - Use `/eval-dataset` for candidate, accepted, and rejected case workflows.
   - Propose candidates only for clear, reusable failures.
   - Avoid duplicates, ambiguous cases, and sensitive data.
   - Write candidates to `.galileo/eval-dataset/candidates.jsonl` only when the
     failure is suitable for human review.

6. **Verify before claiming improvement.**
   - Use exact local and Galileo commands from `.galileo/config.yml` when
     available.
   - Save or reference the after-change packet as
     `.galileo/current/verification-debug-packet.json` when working in the
     current set.
   - Compare the new run against `.galileo/current/debug-packet.json`, the
     verification packet, or a session manifest.
   - Report improved, regressed, and unchanged metrics.
   - Label local verification scores as local. Do not present local generated
     packets as server-side Galileo metric results.
   - A prompt or code diff alone is never proof of improvement.

## Guardrails

- Do not hardcode one reference agent, one dataset, one metric, or one provider.
- Do not scan historical raw sessions unless asked or needed for comparison.
- Do not silently overwrite session evidence.
- Do not use ambiguous packet names such as `debug-packet-after.json`; use
  `verification-debug-packet.json` for after-change evidence in `.galileo/current/`.
- Do not promote eval candidates without human review.
- Do not create or rely on a new local eval harness as a substitute for Galileo
  evidence unless the user explicitly asks for fixture generation or confirms
  local-only evaluation.
- Do not make broad rewrites when a bounded prompt, tool, retriever, guardrail,
  metric, or dataset fix is enough.
- Do not provide RCA claims without trace, span, session, metric, dataset,
  experiment, or log-stream evidence.

## References

- Working-set structure: `references/working-set.md`
- Debug packet schema and usage: `references/debug-packets.md`
- Evidence provenance: `references/evidence-provenance.md`
- Eval dataset case design: `references/eval-datasets.md`
- Galileo evidence sources: `references/galileo-sources.md`
- Galileo live readiness: `references/galileo-live-readiness.md`
- Galileo metric selection: `references/metrics.md`
- Metric-profile checklist for cases and segments:
  `references/metric-profile-checklist.md`
- Galileo experiment wiring: `references/galileo-experiments.md`
- General RCA recipe: `references/rca-recipe.md`
- Tokenomics RCA for cost, latency, and token reduction:
  `references/tokenomics-rca.md`
- Output artifact templates: `assets/diagnosis-template.md`,
  `assets/fix-plan-template.md`, `assets/verification-plan-template.md`,
  `assets/cost-diagnosis-template.md`,
  `assets/tokenomics-fix-plan-template.md`,
  `assets/quality-preserving-verification-template.md`,
  `assets/metric-profile-template.md`
- Repo plan/status context: `docs/plan.md`, `docs/tasks.md`, `docs/progress.md`
