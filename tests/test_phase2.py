import unittest

import settings
from core.simulation import Simulation
from core.traffic_generator import TrafficGenerator


class TestTrafficGenerator(unittest.TestCase):
    """
    Tests for the traffic generation module.
    """

    def setUp(self):
        self.simulation = Simulation()

    def test_invalid_intensity_raises_error(self):
        with self.assertRaises(ValueError):
            TrafficGenerator(intensity_name="EXTREME")

    def test_invalid_direction_weight_raises_error(self):
        with self.assertRaises(ValueError):
            TrafficGenerator(
                direction_weights={
                    "X": 1.0
                }
            )

        with self.assertRaises(ValueError):
            TrafficGenerator(
                direction_weights={
                    "N": -1.0
                }
            )

    def test_zero_rate_generates_no_vehicles(self):
        generator = TrafficGenerator(seed=1)
        generator.base_rate = 0.0

        for _ in range(100):
            generator.generate(self.simulation, dt=0.1)

        self.assertEqual(self.simulation.total_generated, 0)
        self.assertEqual(self.simulation.active_vehicle_count(), 0)

    def test_exact_expected_spawn(self):
        generator = TrafficGenerator(seed=1)

        # Force exactly one expected vehicle from North for dt=1.0.
        generator.base_rate = 1.0
        generator.set_direction_weights({
            "N": 1.0,
            "S": 0.0,
            "E": 0.0,
            "W": 0.0,
        })

        spawned = generator.generate(self.simulation, dt=1.0)

        self.assertEqual(len(spawned), 1)
        self.assertEqual(spawned[0].direction, "N")
        self.assertEqual(self.simulation.total_generated, 1)

    def test_high_intensity_generates_more_than_low(self):
        low_simulation = Simulation(
            TrafficGenerator(
                intensity_name="LOW",
                seed=42
            )
        )

        high_simulation = Simulation(
            TrafficGenerator(
                intensity_name="HIGH",
                seed=42
            )
        )

        for _ in range(1000):
            low_simulation.step()
            high_simulation.step()

        self.assertGreater(
            high_simulation.total_generated,
            low_simulation.total_generated
        )

    def test_same_seed_reproduces_same_sequence(self):
        def run_simulation(seed):
            simulation = Simulation(
                TrafficGenerator(
                    intensity_name="MEDIUM",
                    seed=seed
                )
            )

            for _ in range(200):
                simulation.step()

            return [vehicle.direction for vehicle in simulation.vehicles]

        first_run = run_simulation(7)
        second_run = run_simulation(7)

        self.assertEqual(first_run, second_run)

    def test_simulation_step_uses_generator(self):
        generator = TrafficGenerator(seed=1)

        generator.base_rate = 1.0
        generator.set_direction_weights({
            "N": 1.0,
            "S": 0.0,
            "E": 0.0,
            "W": 0.0,
        })

        simulation = Simulation(generator)

        simulation.step(dt=1.0)

        self.assertEqual(simulation.total_generated, 1)
        self.assertEqual(simulation.active_vehicle_count(), 1)
        self.assertEqual(simulation.vehicles[0].direction, "N")


if __name__ == "__main__":
    unittest.main()