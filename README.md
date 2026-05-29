# Eval Engineer

![Eval Engineer routes Galileo evidence into coding-agent RCA and verification](docs/images/readme-hero.png)

Eval Engineer turns generic coding agents like Codex and Claude Code into
Galileo-backed eval engineers.

Read the launch post:
[Introducing Eval Engineer: Bringing Eval Expertise to Claude and Codex](https://galileo.ai/blog/introducing-eval-engineer-bringing-eval-expertise-to-claude-and-codex).

The idea is simple: coding agents are good at changing code, but AI apps should
not improve by guesswork. They should improve through evidence. Eval Engineer
gives a coding agent the loop it needs to inspect Galileo traces and metrics,
diagnose the failure, make one bounded change, and verify whether the next run
actually improved.

## Quick Installation

Install Eval Engineer into the project you want to debug or improve:

```bash
uvx --from git+https://github.com/Galileo-Agent-Labs/eval-engineer.git \
  eval-engineer install --target both --scope project --project-dir .
```

Project install writes skills into `.agents/skills/eval-*` for Codex and
`.claude/skills/eval-*` for Claude Code. It also prepares a minimal `.galileo/`
workspace without overwriting existing files.

Start a new Claude Code or Codex session from this same project folder after
installing. Codex discovers project skills from `.agents/skills` in the current
directory and its parents; if Codex was opened somewhere else, it will not see
this project's skills.

Claude Code surfaces the skills as slash commands:

```text
/eval-engineer   front door, readiness check, router, and short explanation
/eval-setup      prepare or inspect the .galileo workspace
/eval-fetch      turn Galileo URLs/IDs into local debug packets
/eval-dataset    create, review, accept, or reject eval dataset cases
/eval-measure    choose metrics and expected-output contracts
/eval-diagnose   perform RCA from traces, spans, sessions, and metrics
/eval-cost       reduce cost while protecting quality metrics
/eval-audit      review launch, safety, OWASP, and coverage risk
```

Codex surfaces the same skills as `$` mentions:

```text
$eval-engineer   front door, readiness check, router, and short explanation
$eval-setup      prepare or inspect the .galileo workspace
$eval-fetch      turn Galileo URLs/IDs into local debug packets
$eval-dataset    create, review, accept, or reject eval dataset cases
$eval-measure    choose metrics and expected-output contracts
$eval-diagnose   perform RCA from traces, spans, sessions, and metrics
$eval-cost       reduce cost while protecting quality metrics
$eval-audit      review launch, safety, OWASP, and coverage risk
```

If the skills do not appear, restart the host agent. For Codex, also confirm the
skills were installed under the project you opened:

```bash
find .agents/skills -maxdepth 2 -name SKILL.md | sort
```

The first useful prompt is usually:

```text
$eval-engineer inspect this project and tell me the best next step.
```

In Claude Code, use `/eval-engineer` instead. If you already have Galileo
evidence, start with the artifact you have:

```text
$eval-fetch https://app.galileo.ai/.../log-streams/...
$eval-diagnose .galileo/current/debug-packet.json
$eval-cost compare the baseline and verification packets
```

See `docs/installation.md` for user-scope installs, detailed command behavior,
and plugin packaging guidance.

For global Codex usage, user-scope installs write to
`$CODEX_HOME/skills/eval-*`, defaulting to `~/.codex/skills/eval-*` when
`CODEX_HOME` is not set. Validate that path explicitly with:

```bash
uvx --from git+https://github.com/Galileo-Agent-Labs/eval-engineer.git \
  eval-engineer check --target codex --scope user
```

## Why This Matters

AI failures rarely live in source code alone. The important evidence is often in
tool calls, retrieved context, spans, sessions, metric scores, experiment runs,
or production log streams.

A generic coding agent can edit prompts, tools, retrievers, and configs. What it
does not automatically know is:

- which Galileo artifact to inspect first
- which metric is relevant to the failure
- what that metric proves and does not prove
- whether the fix belongs in the prompt, tool schema, retriever, model config,
  guardrail, dataset, or metric setup
- how to verify that a change improved behavior instead of only sounding better

Eval Engineer adds that missing eval discipline as a portable skill.

## How The Loop Works

Eval Engineer is built around a small, repeatable loop:

<img
  src="docs/images/system-flow.svg"
  alt="Eval Engineer system flow"
  width="100%"
/>

```text
AI app behavior
    -> Galileo traces and metrics
    -> compact debug packet
    -> diagnosis
    -> bounded fix plan
    -> verification run
    -> keep the change only if evidence improves
```

The skill does not start by editing code. It starts by grounding the problem:

1. Identify whether the evidence came from a controlled experiment, production
   log stream, or mixed source.
2. Read the current debug packet.
3. Name the metric contract.
4. Compare expected behavior with actual trace behavior.
5. Choose the fix surface.
6. Propose the smallest useful change.
7. Verify with a fresh local or Galileo run.

This is the practical path toward self-improving agents: not autonomous
rewriting, but measured change retention.

## What The Skill Adds

![Eval Engineer command skills overview](docs/images/skills-overview.png)

The core artifact is the portable skill in
`skills/eval-engineer/`.

The host agent provides repo access, command execution, and code edits. The
skill provides the eval workflow:

- Galileo evidence literacy
- metric selection by failure contract
- root-cause analysis structure
- bounded fix planning
- before/after verification
- durable learnings and candidate eval cases

The skill is intentionally general. The first fixture is a tool-calling support
agent, but Eval Engineer is meant to work across agents, RAG apps, workflows,
providers, experiments, log streams, and custom metrics.

## Repo Structure

This repo separates the reusable skill, the installer, the test fixtures, and
the project notes. The split matters: users install the skill into their own
agent repo, while this repo keeps the reference implementations and regression
tests that make the skill safer to change.

```text
skills/
  eval-engineer/      Shared Galileo workflow, references, templates, scripts.
  eval-setup/         Command skill for preparing or inspecting a repo.
  eval-fetch/         Command skill for Galileo URL and evidence intake.
  eval-dataset/       Command skill for candidate eval dataset cases.
  eval-measure/       Command skill for metric profiles and eval contracts.
  eval-diagnose/      Command skill for RCA from traces, spans, and metrics.
  eval-cost/          Command skill for tokenomics and cost RCA.
  eval-audit/         Command skill for launch, safety, and OWASP review.

src/
  eval_engineer_installer/
                      The `eval-engineer` CLI used by `uvx` installs.

tests/
  agents/             Reference AI apps used to pressure-test the skill.
  skills/             Behavioral tests and packet fixtures for skill logic.
  installer/          Tests for project/user installs and command discovery.

docs/
  installation.md     Detailed install behavior and plugin direction.
  plan.md             Product direction and architecture notes.
  tasks.md            Current checklist and Linear issue mapping.
  progress.md         Running work log and validation evidence.
  images/             README-safe images copied from launch/blog assets.
```

The key design choice is separation of concerns. Galileo stores behavior
evidence. The coding agent edits the repo. The skill connects them through a
repeatable eval loop, with reference fixtures and tests here to keep that loop
from becoming tied to one demo agent.
