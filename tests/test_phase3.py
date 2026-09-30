import unittest

import settings
from core.simulation import Simulation
from core import movement
from control.signal_state import SignalState


class TestSignalState(unittest.TestCase):
    """
    Tests for the basic signal state.
    """

    def setUp(self):
        self.signal = SignalState()

    def test_ns_green_allows_ns_only(self):
        self.signal.set_phase(settings.NS_GREEN)

        self.assertTrue(self.signal.can_enter_junction("N"))
        self.assertTrue(self.signal.can_enter_junction("S"))

        self.assertFalse(self.signal.can_enter_junction("E"))
        self.assertFalse(self.signal.can_enter_junction("W"))

    def test_ew_green_allows_ew_only(self):
        self.signal.set_phase(settings.EW_GREEN)

        self.assertTrue(self.signal.can_enter_junction("E"))
        self.assertTrue(self.signal.can_enter_junction("W"))

        self.assertFalse(self.signal.can_enter_junction("N"))
        self.assertFalse(self.signal.can_enter_junction("S"))

    def test_yellow_and_all_red_allow_no_entry(self):
        self.signal.set_phase(settings.NS_YELLOW)

        self.assertFalse(self.signal.can_enter_junction("N"))
        self.assertFalse(self.signal.can_enter_junction("S"))
        self.assertFalse(self.signal.can_enter_junction("E"))
        self.assertFalse(self.signal.can_enter_junction("W"))

        self.signal.set_phase(settings.ALL_RED)

        self.assertFalse(self.signal.can_enter_junction("N"))
        self.assertFalse(self.signal.can_enter_junction("S"))
        self.assertFalse(self.signal.can_enter_junction("E"))
        self.assertFalse(self.signal.can_enter_junction("W"))

    def test_invalid_phase_raises_error(self):
        with self.assertRaises(ValueError):
            self.signal.set_phase("BLUE")


class TestMovement(unittest.TestCase):
    """
    Tests for vehicle movement and queue behavior.
    """

    def setUp(self):
        self.simulation = Simulation()

    def test_vehicle_moves_on_green(self):
        self.simulation.signal_state.set_phase(settings.NS_GREEN)

        vehicle = self.simulation.add_vehicle("N")
        vehicle.position = 0.0

        movement.update(self.simulation, 0.1)

        self.assertGreater(vehicle.position, 0.0)

    def test_vehicle_stops_on_red(self):
        self.simulation.signal_state.set_phase(settings.ALL_RED)

        vehicle = self.simulation.add_vehicle("N")
        vehicle.position = settings.STOP_LINE_DISTANCE - 1.0

        movement.update(self.simulation, 0.1)

        self.assertLessEqual(
            vehicle.position,
            settings.STOP_LINE_DISTANCE + settings.MOVEMENT_EPSILON
        )

        self.assertAlmostEqual(
            vehicle.position,
            settings.STOP_LINE_DISTANCE,
            places=5
        )

        self.assertEqual(vehicle.speed, 0.0)
        self.assertEqual(vehicle.state, "approaching")

    def test_vehicles_form_queue_without_overlap(self):
        self.simulation.signal_state.set_phase(settings.ALL_RED)

        starting_positions = [0.0, 40.0, 80.0]

        for position in starting_positions:
            vehicle = self.simulation.add_vehicle("N")
            vehicle.position = position

        # Run enough ticks for the queue to form.
        for _ in range(500):
            movement.update(self.simulation, settings.TICK_DURATION)

        lane = sorted(
            self.simulation.vehicles,
            key=lambda vehicle: vehicle.position,
            reverse=True
        )

        self.assertEqual(len(lane), 3)

        # The leader should be at the stop line.
        self.assertAlmostEqual(
            lane[0].position,
            settings.STOP_LINE_DISTANCE,
            places=2
        )

        # Each following vehicle should be safely behind the leader.
        for i in range(1, len(lane)):
            leader = lane[i - 1]
            follower = lane[i]

            maximum_safe_position = (
                leader.position - leader.length - settings.VEHICLE_GAP
            )

            self.assertLessEqual(
                follower.position,
                maximum_safe_position + settings.MOVEMENT_EPSILON
            )

    def test_vehicle_crosses_and_exits_on_green(self):
        self.simulation.signal_state.set_phase(settings.NS_GREEN)

        vehicle = self.simulation.add_vehicle("N")
        vehicle.position = settings.STOP_LINE_DISTANCE - 1.0

        for _ in range(200):
            movement.update(self.simulation, settings.TICK_DURATION)

        self.assertEqual(self.simulation.total_exited, 1)
        self.assertEqual(len(self.simulation.vehicles), 0)

    def test_waiting_time_increases_when_stopped_at_red(self):
        self.simulation.signal_state.set_phase(settings.ALL_RED)

        vehicle = self.simulation.add_vehicle("N")
        vehicle.position = settings.STOP_LINE_DISTANCE - 0.1

        movement.update(self.simulation, 0.1)

        self.assertGreater(vehicle.wait_time, 0.0)


if __name__ == "__main__":
    unittest.main()