import unittest
import pygame
import settings
from core.vehicle import Vehicle
from ui import renderer


class TestExitAnimation(unittest.TestCase):
    """
    Tests that vehicles are drawn off-screen when they exit.
    """

    def setUp(self):
        self.sim_rect = pygame.Rect(
            0,
            0,
            settings.WINDOW_WIDTH - settings.PANEL_WIDTH,
            settings.WINDOW_HEIGHT
        )

    def test_north_vehicle_is_off_screen_at_exit(self):
        vehicle = Vehicle(id=1, direction="N")
        vehicle.position = settings.STOP_LINE_DISTANCE + settings.JUNCTION_EXIT_DISTANCE

        center = renderer.vehicle_screen_center(vehicle, self.sim_rect)

        self.assertGreater(center[1], self.sim_rect.bottom)

    def test_south_vehicle_is_off_screen_at_exit(self):
        vehicle = Vehicle(id=1, direction="S")
        vehicle.position = settings.STOP_LINE_DISTANCE + settings.JUNCTION_EXIT_DISTANCE

        center = renderer.vehicle_screen_center(vehicle, self.sim_rect)

        self.assertLess(center[1], self.sim_rect.top)

    def test_east_vehicle_is_off_screen_at_exit(self):
        vehicle = Vehicle(id=1, direction="E")
        vehicle.position = settings.STOP_LINE_DISTANCE + settings.JUNCTION_EXIT_DISTANCE

        center = renderer.vehicle_screen_center(vehicle, self.sim_rect)

        self.assertLess(center[0], self.sim_rect.left)

    def test_west_vehicle_is_off_screen_at_exit(self):
        vehicle = Vehicle(id=1, direction="W")
        vehicle.position = settings.STOP_LINE_DISTANCE + settings.JUNCTION_EXIT_DISTANCE

        center = renderer.vehicle_screen_center(vehicle, self.sim_rect)

        self.assertGreater(center[0], self.sim_rect.right)


if __name__ == "__main__":
    unittest.main()