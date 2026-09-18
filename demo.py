"""
End-to-end demo of Layer 4, using mock Layer 1/2A/2B/3 data.

Run: python demo.py

Simulates three scenarios:
  A) Electronics/PCB — human corrects in time -> machine resumes.
  B) Electronics/PCB — timer expires -> feasible alternative -> reallocation.
  C) Automobile       — timer expires -> no feasible alternative -> flagged.

Uses an injectable fake clock so we don't actually wait for timers.
"""

import json
from datetime import datetime, timedelta

from layer4 import ELECTRONICS_PCB_CONFIG, AUTOMOBILE_CONFIG, Layer4Backend
from layer4.models import (
    FaultEvent,
    MachineHealthEvent,
    MachineState,
    MachineStatus,
    DigitalTwinState,
    BottleneckInfo,
)
from layer4.mock_sources import (
    InMemoryMachineStateProvider,
    InMemoryHealthEventProvider,
    InMemoryDigitalTwinProvider,
    SimpleWhatIfClient,
    ConsoleOperatorNotifier,
)
from layer4.timer_manager import CorrectionTimerManager


class FakeClock:
    """Lets us jump time forward without sleeping."""
    def __init__(self):
        self.now = datetime.utcnow()

    def __call__(self):
        return self.now

    def advance(self, seconds: int):
        self.now += timedelta(seconds=seconds)


def build_backend(config, machine_states, health_events, twin_states, bottleneck, clock):
    ms_provider = InMemoryMachineStateProvider(machine_states)
    he_provider = InMemoryHealthEventProvider(health_events)
    dt_provider = InMemoryDigitalTwinProvider(twin_states, bottleneck)
    whatif = SimpleWhatIfClient(
        dt_provider, config.max_acceptable_queue_length, config.max_acceptable_load
    )
    notifier = ConsoleOperatorNotifier()
    timers = CorrectionTimerManager(clock=clock)

    return Layer4Backend(
        config=config,
        machine_states=ms_provider,
        health_events=he_provider,
        digital_twin=dt_provider,
        whatif_client=whatif,
        operator=notifier,
        timer_manager=timers,
    ), ms_provider


def pretty(title, obj):
    print(f"\n--- {title} ---")
    print(json.dumps(obj, indent=2, default=str))


def scenario_a_human_corrects():
    print("\n========== SCENARIO A: Electronics/PCB — human corrects in time ==========")
    clock = FakeClock()
    machine_states = {
        "SMT-01": MachineState("SMT-01", "smt_placement", MachineStatus.RUNNING),
        "SMT-02": MachineState("SMT-02", "smt_placement_backup", MachineStatus.RUNNING),
    }
    health_events = {
        "SMT-01": MachineHealthEvent("SMT-01", 0.42, ["nozzle_wear"], 40.0)
    }
    twin_states = {
        "SMT-01": DigitalTwinState("SMT-01", "degraded", 2, 0.7),
        "SMT-02": DigitalTwinState("SMT-02", "nominal", 1, 0.5),
    }
    backend, _ = build_backend(
        ELECTRONICS_PCB_CONFIG, machine_states, health_events, twin_states, None, clock
    )

    fault = FaultEvent(
        fault_id="F-1001", machine_id="SMT-01", fault_type="nozzle_misalignment",
        confidence=0.91, sensor_evidence={"vibration_z": 3.4, "likely_cause": "worn nozzle tip"},
    )
    decision = backend.ingest_fault(fault)
    pretty("Decision after fault detected", decision)

    clock.advance(30)  # well within the 90s Electronics timeout
    resumed = backend.report_human_correction("SMT-01")
    pretty("Decision after human correction", resumed)
    pretty("Explanation", backend.get_explanation(decision["decision_id"]))


def scenario_b_reallocation():
    print("\n========== SCENARIO B: Electronics/PCB — timer expires, reallocation ==========")
    clock = FakeClock()
    machine_states = {
        "REFLOW-01": MachineState("REFLOW-01", "reflow_oven", MachineStatus.RUNNING),
        "REFLOW-02": MachineState("REFLOW-02", "reflow_oven_secondary", MachineStatus.IDLE),
    }
    health_events = {
        "REFLOW-01": MachineHealthEvent("REFLOW-01", 0.21, ["heater_element_degradation"], 6.0)
    }
    twin_states = {
        "REFLOW-01": DigitalTwinState("REFLOW-01", "faulted", 5, 0.95),
        "REFLOW-02": DigitalTwinState("REFLOW-02", "nominal", 1, 0.4),
    }
    bottleneck = BottleneckInfo("REFLOW-01", "high", "PCB line throughput drops ~30%")
    backend, _ = build_backend(
        ELECTRONICS_PCB_CONFIG, machine_states, health_events, twin_states, bottleneck, clock
    )

    fault = FaultEvent(
        fault_id="F-1002", machine_id="REFLOW-01", fault_type="overheat",
        confidence=0.97, sensor_evidence={"chamber_temp_c": 268},
    )
    decision = backend.ingest_fault(fault)
    pretty("Decision after fault detected", decision)

    clock.advance(91)  # past the 90s Electronics timeout, no correction reported
    finalized = backend.tick()
    pretty("Decisions after timer expiry", finalized)
    pretty("Explanation", backend.get_explanation(decision["decision_id"]))
    pretty("Logs for REFLOW-01", backend.get_logs("REFLOW-01"))


def scenario_c_no_alternative():
    print("\n========== SCENARIO C: Automobile — timer expires, no feasible alternative ==========")
    clock = FakeClock()
    machine_states = {
        "PAINT-01": MachineState("PAINT-01", "paint_booth", MachineStatus.RUNNING),
        "PAINT-02": MachineState("PAINT-02", "paint_booth_backup", MachineStatus.RUNNING),
    }
    health_events = {}
    twin_states = {
        "PAINT-01": DigitalTwinState("PAINT-01", "faulted", 8, 0.99),
        # PAINT-02 already overloaded -> fails queue/load checks
        "PAINT-02": DigitalTwinState("PAINT-02", "nominal", 9, 0.97),
    }
    backend, _ = build_backend(
        AUTOMOBILE_CONFIG, machine_states, health_events, twin_states, None, clock
    )

    fault = FaultEvent(
        fault_id="F-2001", machine_id="PAINT-01", fault_type="spray_nozzle_clog",
        confidence=0.88,
    )
    decision = backend.ingest_fault(fault)
    pretty("Decision after fault detected", decision)

    clock.advance(181)  # past the 180s Automobile timeout
    finalized = backend.tick()
    pretty("Decisions after timer expiry", finalized)
    pretty("Explanation", backend.get_explanation(decision["decision_id"]))


if __name__ == "__main__":
    scenario_a_human_corrects()
    scenario_b_reallocation()
    scenario_c_no_alternative()
