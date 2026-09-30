import csv
import os
import tempfile
import unittest
import settings
from experiments import experiment_runner


class TestExperimentRunner(unittest.TestCase):
    """
    Tests for the experiment runner.
    """

    def test_run_single_experiment_returns_flat_result(self):
        result = experiment_runner.run_single_experiment(
            mode="fixed",
            intensity_name="LOW",
            duration_seconds=1.0,
            seed=42
        )

        for field in experiment_runner.RESULT_FIELDS:
            self.assertIn(field, result)

        self.assertEqual(result["mode"], "fixed")
        self.assertEqual(result["intensity"], "LOW")
        self.assertEqual(result["seed"], 42)

    def test_no_traffic_scenario(self):
        zero_weights = {
            direction: 0.0
            for direction in settings.DIRECTIONS
        }

        result = experiment_runner.run_single_experiment(
            mode="adaptive",
            intensity_name="HIGH",
            duration_seconds=2.0,
            seed=1,
            direction_weights=zero_weights
        )

        self.assertEqual(result["total_generated"], 0)
        self.assertEqual(result["total_passed"], 0)
        self.assertEqual(result["vehicles_remaining"], 0)
        self.assertEqual(result["vehicles_currently_waiting"], 0)
        self.assertEqual(result["max_queue_length"], 0)

    def test_same_seed_produces_same_generated_count(self):
        fixed_result = experiment_runner.run_single_experiment(
            mode="fixed",
            intensity_name="LOW",
            duration_seconds=3.0,
            seed=7
        )

        adaptive_result = experiment_runner.run_single_experiment(
            mode="adaptive",
            intensity_name="LOW",
            duration_seconds=3.0,
            seed=7
        )

        self.assertEqual(
            fixed_result["total_generated"],
            adaptive_result["total_generated"]
        )

    def test_invalid_mode_raises_error(self):
        with self.assertRaises(ValueError):
            experiment_runner.run_single_experiment(
                mode="magic",
                intensity_name="LOW",
                duration_seconds=1.0,
                seed=1
            )

    def test_experiment_matrix_row_count(self):
        results = experiment_runner.run_experiment_matrix(
            intensity_levels=["LOW", "MEDIUM"],
            modes=["fixed", "adaptive"],
            duration_seconds=0.5,
            seeds=[1, 2]
        )

        # 2 intensities × 2 modes × 2 seeds = 8 results.
        self.assertEqual(len(results), 8)

    def test_save_results_csv(self):
        result = experiment_runner.run_single_experiment(
            mode="fixed",
            intensity_name="LOW",
            duration_seconds=0.5,
            seed=42
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = os.path.join(
                temporary_directory,
                "results",
                "test_results.csv"
            )

            experiment_runner.save_results_csv([result], output_path)

            self.assertTrue(os.path.exists(output_path))

            with open(output_path, newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["mode"], "fixed")
            self.assertEqual(rows[0]["intensity"], "LOW")


if __name__ == "__main__":
    unittest.main()