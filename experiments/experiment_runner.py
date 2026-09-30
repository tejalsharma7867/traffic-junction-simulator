import argparse
import csv
import os
import settings
from core.simulation import Simulation
from core.traffic_generator import TrafficGenerator
from control.fixed_controller import FixedController
from control.adaptive_controller import AdaptiveController


MODES = ("fixed", "adaptive")

DEFAULT_INTENSITY_LEVELS = ("LOW", "MEDIUM", "HIGH")

RESULT_FIELDS = [
    "mode",
    "intensity",
    "seed",
    "duration_seconds",
    "simulated_seconds",

    "total_generated",
    "total_passed",
    "vehicles_remaining",
    "vehicles_currently_waiting",

    "average_wait_time_finished",
    "max_wait_time_observed",

    "average_queue_length",
    "max_queue_length",

    "passed_N",
    "passed_S",
    "passed_E",
    "passed_W",

    "remaining_N",
    "remaining_S",
    "remaining_E",
    "remaining_W",
]


def create_controller(mode):
    """
    Create a controller for the given mode.

    Args:
        mode: "fixed" or "adaptive".

    Returns:
        FixedController or AdaptiveController.
    """
    mode = mode.lower()

    if mode == "fixed":
        return FixedController()

    if mode == "adaptive":
        return AdaptiveController()

    raise ValueError(f"Invalid controller mode: {mode}")


def run_single_experiment(
    mode="fixed",
    intensity_name="MEDIUM",
    duration_seconds=60.0,
    seed=42,
    direction_weights=None
):
    """
    Run one complete headless simulation experiment.

    Args:
        mode: "fixed" or "adaptive".
        intensity_name: "LOW", "MEDIUM", or "HIGH".
        duration_seconds: Simulation duration in seconds.
        seed: Random seed for traffic generation.
        direction_weights: Optional dictionary of directional weights.

    Returns:
        A flat dictionary of experiment results.
    """
    mode = mode.lower()
    intensity_name = intensity_name.upper()

    if mode not in MODES:
        raise ValueError(f"Invalid experiment mode: {mode}")

    if intensity_name not in settings.TRAFFIC_INTENSITY:
        raise ValueError(f"Invalid traffic intensity: {intensity_name}")

    if duration_seconds < 0:
        raise ValueError("Experiment duration cannot be negative.")

    generator = TrafficGenerator(
        intensity_name=intensity_name,
        direction_weights=direction_weights,
        seed=seed
    )

    controller = create_controller(mode)

    simulation = Simulation(
        traffic_generator=generator,
        controller=controller
    )

    tick_count = int(round(duration_seconds / settings.TICK_DURATION))

    for _ in range(tick_count):
        simulation.step(settings.TICK_DURATION)

    stats = simulation.get_statistics()

    result = {
        "mode": mode,
        "intensity": intensity_name,
        "seed": seed,
        "duration_seconds": duration_seconds,
        "simulated_seconds": stats["simulation_duration"],

        "total_generated": stats["total_generated"],
        "total_passed": stats["total_passed"],
        "vehicles_remaining": stats["active_vehicles"],
        "vehicles_currently_waiting": stats["vehicles_currently_waiting"],

        "average_wait_time_finished": stats["average_wait_time_finished"],
        "max_wait_time_observed": stats["max_wait_time_observed"],

        "average_queue_length": stats["average_queue_length"],
        "max_queue_length": stats["max_queue_length"],
    }

    for direction in settings.DIRECTIONS:
        result[f"passed_{direction}"] = stats["passed_by_direction"][direction]
        result[f"remaining_{direction}"] = stats["vehicles_remaining_by_direction"][direction]

    return result


def run_experiment_matrix(
    intensity_levels=None,
    modes=None,
    duration_seconds=60.0,
    seeds=None
):
    """
    Run a set of experiments over multiple intensities, modes, and seeds.

    Args:
        intensity_levels: List of traffic intensity names.
        modes: List of controller modes.
        duration_seconds: Duration for each experiment.
        seeds: List of random seeds.

    Returns:
        A list of result dictionaries.
    """
    if intensity_levels is None:
        intensity_levels = DEFAULT_INTENSITY_LEVELS

    if modes is None:
        modes = MODES

    if seeds is None:
        seeds = (42,)

    intensity_levels = [level.upper() for level in intensity_levels]
    modes = [mode.lower() for mode in modes]

    results = []

    for seed in seeds:
        for intensity in intensity_levels:
            for mode in modes:
                result = run_single_experiment(
                    mode=mode,
                    intensity_name=intensity,
                    duration_seconds=duration_seconds,
                    seed=seed
                )

                results.append(result)

    return results


def format_results_table(results):
    """
    Format experiment results as a readable text table.

    Args:
        results: List of result dictionaries.

    Returns:
        String containing the formatted table.
    """
    if not results:
        return "No results."

    lines = []

    header = (
        f"{'Mode':<9} "
        f"{'Intensity':<9} "
        f"{'Seed':>5} "
        f"{'Dur':>6} "
        f"{'Gen':>5} "
        f"{'Pass':>5} "
        f"{'Rem':>5} "
        f"{'AvgWait':>8} "
        f"{'MaxWait':>8} "
        f"{'AvgQ':>6} "
        f"{'MaxQ':>6}"
    )

    lines.append(header)
    lines.append("-" * len(header))

    for row in results:
        line = (
            f"{row['mode']:<9} "
            f"{row['intensity']:<9} "
            f"{row['seed']:>5} "
            f"{row['duration_seconds']:>6.1f} "
            f"{row['total_generated']:>5} "
            f"{row['total_passed']:>5} "
            f"{row['vehicles_remaining']:>5} "
            f"{row['average_wait_time_finished']:>8.2f} "
            f"{row['max_wait_time_observed']:>8.2f} "
            f"{row['average_queue_length']:>6.2f} "
            f"{row['max_queue_length']:>6}"
        )

        lines.append(line)

    return "\n".join(lines)


def save_results_csv(results, filename):
    """
    Save experiment results to a CSV file.

    Args:
        results: List of result dictionaries.
        filename: Output CSV file path.
    """
    if not results:
        return

    directory = os.path.dirname(filename)

    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_FIELDS)

        writer.writeheader()

        for row in results:
            clean_row = {
                field: row.get(field, "")
                for field in RESULT_FIELDS
            }

            writer.writerow(clean_row)


def main():
    """
    Command-line entry point for running experiments.
    """
    parser = argparse.ArgumentParser(
        description="Run Adaptive Traffic Junction Simulator experiments."
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=60.0,
        help="Duration of each experiment in simulated seconds."
    )

    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[42],
        help="Random seeds to use."
    )

    parser.add_argument(
        "--intensities",
        nargs="+",
        default=list(DEFAULT_INTENSITY_LEVELS),
        help="Traffic intensity levels."
    )

    parser.add_argument(
        "--modes",
        nargs="+",
        default=list(MODES),
        help="Controller modes."
    )

    parser.add_argument(
        "--output",
        default="results/experiment_results.csv",
        help="Output CSV file."
    )

    args = parser.parse_args()

    results = run_experiment_matrix(
        intensity_levels=args.intensities,
        modes=args.modes,
        duration_seconds=args.duration,
        seeds=args.seeds
    )

    print()
    print("Running experiments...")
    print()
    print(format_results_table(results))
    print()

    save_results_csv(results, args.output)

    print(f"Saved results to: {args.output}")


if __name__ == "__main__":
    main()