import unittest

import settings
from core.simulation import Simulation
from control.adaptive_controller import AdaptiveController


class TestAdaptiveController(unittest.TestCase):
    """
    Tests for the adaptive traffic signal controller.
    """

    def setUp(self):
        self.controller = AdaptiveController(
            min_green=3.0,
            max_green=10.0,
            yellow_time=1.0,
            all_red_time=0.5,
            time_per_vehicle=1.0
        )
        self.simulation = Simulation(controller=self.controller)

    def test_invalid_times_raise_error(self):
        with self.assertRaises(ValueError):
            AdaptiveController(min_green=0.0)
        with self.assertRaises(ValueError):
            AdaptiveController(min_green=5.0, max_green=3.0)
        with self.assertRaises(ValueError):
            AdaptiveController(time_per_vehicle=-1.0)

    def test_initial_phase_is_ns_green(self):
        self.assertEqual(self.simulation.signal_state.phase, settings.NS_GREEN)
        self.assertAlmostEqual(self.simulation.signal_state.time_remaining, 3.0)

    def test_phase_transitions(self):
        # NS_GREEN -> NS_YELLOW
        self.controller.update(self.simulation, 3.0)
        self.assertEqual(self.simulation.signal_state.phase, settings.NS_YELLOW)

        # NS_YELLOW -> ALL_RED
        self.controller.update(self.simulation, 1.0)
        self.assertEqual(self.simulation.signal_state.phase, settings.ALL_RED)

        # ALL_RED -> EW_GREEN (since demands are 0, it defaults to EW or NS based on tie-breaker, let's just check it's a green phase)
        self.controller.update(self.simulation, 0.5)
        self.assertIn(
            self.simulation.signal_state.phase, 
            [settings.NS_GREEN, settings.EW_GREEN]
        )

    def test_dynamic_green_time_low_demand(self):
        # 0 vehicles waiting. Demand = 0.
        # Expected green time = min_green (3.0)
        next_phase, green_time = self.controller._decide_next_green(self.simulation)
        self.assertAlmostEqual(green_time, 3.0)

    def test_dynamic_green_time_high_demand(self):
        # Add 10 vehicles to North
        for _ in range(10):
            v = self.simulation.add_vehicle("N")
            v.state = "approaching"
            
        self.simulation.stats.update(self.simulation)
        
        # Demand = 10. Expected raw time = 3.0 + (10 * 1.0) = 13.0
        # Should be clamped to max_green (10.0)
        next_phase, green_time = self.controller._decide_next_green(self.simulation)
        
        self.assertEqual(next_phase, settings.NS_GREEN)
        self.assertAlmostEqual(green_time, 10.0)

    def test_adaptive_decision_picks_busier_side(self):
        # Add 5 vehicles to East
        for _ in range(5):
            v = self.simulation.add_vehicle("E")
            v.state = "approaching"
            
        # Add 1 vehicle to North
        v = self.simulation.add_vehicle("N")
        v.state = "approaching"
        
        self.simulation.stats.update(self.simulation)
        
        next_phase, _ = self.controller._decide_next_green(self.simulation)
        
        self.assertEqual(next_phase, settings.EW_GREEN)

    def test_fairness_prevents_starvation(self):
        # Setup: EW has more vehicles, but NS has been waiting a very long time.
        
        # 1 vehicle in N, waiting for 20 seconds
        v1 = self.simulation.add_vehicle("N")
        v1.wait_time = 20.0
        v1.state = "approaching"
        
        # 3 vehicles in E, waiting for 1 second
        for _ in range(3):
            v = self.simulation.add_vehicle("E")
            v.wait_time = 1.0
            v.state = "approaching"
            
        self.simulation.stats.update(self.simulation)
        
        # Base demand: NS = 1, EW = 3.
        # With fairness (threshold 15s, bonus 5.0): NS = 1 + 5 = 6. EW = 3.
        # NS should win.
        next_phase, _ = self.controller._decide_next_green(self.simulation)
        
        self.assertEqual(next_phase, settings.NS_GREEN)

    def test_reset_restores_initial_state(self):
        self.controller.update(self.simulation, 3.0) # Move to yellow
        self.controller.reset(self.simulation)
        
        self.assertEqual(self.simulation.signal_state.phase, settings.NS_GREEN)
        self.assertAlmostEqual(self.simulation.signal_state.time_remaining, 3.0)


if __name__ == "__main__":
    unittest.main()