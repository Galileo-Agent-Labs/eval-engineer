# Galileo Live Readiness

Use this checklist before calling a Galileo-backed app or fixture ready. A
project shell is not evidence. Eval Engineer needs a populated, scored evidence
source that can be fetched into a debug packet. A project shell is not evidence
by itself.

## Required Status

Report each field as `ready`, `missing`, `running`, `failed`, or `unknown`:

```text
Galileo readiness:
- console URL: ready/missing
- project: ready/missing
- evidence source: log stream/experiment/session/trace/missing
- log stream: ready/missing/not applicable
- traces or spans: ready/missing
- metrics enabled: ready/missing
- scoring or recompute jobs: completed/running/failed/missing
- queryable metric values: ready/missing
- local debug packet provenance: galileo_fetched/local_generated/missing
```

Do not treat the project as ready when only the project exists.

## Log Stream Path

For a log-stream-backed workflow, verify all of the following before RCA:

- Galileo project exists and the project ID is known.
- Log stream exists for the app/feed under test.
- Trace/span records have been uploaded to that log stream.
- Metric or scorer settings are enabled for the log stream.
- Existing records have been scored or a recompute job has been triggered.
- Scorer or recompute jobs have completed without failure.
- A metrics query returns meaningful quality/safety values, not only system,
  token, or cost aggregates.
- The local debug packet includes source metadata for the project and log
  stream.

## Experiment Path

For an experiment-backed workflow, verify:

- Project ID and experiment ID are known.
- The experiment has runs or sessions with trace/span records.
- The experiment metrics match the failure contract.
- Metric results are available for the relevant rows or traces.
- The local debug packet preserves experiment/run/session IDs.

## SDK Version Note

Avoid recommending incompatible SDK families together. `galileo==2.3.0` uses
the modern `galileo-core>=4.3,<5` family, while older `galileo-observe` releases
may require `galileo-core<4`. If setup instructions name packages, name one
compatible SDK path and verify installation before proceeding.

## Stop Conditions

Stop and ask for missing setup details when:

- only a Galileo project URL is available
- no log stream, experiment, session, or trace ID is available
- metrics are not enabled or scorer status is unknown
- recompute is needed for existing records
- the packet provenance is local-only but the user asked for Galileo-backed RCA
