# Layer 4 — Decision, Recovery & AI Explanation

Scope: **only** Layer 4 of the industrial AI platform. Layers 1, 2A, 2B, 3,
the Digital Twin implementation, the dashboard and the Developer Workspace
are out of scope and not touched here.

## What's in this package

```
layer4/
  models.py           Data contracts for every input/output object
  config.py            IndustryConfig: compatibility, capacity, flow, timers
  interfaces.py         Protocols Layer 4 expects from Layers 1/2A/2B/3 + operator
  timer_manager.py      Configurable, clock-injectable human-correction timer
  recovery_engine.py    The rule-based scheduler (steps 1-8 from the spec)
  explanation.py        AI Alert Explanation — verified-data-only, no invention
  logger.py             Structured event log (fault, timer, decision, what-if...)
  backend.py            Layer4Backend — the one clean facade for the dashboard
  mock_sources.py        Fakes for Layers 1/2A/2B/3, for demo/tests ONLY
demo.py                 Runnable end-to-end demo (3 scenarios)
test_layer4.py          Lightweight assertions covering the core rules
```

## The recovery flow (exactly as specified)

1. **Detect** — a `FaultEvent` arrives from Layer 2A.
2. **Notify** — `OperatorNotifier.notify_fault(...)` is called.
3. **Start timer** — `CorrectionTimerManager` starts a per-machine countdown,
   duration taken from `IndustryConfig.human_correction_timeout_seconds`.
4. **Human corrects in time** — host calls
   `Layer4Backend.report_human_correction(machine_id)`. Machine stays active,
   decision finalized as `resumed_by_human`.
5. **Timer expires** — host calls `Layer4Backend.tick()` periodically (e.g.
   every second); any expired timers trigger escalation:
   - machine marked degraded/unavailable
   - alternative search: compatible type (`IndustryConfig.machine_compatibility`),
     availability (`MachineState.status`), capacity
     (`IndustryConfig.machine_capacity`), queue
     (`DigitalTwinState.queue_length` vs `max_acceptable_queue_length`), load
     (`DigitalTwinState.current_load` vs `max_acceptable_load`).
6. **What-if simulation** — run via `WhatIfClient.run_whatif(...)` *before*
   any reallocation is applied.
7. **Feasible** → alternative selected, workload reallocated, decision =
   `reallocated`.
8. **Not feasible** → machine stays flagged, production impact reported,
   decision = `no_alternative_flagged`.

The scheduler (`recovery_engine.py`) is pure `if`/`for` logic against config
and verified inputs — there is no model, learned weighting, or randomness
anywhere in the decision path.

## AI Alert Explanation

`explanation.py` answers the nine required questions (what happened, anomaly,
sensor evidence, possible cause, production impact, human-correctable,
timeout behavior, alternative availability, what-if result) using **only**
fields present on the `FaultEvent` / `MachineHealthEvent` / `MachineState` /
`BottleneckInfo` / `WhatIfResult` objects it's given. Any field that wasn't
supplied by an upstream layer is reported as *"Not available from backend
data"* rather than inferred — see `test_explanation_never_invents_missing_data`
in `test_layer4.py`.

## Logging

Every step (`fault_detected`, `operator_notified`, `timer_expired`,
`whatif_run`, `recovery_finalized`, etc.) is written to `RecoveryLogger` as a
structured entry with a timestamp and payload. Pass `log_file=` to
`Layer4Backend` to also mirror entries to a JSON-lines file. Query via
`backend.get_logs()` or `backend.get_logs(machine_id=...)`.

## Industry configuration

`config.py` defines `ELECTRONICS_PCB_CONFIG` and `AUTOMOBILE_CONFIG`. Each
industry is fully described by an `IndustryConfig`:

- `machine_compatibility`: which machine *types* can substitute for which
- `machine_capacity`: per-machine throughput
- `production_flow`: ordered station list
- `human_correction_timeout_seconds`: per-industry grace period
- `max_acceptable_queue_length` / `max_acceptable_load`: alternative-machine
  acceptance thresholds

Add a new industry by adding a new `IndustryConfig` to `config.py` — no
changes needed anywhere else.

## Integrating the real Layers 1/2A/2B/3

Implement the four `Protocol`s in `interfaces.py`
(`MachineStateProvider`, `HealthEventProvider`, `DigitalTwinProvider`,
`WhatIfClient`) against the real layers, plus `OperatorNotifier` against
your actual alerting channel, then construct `Layer4Backend` with those
instead of the `mock_sources.py` fakes. Nothing else changes.

## Output for the future dashboard

`Layer4Backend` is the single integration point and returns plain dicts
(JSON-serializable) from every method:

- `ingest_fault(fault) -> dict` (RecoveryDecision)
- `report_human_correction(machine_id) -> dict | None`
- `tick() -> list[dict]` (decisions finalized this tick)
- `get_decision(decision_id) -> dict | None`
- `get_explanation(decision_id) -> dict | None`
- `get_logs(machine_id=None) -> list[dict]`
- `get_config_summary() -> dict`

This is intentionally framework-agnostic — drop it behind FastAPI/Flask
routes, a message queue consumer, or call it directly from the Developer
Workspace when that's built.

## Running

```bash
python demo.py          # runs 3 end-to-end scenarios and prints results
python test_layer4.py   # runs assertions on the core rules
```

No external dependencies — standard library only.
