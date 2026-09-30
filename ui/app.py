import pygame

import settings
from core.simulation import Simulation
from core.traffic_generator import TrafficGenerator
from control.fixed_controller import FixedController
from control.adaptive_controller import AdaptiveController

from ui import renderer, hud, theme
from ui.controls import Button


class App:
    """
    Main interactive Pygame application.
    """

    def __init__(self, intensity_name="MEDIUM", mode="adaptive", seed=42):
        """
        Create the application.

        Args:
            intensity_name: Initial traffic intensity.
            mode: Initial controller mode, "fixed" or "adaptive".
            seed: Random seed for traffic generation.
        """
        pygame.init()
        pygame.display.set_caption("Adaptive Traffic Junction Simulator")

        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        )

        self.clock = pygame.time.Clock()

        self.fonts = {
            "title": pygame.font.Font(None, 30),
            "medium": pygame.font.Font(None, 24),
            "small": pygame.font.Font(None, 20),
            "button": pygame.font.Font(None, 22),
        }

        self.seed = seed
        self.generator = TrafficGenerator(
            intensity_name=intensity_name,
            seed=seed
        )

        self.mode = mode
        self.controller = self._create_controller()

        self.simulation = Simulation(
            traffic_generator=self.generator,
            controller=self.controller
        )

        self.speed_options = [1, 2, 4]
        self.speed_index = 0
        self.speed_multiplier = self.speed_options[self.speed_index]

        self.accumulator = 0.0
        self.running = True

        self.panel_rect = pygame.Rect(
            settings.WINDOW_WIDTH - settings.PANEL_WIDTH,
            0,
            settings.PANEL_WIDTH,
            settings.WINDOW_HEIGHT
        )

        self.buttons = self._create_buttons()

    def _create_controller(self):
        """
        Create the controller for the current mode.

        Returns:
            FixedController or AdaptiveController.
        """
        if self.mode == "fixed":
            return FixedController()

        return AdaptiveController()

    def _create_buttons(self):
        """
        Create UI buttons.

        Returns:
            List of Button objects.
        """
        panel_x = self.panel_rect.x
        margin = 20

        button_width = 150
        button_height = 36
        gap = 20

        row_1_y = 140
        row_2_y = row_1_y + 46
        row_3_y = row_2_y + 46
        row_4_y = row_3_y + 46

        buttons = []

        buttons.append(
            Button(
                pygame.Rect(
                    panel_x + margin,
                    row_1_y,
                    button_width,
                    button_height
                ),
                lambda: "Resume" if self.simulation.paused else "Pause",
                self.toggle_pause
            )
        )

        buttons.append(
            Button(
                pygame.Rect(
                    panel_x + margin + button_width + gap,
                    row_1_y,
                    button_width,
                    button_height
                ),
                "Reset",
                self.reset_simulation
            )
        )

        buttons.append(
            Button(
                pygame.Rect(
                    panel_x + margin,
                    row_2_y,
                    button_width,
                    button_height
                ),
                "Fixed",
                lambda: self.set_mode("fixed"),
                active=lambda: self.mode == "fixed"
            )
        )

        buttons.append(
            Button(
                pygame.Rect(
                    panel_x + margin + button_width + gap,
                    row_2_y,
                    button_width,
                    button_height
                ),
                "Adaptive",
                lambda: self.set_mode("adaptive"),
                active=lambda: self.mode == "adaptive"
            )
        )

        intensity_levels = ["LOW", "MEDIUM", "HIGH"]
        intensity_button_width = 100
        intensity_gap = 10

        for index, level in enumerate(intensity_levels):
            rect = pygame.Rect(
                panel_x + margin + index * (intensity_button_width + intensity_gap),
                row_3_y,
                intensity_button_width,
                button_height
            )

            buttons.append(
                Button(
                    rect,
                    level.capitalize(),
                    lambda selected_level=level: self.set_intensity(selected_level),
                    active=lambda selected_level=level: self.generator.intensity_name == selected_level
                )
            )

        buttons.append(
            Button(
                pygame.Rect(
                    panel_x + margin,
                    row_4_y,
                    self.panel_rect.width - margin * 2,
                    button_height
                ),
                lambda: f"Speed: {self.speed_multiplier}x",
                self.cycle_speed
            )
        )

        return buttons

    def toggle_pause(self):
        """
        Pause or resume the simulation.
        """
        self.simulation.toggle_pause()

    def reset_simulation(self):
        """
        Reset the simulation and generator seed.
        """
        self.simulation.reset()
        self.generator.set_seed(self.seed)

        self.accumulator = 0.0
        self.simulation.paused = False

    def set_mode(self, mode):
        """
        Switch between fixed and adaptive control.

        Args:
            mode: "fixed" or "adaptive".
        """
        if mode == self.mode:
            return

        self.mode = mode
        self.controller = self._create_controller()
        self.simulation.set_controller(self.controller)

    def set_intensity(self, intensity_name):
        """
        Set traffic intensity.

        Args:
            intensity_name: "LOW", "MEDIUM", or "HIGH".
        """
        self.generator.set_intensity(intensity_name)

    def cycle_speed(self):
        """
        Cycle simulation speed multiplier.
        """
        self.speed_index = (self.speed_index + 1) % len(self.speed_options)
        self.speed_multiplier = self.speed_options[self.speed_index]

    def handle_events(self):
        """
        Handle Pygame events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.running = False

                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()

                elif event.key == pygame.K_r:
                    self.reset_simulation()

                elif event.key == pygame.K_m:
                    if self.mode == "fixed":
                        self.set_mode("adaptive")
                    else:
                        self.set_mode("fixed")

                elif event.key == pygame.K_1:
                    self.set_intensity("LOW")

                elif event.key == pygame.K_2:
                    self.set_intensity("MEDIUM")

                elif event.key == pygame.K_3:
                    self.set_intensity("HIGH")

                elif event.key == pygame.K_s:
                    self.cycle_speed()

            else:
                for button in self.buttons:
                    button.handle_event(event)

    def update(self):
        """
        Update the simulation using a fixed time step.
        """
        dt = self.clock.tick(settings.FPS) / 1000.0

        if not self.simulation.paused:
            self.accumulator += dt * self.speed_multiplier

            steps = 0

            while self.accumulator >= settings.TICK_DURATION and steps < 20:
                self.simulation.step(settings.TICK_DURATION)
                self.accumulator -= settings.TICK_DURATION
                steps += 1

            # Prevent the simulation from trying to catch up too much.
            if steps == 20:
                self.accumulator = 0.0
        else:
            self.accumulator = 0.0

    def draw(self):
        """
        Draw the full application window.
        """
        self.screen.fill(theme.BACKGROUND)

        renderer.draw_simulation(self.screen, self.simulation)

        hud.draw_panel(
            self.screen,
            self.simulation,
            self.panel_rect,
            self.fonts,
            self.mode,
            self.speed_multiplier,
            self.buttons
        )

        pygame.display.flip()

    def run(self):
        """
        Run the main application loop.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()