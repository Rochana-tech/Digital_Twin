"""
main.py

Standalone entry point for Layer 1 (Data Acquisition & Communication).

Run with:
    python main.py
    INDUSTRY=automobile python main.py
    python main.py --industry automobile
    python main.py --demo          # also prints incoming data to prove the
                                    # streams are alive (for manual testing
                                    # only -- not part of the real interface)

Layer 1 starts two independent background engines:
  A. DummySensorPublisher     -> publishes to MQTT, topic per machine
  B. DummyMachineDataSimulator -> in-process callbacks + local HTTP polling

It does NOT do any fault detection, health scoring, digital twin,
bottleneck/what-if analysis, recovery, or dashboarding -- that is
explicitly out of scope for this layer.
"""

import argparse
import signal
import sys
import time

from config.industry_config import get_active_industry, get_machines, list_industries, set_active_industry
from common.logger import get_logger
from machine_data.machine_simulator import DummyMachineDataSimulator
from sensors.sensor_publisher import DummySensorPublisher

logger = get_logger("main")


def _parse_args():
    parser = argparse.ArgumentParser(description="Run Layer 1: Data Acquisition & Communication")
    parser.add_argument(
        "--industry",
        choices=list_industries(),
        default=None,
        help="Industry configuration to run (overrides INDUSTRY env var / saved selection).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Print a sample of incoming sensor + machine data to stdout for manual verification.",
    )
    return parser.parse_args()


def _demo_sensor_callback(reading: dict) -> None:
    print(f"[SENSOR ] {reading}")


def _demo_machine_callback(record: dict) -> None:
    print(f"[MACHINE] {record}")


def main() -> None:
    args = _parse_args()

    if args.industry:
        set_active_industry(args.industry)

    industry = get_active_industry()
    machines = get_machines(industry)

    logger.info("=== Layer 1: Data Acquisition & Communication ===")
    logger.info("Active industry: %s", industry)
    logger.info("Production line: %s", [f"{m['machine_id']}:{m['name']}" for m in machines])

    sensor_publisher = DummySensorPublisher(machines=machines, industry=industry)
    machine_simulator = DummyMachineDataSimulator(machines=machines, industry=industry)

    if args.demo:
        sensor_publisher.subscribe(_demo_sensor_callback)
        machine_simulator.subscribe(_demo_machine_callback)

    sensor_publisher.start()
    machine_simulator.start()

    stop_requested = {"flag": False}

    def _handle_shutdown(signum, frame):  # noqa: ANN001
        logger.info("Shutdown signal received, stopping Layer 1...")
        stop_requested["flag"] = True

    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    try:
        while not stop_requested["flag"]:
            time.sleep(0.5)
    finally:
        sensor_publisher.stop()
        machine_simulator.stop()
        logger.info("Layer 1 stopped cleanly.")


if __name__ == "__main__":
    sys.exit(main() or 0)
