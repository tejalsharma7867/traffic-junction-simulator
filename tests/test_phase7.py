import unittest
import pygame
import settings
from core.vehicle import Vehicle
from ui import renderer, theme
from ui.controls import Button


class TestPhase7Smoke(unittest.TestCase):
    """
    Basic smoke tests for Phase 7 UI components.
    """

    def test_signal_color_for_ns_green(self):
        color = renderer.signal_color_for(settings.NS_GREEN, "N")
        self.assertEqual(color, theme.GREEN)

        color = renderer.signal_color_for(settings.NS_GREEN, "S")
        self.assertEqual(color, theme.GREEN)

    def test_signal_color_for_all_red(self):
        color = renderer.signal_color_for(settings.ALL_RED, "N")
        self.assertEqual(color, theme.RED)

        color = renderer.signal_color_for(settings.ALL_RED, "E")
        self.assertEqual(color, theme.RED)

    def test_button_creation_and_callback(self):
        clicked = []

        button = Button(
            pygame.Rect(0, 0, 100, 40),
            "Test",
            lambda: clicked.append(True)
        )

        self.assertEqual(button.get_label(), "Test")

        button.on_click()

        self.assertTrue(clicked)

    def test_vehicle_screen_center_north(self):
        sim_rect = pygame.Rect(
            0,
            0,
            settings.WINDOW_WIDTH - settings.PANEL_WIDTH,
            settings.WINDOW_HEIGHT
        )

        vehicle = Vehicle(id=1, direction="N")
        vehicle.position = settings.STOP_LINE_DISTANCE

        center = renderer.vehicle_screen_center(vehicle, sim_rect)

        # A north vehicle at the stop line should be above the junction center.
        self.assertLess(center[1], sim_rect.centery)

    def test_theme_colors_are_rgb(self):
        self.assertEqual(len(theme.BACKGROUND), 3)
        self.assertEqual(len(theme.TEXT), 3)
        self.assertEqual(len(theme.RED), 3)


if __name__ == "__main__":
    unittest.main()