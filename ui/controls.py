import pygame
from ui import theme


class Button:
    """
    A simple clickable UI button.
    """

    def __init__(self, rect, label, on_click, active=False):
        """
        Create a button.

        Args:
            rect: pygame.Rect for the button.
            label: Button text, or a function returning text.
            on_click: Function to call when clicked.
            active: Boolean or function returning boolean for active styling.
        """
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.active = active
        self.hover = False

    def get_label(self):
        """
        Return the current button label.
        """
        if callable(self.label):
            return self.label()

        return self.label

    def is_active(self):
        """
        Return whether the button should be drawn as active.
        """
        if callable(self.active):
            return self.active()

        return self.active

    def handle_event(self, event):
        """
        Handle Pygame events for this button.

        Args:
            event: Pygame event.

        Returns:
            True if the button was clicked, otherwise False.
        """
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.on_click()
                return True

        return False

    def draw(self, surface, font):
        """
        Draw the button.

        Args:
            surface: Pygame surface.
            font: Pygame font.
        """
        if self.is_active():
            background = theme.BUTTON_ACTIVE
        elif self.hover:
            background = theme.BUTTON_HOVER
        else:
            background = theme.BUTTON

        pygame.draw.rect(
            surface,
            background,
            self.rect,
            border_radius=8
        )

        pygame.draw.rect(
            surface,
            theme.ROAD_EDGE,
            self.rect,
            width=1,
            border_radius=8
        )

        text_image = font.render(self.get_label(), True, theme.BUTTON_TEXT)
        text_rect = text_image.get_rect(center=self.rect.center)

        surface.blit(text_image, text_rect)