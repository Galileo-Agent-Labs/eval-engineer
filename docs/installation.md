# Installing Eval Engineer Skills

Eval Engineer is distributed as a portable skill bundle first. The shared
knowledge lives under `skills/eval-engineer/`; focused command skills such as
`eval-fetch` and `eval-cost` route users into that shared knowledge instead of
duplicating it.

## Recommended Quick Install

Install into the current project for both Codex and Claude Code:

```bash
uvx --from git+https://github.com/Galileo-Agent-Labs/eval-engineer.git \
  eval-engineer install --target both --scope project --project-dir .
```

That creates:

- `.agents/skills/eval-*` for Codex.
- `.claude/skills/eval-*` for Claude Code.
- `.galileo/` with safe placeholder workspace files if they do not exist.

The command skills are:

| Command | Job |
| --- | --- |
| `/eval-engineer` | Front door, project readiness, routing, and concise education. |
| `/eval-setup` | Prepare or inspect `.galileo/`, config, editable files, and verification commands. |
| `/eval-fetch` | Parse Galileo URLs/IDs and bring evidence into `.galileo/current/debug-packet.json`. |
| `/eval-dataset` | Create, review, accept, or reject `.galileo/eval-dataset/` cases. |
| `/eval-measure` | Define metric profiles and expected-output contracts before optimizing. |
| `/eval-diagnose` | Diagnose root cause from fetched traces, spans, sessions, and metrics. |
| `/eval-cost` | Reduce token, latency, tool, model, retrieval, and evaluator cost while protecting quality. |
| `/eval-audit` | Review launch, safety, OWASP, metric coverage, and production-readiness risks. |

Validate the install:

```bash
uvx --from git+https://github.com/Galileo-Agent-Labs/eval-engineer.git \
  eval-engineer check --target both --scope project --project-dir .
```

Use a user-scope install only when the skill should be available across all
projects:

```bash
uvx --from git+https://github.com/Galileo-Agent-Labs/eval-engineer.git \
  eval-engineer install --target both --scope user
```

User-scope installs write to `$CODEX_HOME/skills/eval-*` for Codex, defaulting
to `~/.codex/skills/eval-*` when `CODEX_HOME` is not set. Claude Code
user-scope installs write to `~/.claude/skills/eval-*`.

Validate a global Codex install with the same environment the Codex session
will use:

```bash
uvx --from git+https://github.com/Galileo-Agent-Labs/eval-engineer.git \
  eval-engineer check --target codex --scope user
```

Use `--force` when intentionally replacing an existing install. Use a tagged Git
ref once releases exist if the install must be reproducible. The install itself
does not require Galileo credentials; credentials are only needed later when a
skill run reads or writes Galileo evidence.

Use `--no-scaffold` if project installation should not create `.galileo/`.

## Real-World URL Intake

Users can start from Galileo console URLs:

```text
https://console.demo-v2.galileocloud.io/agent-labs/project/<project-id>
https://console.demo-v2.galileocloud.io/agent-labs/project/<project-id>/log-streams/<log-stream-id>
https://console.demo-v2.galileocloud.io/agent-labs/project/<project-id>/experiments
```

`/eval-fetch` should parse the URL, preserve source metadata, and ask only for
the missing information. A project URL is broad context; a log stream URL is
actionable but may still need a time window, latest-N traces, failed traces, or
aggregate metrics. An experiments list URL needs a specific experiment or
comparison choice.

## Why This Is Skill-First

Claude Code treats standalone `.claude/skills` as the right path for quick
iteration and project-specific workflows, then recommends plugins when sharing,
versioned releases, or marketplace distribution become important.

Codex uses skills as the authoring format for reusable workflows and plugins as
the installable distribution unit for skills, apps, and MCP integrations.

For Eval Engineer, the reusable object today is a skill bundle with shared
references, scripts, and assets. A `uvx` installer is the lowest-friction path
that works for both Claude Code and Codex without forking the skill.

## Plugin Direction

Plugin packaging should come after the skill installer works well.

Do not create independent skill copies for plugins. Keep `skills/eval-engineer/`
as the shared knowledge source and generate or package the command bundle into:

- a Codex plugin when we need Codex marketplace installation, bundled app
  integrations, MCP servers, or plugin metadata
- a Claude Code plugin when we need namespaced team/community distribution,
  plugin agents, hooks, MCP servers, or versioned marketplace-style releases

Because Claude and Codex plugin manifests differ, publish separate plugins if we
go that route. They should share the same canonical skill source.
