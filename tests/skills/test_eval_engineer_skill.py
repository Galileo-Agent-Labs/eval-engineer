#!/usr/bin/env python3
"""Behavior checks for the Galileo Eval Engineer skill."""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / "skills" / "eval-engineer"
SUMMARIZER = SKILL_DIR / "scripts" / "summarize_debug_packet.py"
TOKENOMICS_COMPARE = SKILL_DIR / "scripts" / "compare_tokenomics_packets.py"
URL_PARSER = SKILL_DIR / "scripts" / "parse_galileo_url.py"
LOG_STREAM_FETCHER = SKILL_DIR / "scripts" / "fetch_log_stream_packet.py"
ASSETS_DIR = SKILL_DIR / "assets"
TOKENOMICS_SCENARIOS = ROOT / "tests" / "skills" / "fixtures" / "tokenomics-scenarios.json"
COMMAND_SKILLS = [
    "eval-engineer",
    "eval-setup",
    "eval-fetch",
    "eval-dataset",
    "eval-measure",
    "eval-diagnose",
    "eval-cost",
    "eval-audit",
]


def _load_summarizer():
    spec = importlib.util.spec_from_file_location("summarize_debug_packet", SUMMARIZER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_tokenomics_compare():
    spec = importlib.util.spec_from_file_location("compare_tokenomics_packets", TOKENOMICS_COMPARE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_url_parser():
    spec = importlib.util.spec_from_file_location("parse_galileo_url", URL_PARSER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_log_stream_fetcher():
    spec = importlib.util.spec_from_file_location("fetch_log_stream_packet", LOG_STREAM_FETCHER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _tokenomics_scenario(name: str) -> dict:
    scenarios = json.loads(TOKENOMICS_SCENARIOS.read_text(encoding="utf-8"))
    return scenarios[name]


class EvalEngineerSkillTest(unittest.TestCase):
    def test_command_skills_are_distinct_and_share_core_references(self) -> None:
        descriptions = {}
        for skill_name in COMMAND_SKILLS:
            skill_path = ROOT / "skills" / skill_name / "SKILL.md"
            self.assertTrue(skill_path.is_file(), skill_path)
            text = skill_path.read_text(encoding="utf-8")
            self.assertIn(f"name: {skill_name}", text)
            match = re.search(r"^description:\s*(.+)$", text, flags=re.MULTILINE)
            self.assertIsNotNone(match, skill_name)
            description = match.group(1).strip()
            self.assertLessEqual(len(description), 260)
            descriptions[skill_name] = description

        self.assertEqual(len(set(descriptions.values())), len(COMMAND_SKILLS))

        expectations = {
            "eval-engineer": [
                "front door",
                "route",
                "Current Project State",
                "/eval-dataset",
                "galileo-integration-intake.md",
                "hosted Galileo evidence used",
            ],
            "eval-setup": [
                ".galileo/config.yml",
                "Do not guess metrics",
                "/eval-diagnose",
                "galileo-integration-intake.md",
                "missing Galileo integration inputs",
            ],
            "eval-fetch": [
                "Galileo URL",
                "source.console_url",
                "project URL",
                "fetch_ready: true",
                "fetch_log_stream_packet.py",
                "Do not print secret values",
                "## Gotchas",
                "## Validation Loop",
            ],
            "eval-dataset": [
                "references/eval-datasets.md",
                ".galileo/eval-dataset/candidates.jsonl",
                "Follow the user-provided schema",
                "Do not promote",
                "Do not force Eval Engineer fields",
                "changelog.md",
                "## Validation Loop",
            ],
            "eval-measure": ["metric-profile-checklist.md", "expected-output contract", "Findings first"],
            "eval-diagnose": [
                "rca-recipe.md",
                "evidence-provenance.md",
                "fix surface",
                "Honor read-only requests",
                "Unless the request is read-only",
                "## Gotchas",
                "## Validation Loop",
            ],
            "eval-cost": [
                "tokenomics-rca.md",
                "quality metrics do not regress",
                "behavior counters",
                "Load `skills/eval-engineer/references/tokenomics-rca.md` when",
                "## Gotchas",
                "## Validation Loop",
            ],
            "eval-audit": ["OWASP", "Do not fix by default", "Do not read secret values"],
        }
        for skill_name, required_terms in expectations.items():
            text = (ROOT / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
            for term in required_terms:
                self.assertIn(term, text, f"{term} missing from {skill_name}")

    def test_eval_setup_requires_live_galileo_readiness_checks(self) -> None:
        setup_text = (ROOT / "skills" / "eval-setup" / "SKILL.md").read_text(encoding="utf-8")
        reference = SKILL_DIR / "references" / "galileo-live-readiness.md"
        self.assertTrue(reference.is_file(), reference)
        reference_text = reference.read_text(encoding="utf-8")

        required_setup_terms = [
            "galileo-live-readiness.md",
            "metrics enabled",
            "scorer/recompute job",
            "queryable metric values",
            "Do not call a Galileo project ready when only the project exists",
        ]
        for term in required_setup_terms:
            self.assertIn(term, setup_text)

        required_reference_terms = [
            "A project shell is not evidence",
            "log stream",
            "traces or spans",
            "metrics enabled",
            "scoring or recompute jobs",
            "queryable metric values",
            "galileo_fetched/local_generated/missing",
        ]
        for term in required_reference_terms:
            self.assertIn(term, reference_text)

    def test_eval_engineer_requires_evidence_provenance_labels(self) -> None:
        skill_text = (ROOT / "skills" / "eval-engineer" / "SKILL.md").read_text(encoding="utf-8")
        diagnose_text = (ROOT / "skills" / "eval-diagnose" / "SKILL.md").read_text(encoding="utf-8")
        installer_text = (ROOT / "src" / "eval_engineer_installer" / "cli.py").read_text(
            encoding="utf-8"
        )
        reference = SKILL_DIR / "references" / "evidence-provenance.md"
        self.assertTrue(reference.is_file(), reference)
        reference_text = reference.read_text(encoding="utf-8")

        for term in [
            "evidence-provenance.md",
            "Evidence provenance:",
            "hosted Galileo evidence used: yes/no",
            "score source: galileo_fetched/local_existing/local_generated/mixed/unknown",
            "missing before Galileo-backed claim: none/<specific IDs or metrics>",
            "A packet under `.galileo/` is not automatically hosted Galileo evidence",
            "Do not create or rely on a new local eval harness",
        ]:
            self.assertIn(term, skill_text)

        self.assertIn("evidence-provenance.md", diagnose_text)
        self.assertIn("local deterministic packets", diagnose_text)

        for term in [
            "galileo_fetched",
            "local_existing",
            "local_generated",
            "Evidence provenance:",
            "missing before Galileo-backed claim: none/<specific IDs or metrics>",
            "Galileo evidence has not been fetched",
            "Do not create a new eval harness",
        ]:
            self.assertIn(term, reference_text)

        self.assertIn('"references/evidence-provenance.md"', installer_text)

    def test_project_skill_links_cover_all_command_skills(self) -> None:
        for skill_root in (ROOT / ".agents" / "skills", ROOT / ".claude" / "skills"):
            if not skill_root.is_dir():
                continue
            for skill_name in COMMAND_SKILLS:
                link = skill_root / skill_name
                self.assertTrue(link.is_symlink(), f"{link} should be a skill symlink")
                self.assertEqual(
                    link.readlink(),
                    Path("..") / ".." / "skills" / skill_name,
                    f"{link} should point at the canonical skill source",
                )

    def test_front_door_description_stays_router_focused(self) -> None:
        text = (ROOT / "skills" / "eval-engineer" / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"^description:\s*(.+)$", text, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        description = match.group(1)

        self.assertIn("unsure which Eval Engineer command", description)
        self.assertIn("onboarding", description)
        self.assertNotIn("trace IDs", description)
        self.assertNotIn("log stream IDs", description)
        self.assertNotIn("production symptoms", description)

    def test_eval_engineer_requires_galileo_integration_intake_before_local_evidence(self) -> None:
        core = (ROOT / "skills" / "eval-engineer" / "SKILL.md").read_text(encoding="utf-8")
        setup = (ROOT / "skills" / "eval-setup" / "SKILL.md").read_text(encoding="utf-8")
        installer_cli = (ROOT / "src" / "eval_engineer_installer" / "cli.py").read_text(
            encoding="utf-8"
        )
        reference_path = SKILL_DIR / "references" / "galileo-integration-intake.md"
        reference = reference_path.read_text(encoding="utf-8")

        self.assertIn("references/galileo-integration-intake.md", installer_cli)
        self.assertIn("hosted Galileo evidence used", core)
        self.assertIn("missing Galileo inputs", core)
        self.assertIn("local-only workflow confirmed", core)
        self.assertIn("before creating local evidence", core)
        self.assertIn("scripts/evaluate_*", setup)

        required_terms = [
            "Required Inputs",
            "GALILEO_CONSOLE_URL",
            "project URL or project ID",
            "log stream URL/ID",
            "experiment URL/ID",
            "session ID",
            "trace ID",
            "metric/scorer names",
            "GALILEO_API_KEY",
            "Do Not Substitute",
            "evidence-provenance.md",
            "local-only evaluation",
        ]
        for term in required_terms:
            self.assertIn(term, reference, f"{term} missing from {reference_path}")

    def test_galileo_url_parser_handles_console_urls(self) -> None:
        module = _load_url_parser()

        log_stream = module.parse_galileo_url(
            "https://console.demo-v2.galileocloud.io/agent-labs/project/"
            "555caaf8-8a6b-4f15-96bd-2b4e334ca90d/log-streams/"
            "214f2b90-72a4-4e0e-81ae-b096e2fd612c"
        )
        self.assertEqual(log_stream["artifact_type"], "log_stream")
        self.assertEqual(log_stream["console_host"], "console.demo-v2.galileocloud.io")
        self.assertEqual(log_stream["workspace_slug"], "agent-labs")
        self.assertEqual(log_stream["project_id"], "555caaf8-8a6b-4f15-96bd-2b4e334ca90d")
        self.assertEqual(log_stream["log_stream_id"], "214f2b90-72a4-4e0e-81ae-b096e2fd612c")
        self.assertTrue(log_stream["fetch_ready"])

        project = module.parse_galileo_url(
            "https://console.demo-v2.galileocloud.io/agent-labs/project/"
            "555caaf8-8a6b-4f15-96bd-2b4e334ca90d"
        )
        self.assertEqual(project["artifact_type"], "project")
        self.assertFalse(project["fetch_ready"])
        self.assertIn("log stream", project["next_questions"][0])

        experiments = module.parse_galileo_url(
            "https://console.demo-v2.galileocloud.io/agent-labs/project/"
            "555caaf8-8a6b-4f15-96bd-2b4e334ca90d/experiments"
        )
        self.assertEqual(experiments["artifact_type"], "experiments_index")
        self.assertFalse(experiments["fetch_ready"])
        self.assertIn("specific experiment", " ".join(experiments["next_questions"]))

    def test_eval_dataset_skill_requires_claimed_source_gates_in_fields(self) -> None:
        text = (ROOT / "skills" / "eval-dataset" / "SKILL.md").read_text(encoding="utf-8")
        reference = (SKILL_DIR / "references" / "eval-datasets.md").read_text(encoding="utf-8")

        self.assertIn("references/eval-datasets.md", text)
        self.assertIn("Follow the user-provided schema", text)
        self.assertIn("Do not force Eval Engineer fields", text)
        self.assertIn("If notes or summaries name a forbidden source", reference)
        self.assertIn("Only add `forbidden_retrieved_sources`", reference)

    def test_eval_dataset_reference_bootstraps_metric_caught_failure_cases(self) -> None:
        reference = SKILL_DIR / "references" / "eval-datasets.md"
        self.assertTrue(reference.is_file(), reference)
        text = reference.read_text(encoding="utf-8")

        required_terms = [
            "Bootstrap By Use Case",
            "RAG",
            "tool-calling agent",
            "multi-turn",
            "Failure Trigger",
            "Metric That Should Catch It",
            "prompt_injection",
            "output_pii",
            "context_relevance",
            "tool_selection_quality",
            "agentic_workflow_success",
            "forbidden_retrieved_sources",
        ]
        for term in required_terms:
            self.assertIn(term, text)

    def test_eval_dataset_reference_allows_user_or_existing_schema(self) -> None:
        text = (SKILL_DIR / "references" / "eval-datasets.md").read_text(encoding="utf-8")

        required_terms = [
            "Schema Precedence",
            "user-provided schema",
            "existing Galileo dataset schema",
            "Do not force Eval Engineer fields",
            "Optional Review Metadata",
            "Minimal Galileo Upload",
            "schema_overrides",
            "only when",
        ]
        for term in required_terms:
            self.assertIn(term, text)

    def test_eval_dataset_reference_documents_galileo_sdk_dataset_usage(self) -> None:
        text = (SKILL_DIR / "references" / "eval-datasets.md").read_text(encoding="utf-8")

        required_terms = [
            "Galileo SDK Usage",
            "from galileo.datasets import create_dataset, get_dataset, list_datasets",
            "from galileo.experiments import run_experiment",
            "create_dataset(",
            "get_dataset(",
            "dataset.add_rows(",
            "list_datasets(",
            "run_experiment(",
            "dataset_name=",
            '"generated_output"',
            '"ground_truth"',
            '"metadata"',
            "metadata values must be strings",
            '"output"',
            "function experiments in `galileo==1.39.0`",
            "requested scorer aggregates may be absent",
            "dataset version",
            "Do not put secret values",
        ]
        for term in required_terms:
            self.assertIn(term, text)

    def test_log_stream_fetcher_aggregates_scorer_metrics_from_records(self) -> None:
        module = _load_log_stream_fetcher()

        class Response:
            def __init__(self, records: list[dict]) -> None:
                self.records = records

        module.get_traces = lambda *args, **kwargs: Response(
            [
                {
                    "id": "trace-row-1",
                    "trace_id": "trace-1",
                    "name": "failed privacy case",
                    "metrics": {
                        "context_adherence": 0.25,
                        "context_adherence_status": "success",
                        "context_adherence_rationale": "Missed the policy source.",
                        "context_adherence_ems_error_code": 2013,
                        "tool_error_rate": 0.0,
                    },
                },
                {
                    "id": "trace-row-2",
                    "trace_id": "trace-2",
                    "name": "passing case",
                    "metrics": {
                        "context_adherence": 0.75,
                        "context_adherence_status": "success",
                        "tool_error_rate": 0.5,
                    },
                },
            ]
        )
        module.get_spans = lambda *args, **kwargs: Response(
            [
                {
                    "id": "span-1",
                    "trace_id": "trace-1",
                    "type": "llm",
                    "name": "answer",
                    "model": "test-model",
                    "input": "{\"question\": \"q\"}",
                    "output": "answer",
                    "metrics": {"num_input_tokens": 100, "cost": 0.02},
                },
                {
                    "id": "span-2",
                    "trace_id": "trace-2",
                    "type": "retriever",
                    "name": "search",
                    "metrics": {"duration_ns": 1000},
                },
            ]
        )
        module.get_sessions = lambda *args, **kwargs: Response([{"id": "session-1", "name": "session"}])

        packet = module.build_packet(
            project_id="project-123",
            log_stream_id="log-stream-456",
            limit=20,
            source={"console_url": "https://console.example/project/project-123/log-streams/log-stream-456"},
        )

        self.assertEqual(packet["source_type"], "log_stream")
        self.assertEqual(packet["source"]["log_stream_id"], "log-stream-456")
        self.assertEqual(packet["aggregate_metrics"]["average_context_adherence"], 0.5)
        self.assertEqual(packet["aggregate_metrics"]["average_tool_error_rate"], 0.25)
        self.assertNotIn("average_context_adherence_ems_error_code", packet["aggregate_metrics"])
        self.assertNotIn("context_adherence_ems_error_code", packet["scorer_metrics"])
        self.assertEqual(packet["aggregate_metrics"]["average_num_input_tokens"], 100)
        self.assertEqual(packet["aggregate_metrics"]["average_cost"], 0.02)
        self.assertEqual(packet["aggregate_metrics"]["total_responses"], 2)
        self.assertEqual(packet["scorer_metrics"]["context_adherence"]["success"], 2)
        self.assertEqual(packet["metric_fetch_status"], "ok")
        self.assertIn("context_adherence", packet["traces"][0]["scores"])

    def test_log_stream_fetcher_marks_missing_scorer_metrics(self) -> None:
        module = _load_log_stream_fetcher()

        class Response:
            def __init__(self, records: list[dict]) -> None:
                self.records = records

        module.get_traces = lambda *args, **kwargs: Response([{"trace_id": "trace-1", "metrics": {}}])
        module.get_spans = lambda *args, **kwargs: Response([{"id": "span-1", "type": "llm", "metrics": {}}])
        module.get_sessions = lambda *args, **kwargs: Response([])

        packet = module.build_packet(project_id="project-123", log_stream_id="log-stream-456", limit=20)

        self.assertEqual(packet["metric_fetch_status"], "missing_metric_results")
        self.assertEqual(packet["aggregate_metrics"]["total_responses"], 1)
        self.assertEqual(packet["scorer_metrics"], {})

    def test_skill_description_is_portable(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"^description:\s*(.+)$", skill_text, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        description = match.group(1).strip()
        self.assertLessEqual(len(description), 200)
        self.assertIn("AI agents/RAG apps", description)

    def test_skill_does_not_hardcode_reference_fixture(self) -> None:
        banned_terms = [
            "TC-1",
            "tool-calling-support",
            "Brazil",
            "wire_transfer",
            "claude-sonnet-4-6",
        ]
        for path in SKILL_DIR.rglob("*"):
            if path.is_file() and not path.name.startswith("."):
                text = path.read_text(encoding="utf-8")
                for term in banned_terms:
                    self.assertNotIn(term, text, f"{term} leaked into {path}")

    def test_skill_names_baseline_and_verification_packets(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn(".galileo/current/debug-packet.json", skill_text)
        self.assertIn(".galileo/current/verification-debug-packet.json", skill_text)
        self.assertIn("debug-packet-after.json", skill_text)
        self.assertIn("log streams", skill_text)

    def test_summarizer_handles_generic_rag_packet(self) -> None:
        module = _load_summarizer()
        packet_path = ROOT / "tests" / "skills" / "fixtures" / "generic-rag-debug-packet.json"
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        summary = module.summarize(packet)

        self.assertIn("agent_type: rag", summary)
        self.assertIn("groundedness: 0.42", summary)
        self.assertIn("expected:", summary)
        self.assertIn("actual:", summary)
        self.assertIn("trace-rag-001", summary)

    def test_summarizer_handles_generic_tool_calling_packet(self) -> None:
        module = _load_summarizer()
        packet_path = ROOT / "tests" / "skills" / "fixtures" / "generic-tool-calling-debug-packet.json"
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        summary = module.summarize(packet)

        self.assertIn("agent_type: tool_calling", summary)
        self.assertIn("tool_selection_quality: 0.44", summary)
        self.assertIn("update_crm_record", summary)
        self.assertIn("send_email", summary)
        self.assertIn("trace-tool-001", summary)

    def test_artifact_templates_preserve_grounded_rca_shape(self) -> None:
        expected = {
            "diagnosis-template.md": [
                "RCA Summary",
                "Evidence Source",
                "Evidence Links",
                "Metric Contract",
                "Failure Pattern",
                "Expected Versus Actual",
                "Metric Reading",
                "Uncertainty",
                "Debug packet",
                "Verification packet",
                "Trace IDs",
                "Span IDs",
                "Metrics",
            ],
            "fix-plan-template.md": [
                "Bounded Change",
                "Fix Surface",
                "Evidence Behind The Change",
                "Metric Contract",
                "Editable Files",
                "Non-Goals",
                "Risk",
            ],
            "verification-plan-template.md": [
                "Baseline",
                "Evidence Source",
                "Commands",
                "Verification Mode",
                "Galileo Comparison",
                "Regression Check",
                "Success Criteria",
                "Follow-Up",
                "verification-debug-packet.json",
                "log-stream-origin RCA",
                "metrics",
                "traces",
            ],
        }

        for filename, required_terms in expected.items():
            text = (ASSETS_DIR / filename).read_text(encoding="utf-8")
            for term in required_terms:
                self.assertIn(term, text, f"{term} missing from {filename}")

    def test_rca_recipe_captures_galileo_learning_loop(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        recipe_text = (SKILL_DIR / "references" / "rca-recipe.md").read_text(encoding="utf-8")

        self.assertIn("references/rca-recipe.md", skill_text)

        required_terms = [
            "Start From Fetched Evidence",
            "Name The Metric Contract",
            "Classify The Fix Surface",
            "Prove One Narrow Improvement",
            "Preserve The Learning",
            "controlled experiment",
            "production log stream",
            "mixed",
            "retriever, ranker, query rewrite, or chunking",
            "deterministic guardrail",
            "adapter or SDK wiring",
            "custom metric or rubric",
            "Choose verification mode from the evidence source",
            "metric/eval gap",
        ]
        for term in required_terms:
            self.assertIn(term, recipe_text)

    def test_galileo_sources_reference_covers_experiments_and_log_streams(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        source_text = (SKILL_DIR / "references" / "galileo-sources.md").read_text(encoding="utf-8")

        self.assertIn("references/galileo-sources.md", skill_text)

        required_terms = [
            "experiments for controlled sample evals",
            "log streams for production or live-traffic RCA",
            "Normalize both into the same debug-packet contract",
            "Production evidence should often become future controlled evals",
        ]
        for term in required_terms:
            self.assertIn(term, source_text)

    def test_metrics_reference_is_not_agent_metric_only(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        metrics_text = (SKILL_DIR / "references" / "metrics.md").read_text(encoding="utf-8")

        self.assertIn("references/metrics.md", skill_text)

        required_terms = [
            "choose metrics from the failure contract",
            "case-specific metric profile",
            "full expected-output contract",
            "Response Quality",
            "RAG And Context Use",
            "Safety, Security, And Style",
            "SQL",
            "Vision",
            "Custom Metrics",
            "fixture-specific, not a general recommendation",
        ]
        for term in required_terms:
            self.assertIn(term, metrics_text)

    def test_metric_profile_checklist_is_discoverable(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        checklist_text = (SKILL_DIR / "references" / "metric-profile-checklist.md").read_text(encoding="utf-8")
        template_text = (ASSETS_DIR / "metric-profile-template.md").read_text(encoding="utf-8")

        self.assertIn("references/metric-profile-checklist.md", skill_text)
        self.assertIn("assets/metric-profile-template.md", skill_text)
        self.assertIn("references/metric-profile-checklist.md", (SKILL_DIR / "references" / "tokenomics-rca.md").read_text(encoding="utf-8"))

        required_terms = [
            "Do not optimize cost before this checklist is complete",
            "risk_profile",
            "quality_dimensions",
            "galileo_metrics",
            "expected_decision",
            "required_citations",
            "forbidden_citations",
            "required_tools",
            "forbidden_answer_terms",
            "must_abstain",
            "Safety And Compliance",
            "RAG Grounding",
            "Agent Performance",
            "Cost And Latency",
            "segment-level acceptance gate",
            "metric gap",
        ]
        for term in required_terms:
            self.assertIn(term, checklist_text)

        template_terms = [
            "Case Or Segment",
            "Risk Profile",
            "Expected Output Contract",
            "Metric Profile",
            "Acceptance Gate",
            "Cost Metrics",
            "Missing Metrics",
        ]
        for term in template_terms:
            self.assertIn(term, template_text)

    def test_tokenomics_subskill_is_discoverable_and_general(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        tokenomics_text = (SKILL_DIR / "references" / "tokenomics-rca.md").read_text(encoding="utf-8")

        self.assertIn("references/tokenomics-rca.md", skill_text)
        self.assertIn("assets/cost-diagnosis-template.md", skill_text)
        self.assertIn("assets/tokenomics-fix-plan-template.md", skill_text)
        self.assertIn("assets/quality-preserving-verification-template.md", skill_text)

        required_terms = [
            "RAG",
            "agent",
            "average_cost",
            "average_latency",
            "average_num_input_tokens",
            "multi-hop",
            "case-level",
            "retriever",
            "tool",
            "model routing",
            "metric sampling",
            "segment",
            "agent steps",
            "rerank",
            "self-check",
            "agent tool loops",
            "evaluator cost",
            "quality metrics do not regress",
            "Do not rely on local deterministic scoring alone",
            "lower-is-better",
            "traffic volume",
            "scripts/compare_tokenomics_packets.py",
        ]
        for term in required_terms:
            self.assertIn(term, tokenomics_text)

    def test_tokenomics_templates_preserve_quality_gate_shape(self) -> None:
        expected = {
            "cost-diagnosis-template.md": [
                "Cost Signals",
                "Quality Contract",
                "Cost Driver",
                "Evidence Links",
                "Uncertainty",
            ],
            "tokenomics-fix-plan-template.md": [
                "Bounded Change",
                "Evidence Behind The Change",
                "Quality Guardrail",
                "Expected Cost Movement",
                "Rollback Criteria",
            ],
            "quality-preserving-verification-template.md": [
                "Cost Comparison",
                "Quality Gates",
                "Go No-Go",
                "cost delta",
                "quality metric delta",
            ],
        }

        for filename, required_terms in expected.items():
            text = (ASSETS_DIR / filename).read_text(encoding="utf-8")
            for term in required_terms:
                self.assertIn(term, text, f"{term} missing from {filename}")

    def test_tokenomics_compare_keeps_when_cost_improves_and_quality_holds(self) -> None:
        module = _load_tokenomics_compare()
        baseline = {
            "experiment_name": "baseline",
            "aggregate_metrics": {
                "average_cost": 10.0,
                "average_latency": 100.0,
                "average_num_input_tokens": 1000.0,
                "average_tool_selection_quality": 0.8,
            },
        }
        verification = {
            "experiment_name": "verification",
            "aggregate_metrics": {
                "average_cost": 6.0,
                "average_latency": 70.0,
                "average_num_input_tokens": 700.0,
                "average_tool_selection_quality": 0.8,
            },
        }

        result = module.compare(baseline, verification, ["average_tool_selection_quality"])

        self.assertEqual(result["decision"], "keep-candidate: cost evidence improved and quality did not regress")
        self.assertEqual(result["cost"]["average_cost"]["delta"], -4.0)
        self.assertEqual(result["quality"]["average_tool_selection_quality"]["delta"], 0.0)

    def test_tokenomics_compare_infers_custom_quality_metrics_when_omitted(self) -> None:
        module = _load_tokenomics_compare()
        baseline = {
            "run_name": "claim-triage-baseline",
            "aggregate_metrics": {
                "average_cost": 0.000050,
                "average_num_input_tokens": 220.0,
                "average_case_success": 0.0,
                "average_source_authority": 0.5,
                "average_permission_safety": 0.67,
                "average_wall_time_ns": 1000.0,
            },
        }
        verification = {
            "run_name": "claim-triage-post",
            "aggregate_metrics": {
                "average_cost": 0.000045,
                "average_num_input_tokens": 180.0,
                "average_case_success": 1.0,
                "average_source_authority": 1.0,
                "average_permission_safety": 1.0,
                "average_wall_time_ns": 800.0,
            },
        }

        result = module.compare(baseline, verification, [])

        self.assertEqual(result["decision"], "keep-candidate: cost evidence improved and quality did not regress")
        self.assertIn("average_case_success", result["quality"])
        self.assertIn("average_source_authority", result["quality"])
        self.assertNotIn("average_num_input_tokens", result["quality"])
        self.assertNotIn("average_wall_time_ns", result["quality"])

    def test_tokenomics_compare_does_not_infer_handoff_counts_as_quality(self) -> None:
        module = _load_tokenomics_compare()
        baseline = {
            "run_name": "handoff-baseline",
            "aggregate_metrics": {
                "average_cost": 0.002,
                "average_num_total_tokens": 800.0,
                "average_handoff_count": 1.0,
                "average_case_success": 1.0,
            },
        }
        verification = {
            "run_name": "handoff-verification",
            "aggregate_metrics": {
                "average_cost": 0.001,
                "average_num_total_tokens": 600.0,
                "average_handoff_count": 0.0,
                "average_case_success": 1.0,
            },
        }

        result = module.compare(baseline, verification, [])

        self.assertEqual(result["decision"], "keep-candidate: cost evidence improved and quality did not regress")
        self.assertIn("average_handoff_count", result["cost"])
        self.assertNotIn("average_handoff_count", result["quality"])
        self.assertEqual(result["cost"]["average_handoff_count"]["classification"], "efficiency")

    def test_tokenomics_compare_rejects_when_higher_is_better_quality_drops(self) -> None:
        module = _load_tokenomics_compare()
        baseline = {
            "experiment_name": "baseline",
            "aggregate_metrics": {
                "average_cost": 10.0,
                "average_groundedness": 0.95,
            },
        }
        verification = {
            "experiment_name": "verification",
            "aggregate_metrics": {
                "average_cost": 6.0,
                "average_groundedness": 0.80,
            },
        }

        result = module.compare(baseline, verification, ["average_groundedness"])

        self.assertEqual(result["decision"], "reject: quality regressed")
        self.assertEqual(result["quality"]["average_groundedness"]["delta"], -0.1499999999999999)

    def test_tokenomics_compare_keeps_when_lower_is_better_quality_improves(self) -> None:
        module = _load_tokenomics_compare()
        baseline = {
            "experiment_name": "baseline",
            "aggregate_metrics": {
                "average_cost": 10.0,
                "tool_error_rate": 0.20,
            },
        }
        verification = {
            "experiment_name": "verification",
            "aggregate_metrics": {
                "average_cost": 6.0,
                "tool_error_rate": 0.05,
            },
        }

        result = module.compare(baseline, verification, ["tool_error_rate"])

        self.assertEqual(result["decision"], "keep-candidate: cost evidence improved and quality did not regress")
        self.assertEqual(result["quality"]["tool_error_rate"]["direction"], "lower_is_better")

    def test_tokenomics_compare_rejects_when_lower_is_better_quality_increases(self) -> None:
        module = _load_tokenomics_compare()
        baseline = {
            "experiment_name": "baseline",
            "aggregate_metrics": {
                "average_cost": 10.0,
                "tool_error_rate": 0.05,
            },
        }
        verification = {
            "experiment_name": "verification",
            "aggregate_metrics": {
                "average_cost": 6.0,
                "tool_error_rate": 0.20,
            },
        }

        result = module.compare(baseline, verification, ["tool_error_rate"])

        self.assertEqual(result["decision"], "reject: quality regressed")
        self.assertEqual(result["quality"]["tool_error_rate"]["direction"], "lower_is_better")

    def test_tokenomics_compare_is_inconclusive_when_only_traffic_volume_drops(self) -> None:
        module = _load_tokenomics_compare()
        baseline = {
            "experiment_name": "baseline",
            "aggregate_metrics": {
                "total_responses": 100.0,
                "average_completeness_gpt": 1.0,
            },
        }
        verification = {
            "experiment_name": "verification",
            "aggregate_metrics": {
                "total_responses": 50.0,
                "average_completeness_gpt": 1.0,
            },
        }

        result = module.compare(baseline, verification, ["average_completeness_gpt"])

        self.assertEqual(result["decision"], "inconclusive: quality held but efficiency evidence did not improve")
        self.assertEqual(result["cost"]["total_responses"]["classification"], "traffic_or_volume")

    def test_tokenomics_compare_renders_small_cost_values_readably(self) -> None:
        module = _load_tokenomics_compare()
        baseline = {
            "experiment_name": "baseline",
            "aggregate_metrics": {
                "average_cost": 0.00003985,
                "average_latency": 18_672_583.333333332,
                "average_completeness_gpt": 1.0,
            },
        }
        verification = {
            "experiment_name": "verification",
            "aggregate_metrics": {
                "average_cost": 0.0000235,
                "average_latency": 8_919_805.5,
                "average_completeness_gpt": 1.0,
            },
        }

        result = module.compare(baseline, verification, ["average_completeness_gpt"])
        markdown = module.render_markdown(result)

        self.assertIn("3.985e-05", markdown)
        self.assertIn("2.35e-05", markdown)
        self.assertNotIn("0.000000", markdown)

    def test_tokenomics_compare_agent_tool_loop_uses_span_and_retry_efficiency(self) -> None:
        module = _load_tokenomics_compare()
        scenario = _tokenomics_scenario("agent_tool_loop")

        result = module.compare(
            scenario["baseline"],
            scenario["verification"],
            scenario["quality_metrics"],
        )

        self.assertEqual(result["decision"], "keep-candidate: cost evidence improved and quality did not regress")
        self.assertEqual(result["cost"]["average_llm_span_count"]["classification"], "efficiency")
        self.assertEqual(result["cost"]["average_tool_call_count"]["delta"], -4.0)
        self.assertEqual(result["cost"]["average_retry_count"]["delta"], -1.5)
        self.assertEqual(result["quality"]["tool_error_rate"]["direction"], "lower_is_better")

    def test_tokenomics_compare_agentic_rag_uses_agent_step_efficiency(self) -> None:
        module = _load_tokenomics_compare()
        baseline = {
            "run_name": "baseline",
            "aggregate_metrics": {
                "average_agent_steps": 6.0,
                "average_rerank_count": 1.0,
                "average_self_check_count": 1.0,
                "average_case_success": 1.0,
            },
        }
        verification = {
            "run_name": "adaptive",
            "aggregate_metrics": {
                "average_agent_steps": 5.0,
                "average_rerank_count": 0.75,
                "average_self_check_count": 0.75,
                "average_case_success": 1.0,
            },
        }

        result = module.compare(baseline, verification, ["average_case_success"])

        self.assertEqual(result["decision"], "keep-candidate: cost evidence improved and quality did not regress")
        self.assertEqual(result["cost"]["average_agent_steps"]["classification"], "efficiency")
        self.assertEqual(result["cost"]["average_rerank_count"]["delta"], -0.25)
        self.assertEqual(result["cost"]["average_self_check_count"]["delta"], -0.25)

    def test_tokenomics_compare_rejects_rag_pruning_quality_regression(self) -> None:
        module = _load_tokenomics_compare()
        scenario = _tokenomics_scenario("rag_pruning_regression")

        result = module.compare(
            scenario["baseline"],
            scenario["verification"],
            scenario["quality_metrics"],
        )

        self.assertEqual(result["decision"], "reject: quality regressed")
        self.assertEqual(result["cost"]["average_retrieved_context_tokens"]["classification"], "efficiency")
        self.assertLess(result["quality"]["average_completeness_gpt"]["delta"], 0)

    def test_tokenomics_compare_keeps_evaluator_sampling_cost_reduction(self) -> None:
        module = _load_tokenomics_compare()
        scenario = _tokenomics_scenario("evaluator_sampling")

        result = module.compare(
            scenario["baseline"],
            scenario["verification"],
            scenario["quality_metrics"],
        )

        self.assertEqual(result["decision"], "keep-candidate: cost evidence improved and quality did not regress")
        self.assertEqual(result["cost"]["average_evaluator_cost"]["delta"], -0.006)
        self.assertEqual(result["cost"]["metric_sampling_rate"]["classification"], "efficiency")

    def test_tokenomics_compare_keeps_model_routing_when_quality_holds(self) -> None:
        module = _load_tokenomics_compare()
        scenario = _tokenomics_scenario("model_routing")

        result = module.compare(
            scenario["baseline"],
            scenario["verification"],
            scenario["quality_metrics"],
        )

        self.assertEqual(result["decision"], "keep-candidate: cost evidence improved and quality did not regress")
        self.assertEqual(result["cost"]["average_premium_model_span_count"]["delta"], -2.0)

    def test_tokenomics_compare_rejects_hidden_segment_quality_regression(self) -> None:
        module = _load_tokenomics_compare()
        scenario = _tokenomics_scenario("hidden_segment_regression")

        result = module.compare(
            scenario["baseline"],
            scenario["verification"],
            scenario["quality_metrics"],
        )

        self.assertEqual(result["decision"], "reject: quality regressed")
        self.assertIn("enterprise", result["segments"])
        self.assertLess(
            result["segments"]["enterprise"]["quality"]["average_completeness_gpt"]["delta"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
