import unittest

import settings
from core.simulation import Simulation
from control.fixed_controller import FixedController


class TestFixedController(unittest.TestCase):
    """
    Tests for the fixed-time signal controller.
    """

    def setUp(self):
        self.controller = FixedController(
            green_time=1.0,
            yellow_time=0.5,
            all_red_time=0.5
        )

        self.simulation = Simulation(controller=self.controller)

    def test_initial_phase_is_ns_green(self):
        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.NS_GREEN
        )

        self.assertAlmostEqual(
            self.simulation.signal_state.time_remaining,
            1.0
        )

    def test_transition_sequence(self):
        # NS_GREEN -> NS_YELLOW
        self.controller.update(self.simulation, 1.0)
        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.NS_YELLOW
        )

        # NS_YELLOW -> ALL_RED
        self.controller.update(self.simulation, 0.5)
        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.ALL_RED
        )

        # ALL_RED -> EW_GREEN
        self.controller.update(self.simulation, 0.5)
        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.EW_GREEN
        )

        # EW_GREEN -> EW_YELLOW
        self.controller.update(self.simulation, 1.0)
        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.EW_YELLOW
        )

        # EW_YELLOW -> ALL_RED
        self.controller.update(self.simulation, 0.5)
        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.ALL_RED
        )

        # ALL_RED -> NS_GREEN
        self.controller.update(self.simulation, 0.5)
        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.NS_GREEN
        )

    def test_reset_restores_initial_phase(self):
        self.controller.update(self.simulation, 1.0)

        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.NS_YELLOW
        )

        self.controller.reset(self.simulation)

        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.NS_GREEN
        )

        self.assertAlmostEqual(
            self.simulation.signal_state.time_remaining,
            1.0
        )

    def test_invalid_times_raise_error(self):
        with self.assertRaises(ValueError):
            FixedController(green_time=0.0)

        with self.assertRaises(ValueError):
            FixedController(green_time=-1.0)

        with self.assertRaises(ValueError):
            FixedController(yellow_time=-0.1)

        with self.assertRaises(ValueError):
            FixedController(all_red_time=-0.1)

    def test_fixed_controller_ignores_queues(self):
        # Add many vehicles to one direction.
        for _ in range(20):
            self.simulation.add_vehicle("N")

        # The fixed controller should still change phase after green_time.
        self.controller.update(self.simulation, 1.0)

        self.assertEqual(
            self.simulation.signal_state.phase,
            settings.NS_YELLOW
        )

    def test_simulation_step_uses_controller(self):
        controller = FixedController(
            green_time=1.0,
            yellow_time=0.5,
            all_red_time=0.5
        )

        simulation = Simulation(controller=controller)

        simulation.step(dt=0.5)

        self.assertEqual(
            simulation.signal_state.phase,
            settings.NS_GREEN
        )

        simulation.step(dt=0.5)

        self.assertEqual(
            simulation.signal_state.phase,
            settings.NS_YELLOW
        )


if __name__ == "__main__":
    unittest.main()