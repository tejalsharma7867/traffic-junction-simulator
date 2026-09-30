import unittest

import settings
from core.simulation import Simulation


class TestStatistics(unittest.TestCase):
    """
    Tests for the statistics module.
    """

    def setUp(self):
        self.simulation = Simulation()

    def test_initial_stats_zero(self):
        stats = self.simulation.get_statistics()

        self.assertEqual(stats["simulation_duration"], 0.0)
        self.assertEqual(stats["tick"], 0)

        self.assertEqual(stats["total_generated"], 0)
        self.assertEqual(stats["total_passed"], 0)
        self.assertEqual(stats["active_vehicles"], 0)

        self.assertEqual(stats["vehicles_currently_waiting"], 0)
        self.assertEqual(stats["current_total_queue_length"], 0)

        self.assertEqual(stats["average_wait_time_finished"], 0.0)
        self.assertEqual(stats["max_wait_time_observed"], 0.0)

        self.assertEqual(stats["average_queue_length"], 0.0)
        self.assertEqual(stats["max_queue_length"], 0)

        expected_zero_directions = {
            "N": 0,
            "S": 0,
            "E": 0,
            "W": 0,
        }

        self.assertEqual(stats["current_queue_by_direction"], expected_zero_directions)
        self.assertEqual(stats["passed_by_direction"], expected_zero_directions)
        self.assertEqual(stats["vehicles_remaining_by_direction"], expected_zero_directions)

    def test_record_exited_vehicle(self):
        vehicle = self.simulation.add_vehicle("E")
        vehicle.wait_time = 4.5

        self.simulation.stats.record_exited_vehicle(vehicle)

        self.assertEqual(self.simulation.stats.total_exited_recorded, 1)
        self.assertAlmostEqual(
            self.simulation.stats.average_wait_time_finished(),
            4.5
        )

        self.assertEqual(self.simulation.stats.passed_by_direction["E"], 1)

        self.assertAlmostEqual(
            self.simulation.stats.max_wait_time_observed,
            4.5
        )

    def test_average_wait_finished_multiple_vehicles(self):
        vehicle_1 = self.simulation.add_vehicle("N")
        vehicle_1.wait_time = 2.0

        vehicle_2 = self.simulation.add_vehicle("S")
        vehicle_2.wait_time = 4.0

        self.simulation.stats.record_exited_vehicle(vehicle_1)
        self.simulation.stats.record_exited_vehicle(vehicle_2)

        self.assertEqual(self.simulation.stats.total_exited_recorded, 2)

        self.assertAlmostEqual(
            self.simulation.stats.average_wait_time_finished(),
            3.0
        )

        self.assertAlmostEqual(
            self.simulation.stats.max_wait_time_observed,
            4.0
        )

    def test_waiting_and_queue_counts(self):
        # Stopped vehicle at the stop line.
        vehicle_1 = self.simulation.add_vehicle("N")
        vehicle_1.position = settings.STOP_LINE_DISTANCE
        vehicle_1.speed = 0.0
        vehicle_1.state = "approaching"

        # Moving vehicle still approaching the junction.
        vehicle_2 = self.simulation.add_vehicle("N")
        vehicle_2.position = 100.0
        vehicle_2.speed = 10.0
        vehicle_2.state = "approaching"

        # Vehicle already crossing should not be counted in queue.
        vehicle_3 = self.simulation.add_vehicle("E")
        vehicle_3.position = settings.STOP_LINE_DISTANCE + 10.0
        vehicle_3.state = "crossing"

        self.simulation.stats.update(self.simulation)

        stats = self.simulation.get_statistics()

        self.assertEqual(stats["current_total_queue_length"], 2)
        self.assertEqual(stats["vehicles_currently_waiting"], 1)

        self.assertEqual(stats["current_queue_by_direction"]["N"], 2)
        self.assertEqual(stats["current_queue_by_direction"]["E"], 0)

    def test_average_and_max_queue_length(self):
        # Two approaching vehicles.
        self.simulation.add_vehicle("N")
        self.simulation.add_vehicle("E")

        self.simulation.stats.update(self.simulation)

        # Add one more approaching vehicle.
        self.simulation.add_vehicle("S")

        self.simulation.stats.update(self.simulation)

        stats = self.simulation.get_statistics()

        self.assertAlmostEqual(stats["average_queue_length"], 2.5)
        self.assertEqual(stats["max_queue_length"], 3)

    def test_max_waiting_observed_active(self):
        vehicle = self.simulation.add_vehicle("N")
        vehicle.wait_time = 7.0
        vehicle.speed = 0.0
        vehicle.state = "approaching"

        self.simulation.stats.update(self.simulation)

        stats = self.simulation.get_statistics()

        self.assertAlmostEqual(stats["max_wait_time_observed"], 7.0)
        self.assertAlmostEqual(stats["current_max_active_wait"], 7.0)

    def test_simulation_exit_records_stats(self):
        simulation = Simulation()

        simulation.signal_state.set_phase(settings.NS_GREEN)

        vehicle = simulation.add_vehicle("N")
        vehicle.position = settings.STOP_LINE_DISTANCE - 1.0

        # Run enough ticks for the vehicle to cross and exit.
        for _ in range(300):
            simulation.step(settings.TICK_DURATION)

        stats = simulation.get_statistics()

        self.assertEqual(stats["total_passed"], 1)
        self.assertEqual(stats["total_exited_recorded"], 1)
        self.assertEqual(stats["passed_by_direction"]["N"], 1)

    def test_stats_reset_clears_statistics(self):
        vehicle = self.simulation.add_vehicle("N")
        vehicle.wait_time = 5.0

        self.simulation.stats.record_exited_vehicle(vehicle)
        self.simulation.stats.update(self.simulation)

        self.simulation.reset()

        stats = self.simulation.get_statistics()

        self.assertEqual(stats["total_generated"], 0)
        self.assertEqual(stats["total_passed"], 0)
        self.assertEqual(stats["active_vehicles"], 0)

        self.assertEqual(stats["average_wait_time_finished"], 0.0)
        self.assertEqual(stats["max_wait_time_observed"], 0.0)

        self.assertEqual(stats["average_queue_length"], 0.0)
        self.assertEqual(stats["max_queue_length"], 0)

        expected_zero_directions = {
            "N": 0,
            "S": 0,
            "E": 0,
            "W": 0,
        }

        self.assertEqual(stats["passed_by_direction"], expected_zero_directions)
        self.assertEqual(stats["current_queue_by_direction"], expected_zero_directions)


if __name__ == "__main__":
    unittest.main()