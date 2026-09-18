"""
Lightweight tests (no pytest dependency needed — run with `python test_layer4.py`)
covering the core rules: human-correction path, reallocation path, and
no-alternative path, plus the "explanation never invents data" guarantee.
"""

from datetime import datetime, timedelta

from layer4 import ELECTRONICS_PCB_CONFIG, Layer4Backend
from layer4.models import (
    FaultEvent, MachineState, MachineStatus, MachineHealthEvent, DigitalTwinState,
)
from layer4.mock_sources import (
    InMemoryMachineStateProvider, InMemoryHealthEventProvider,
    InMemoryDigitalTwinProvider, SimpleWhatIfClient, ConsoleOperatorNotifier,
)
from layer4.timer_manager import CorrectionTimerManager


class FakeClock:
    def __init__(self):
        self.now = datetime(2026, 1, 1)

    def __call__(self):
        return self.now

    def advance(self, s):
        self.now += timedelta(seconds=s)


def make_backend(machine_states, twin_states, health_events=None, config=ELECTRONICS_PCB_CONFIG):
    clock = FakeClock()
    ms = InMemoryMachineStateProvider(machine_states)
    he = InMemoryHealthEventProvider(health_events or {})
    dt = InMemoryDigitalTwinProvider(twin_states)
    wi = SimpleWhatIfClient(dt, config.max_acceptable_queue_length, config.max_acceptable_load)
    backend = Layer4Backend(config, ms, he, dt, wi, ConsoleOperatorNotifier(),
                             timer_manager=CorrectionTimerManager(clock=clock))
    return backend, clock


def test_human_correction_keeps_machine_active():
    backend, clock = make_backend(
        {"SMT-01": MachineState("SMT-01", "smt_placement", MachineStatus.RUNNING)},
        {"SMT-01": DigitalTwinState("SMT-01", "ok", 1, 0.5)},
    )
    d = backend.ingest_fault(FaultEvent("F1", "SMT-01", "jam", 0.9))
    assert d["status"] == "awaiting_correction"
    clock.advance(10)
    d2 = backend.report_human_correction("SMT-01")
    assert d2["status"] == "resumed_by_human"
    assert d2["human_corrected"] is True
    print("PASS: test_human_correction_keeps_machine_active")


def test_timer_expiry_triggers_reallocation():
    backend, clock = make_backend(
        {
            "SMT-01": MachineState("SMT-01", "smt_placement", MachineStatus.RUNNING),
            "SMT-02": MachineState("SMT-02", "smt_placement_backup", MachineStatus.IDLE),
        },
        {
            "SMT-01": DigitalTwinState("SMT-01", "faulted", 5, 0.95),
            "SMT-02": DigitalTwinState("SMT-02", "ok", 1, 0.3),
        },
    )
    d = backend.ingest_fault(FaultEvent("F2", "SMT-01", "overheat", 0.9))
    clock.advance(ELECTRONICS_PCB_CONFIG.human_correction_timeout_seconds + 1)
    finalized = backend.tick()
    assert len(finalized) == 1
    assert finalized[0]["status"] == "reallocated"
    assert finalized[0]["alternative_machine_id"] == "SMT-02"
    print("PASS: test_timer_expiry_triggers_reallocation")


def test_no_alternative_flags_machine():
    backend, clock = make_backend(
        {
            "SMT-01": MachineState("SMT-01", "smt_placement", MachineStatus.RUNNING),
            "SMT-02": MachineState("SMT-02", "smt_placement_backup", MachineStatus.RUNNING),
        },
        {
            "SMT-01": DigitalTwinState("SMT-01", "faulted", 5, 0.95),
            "SMT-02": DigitalTwinState("SMT-02", "ok", 9, 0.99),  # overloaded -> fails checks
        },
    )
    d = backend.ingest_fault(FaultEvent("F3", "SMT-01", "overheat", 0.9))
    clock.advance(ELECTRONICS_PCB_CONFIG.human_correction_timeout_seconds + 1)
    finalized = backend.tick()
    assert finalized[0]["status"] == "no_alternative_flagged"
    assert finalized[0]["alternative_machine_id"] is None
    print("PASS: test_no_alternative_flags_machine")


def test_explanation_never_invents_missing_data():
    backend, clock = make_backend(
        {"SMT-01": MachineState("SMT-01", "smt_placement", MachineStatus.RUNNING)},
        {"SMT-01": DigitalTwinState("SMT-01", "ok", 1, 0.5)},
        health_events={},  # deliberately no health event
    )
    d = backend.ingest_fault(FaultEvent("F4", "SMT-01", "jam", 0.9))  # no sensor_evidence
    exp = backend.get_explanation(d["decision_id"])
    assert "No machine-health event was supplied" in exp["sensor_evidence"]
    assert "Not available from backend data" in exp["possible_cause"]
    print("PASS: test_explanation_never_invents_missing_data")


if __name__ == "__main__":
    test_human_correction_keeps_machine_active()
    test_timer_expiry_triggers_reallocation()
    test_no_alternative_flags_machine()
    test_explanation_never_invents_missing_data()
    print("\nAll tests passed.")
