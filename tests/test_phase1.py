import unittest

import settings
from core.vehicle import Vehicle
from core.simulation import Simulation


class TestVehicle(unittest.TestCase):
    """
    Tests for basic vehicle creation.
    """

    def test_vehicle_creation(self):
        vehicle = Vehicle(
            id=1,
            direction="N",
            arrival_time=0.0
        )

        self.assertEqual(vehicle.id, 1)
        self.assertEqual(vehicle.direction, "N")
        self.assertEqual(vehicle.arrival_time, 0.0)
        self.assertEqual(vehicle.position, 0.0)
        self.assertEqual(vehicle.speed, 0.0)
        self.assertEqual(vehicle.state, "approaching")

    def test_invalid_direction_raises_error(self):
        with self.assertRaises(ValueError):
            Vehicle(
                id=1,
                direction="X",
                arrival_time=0.0
            )


class TestSimulation(unittest.TestCase):
    """
    Tests for the basic simulation state.
    """

    def setUp(self):
        self.simulation = Simulation()

    def test_initial_state(self):
        self.assertEqual(self.simulation.tick, 0)
        self.assertEqual(self.simulation.time, 0.0)
        self.assertEqual(self.simulation.active_vehicle_count(), 0)
        self.assertEqual(self.simulation.total_generated, 0)
        self.assertFalse(self.simulation.paused)

    def test_time_advances(self):
        old_time = self.simulation.time
        old_tick = self.simulation.tick

        self.simulation.step()

        self.assertEqual(self.simulation.tick, old_tick + 1)
        self.assertAlmostEqual(
            self.simulation.time,
            old_time + settings.TICK_DURATION
        )

    def test_pause_prevents_time_advance(self):
        old_time = self.simulation.time
        old_tick = self.simulation.tick

        self.simulation.pause()
        self.simulation.step()

        self.assertEqual(self.simulation.tick, old_tick)
        self.assertEqual(self.simulation.time, old_time)

    def test_resume_allows_time_advance(self):
        self.simulation.pause()
        self.simulation.resume()

        old_time = self.simulation.time

        self.simulation.step()

        self.assertAlmostEqual(
            self.simulation.time,
            old_time + settings.TICK_DURATION
        )

    def test_add_vehicle(self):
        vehicle_1 = self.simulation.add_vehicle("N")
        vehicle_2 = self.simulation.add_vehicle("E")

        self.assertEqual(self.simulation.active_vehicle_count(), 2)
        self.assertEqual(self.simulation.total_generated, 2)

        self.assertEqual(vehicle_1.id, 1)
        self.assertEqual(vehicle_2.id, 2)

        self.assertEqual(vehicle_1.direction, "N")
        self.assertEqual(vehicle_2.direction, "E")

    def test_reset_clears_state(self):
        self.simulation.add_vehicle("N")
        self.simulation.add_vehicle("S")

        for _ in range(5):
            self.simulation.step()

        self.simulation.reset()

        self.assertEqual(self.simulation.tick, 0)
        self.assertEqual(self.simulation.time, 0.0)
        self.assertEqual(self.simulation.active_vehicle_count(), 0)
        self.assertEqual(self.simulation.total_generated, 0)
        self.assertFalse(self.simulation.paused)


if __name__ == "__main__":
    unittest.main()