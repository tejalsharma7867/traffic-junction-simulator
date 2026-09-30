import pygame

import settings
from ui import theme


def draw_text(surface, font, text, color, x, y, align="left"):
    """
    Draw text at a position.

    Args:
        surface: Pygame surface.
        font: Pygame font.
        text: Text string.
        color: RGB color.
        x: X coordinate.
        y: Y coordinate.
        align: "left", "center", or "right".
    """
    image = font.render(text, True, color)
    rect = image.get_rect()

    if align == "left":
        rect.topleft = (x, y)
    elif align == "center":
        rect.center = (x, y)
    elif align == "right":
        rect.topright = (x, y)

    surface.blit(image, rect)

    return rect


def draw_bar(surface, x, y, width, height, fraction, color):
    """
    Draw a horizontal bar.

    Args:
        surface: Pygame surface.
        x: X position.
        y: Y position.
        width: Bar width.
        height: Bar height.
        fraction: Fill fraction from 0 to 1.
        color: Fill color.
    """
    fraction = max(0.0, min(1.0, fraction))

    background_rect = pygame.Rect(x, y, width, height)

    pygame.draw.rect(
        surface,
        theme.BUTTON,
        background_rect,
        border_radius=4
    )

    fill_width = int(width * fraction)

    if fill_width > 0:
        fill_rect = pygame.Rect(x, y, fill_width, height)

        pygame.draw.rect(
            surface,
            color,
            fill_rect,
            border_radius=4
        )

    pygame.draw.rect(
        surface,
        theme.ROAD_EDGE,
        background_rect,
        width=1,
        border_radius=4
    )


def draw_panel(surface, simulation, panel_rect, fonts, mode, speed_multiplier, buttons):
    """
    Draw the side panel containing controls and live statistics.

    Args:
        surface: Pygame surface.
        simulation: Simulation object.
        panel_rect: Rectangle for the side panel.
        fonts: Dictionary of pygame fonts.
        mode: Current controller mode.
        speed_multiplier: Current simulation speed multiplier.
        buttons: List of Button objects.
    """
    pygame.draw.rect(surface, theme.PANEL_BG, panel_rect)

    pygame.draw.line(
        surface,
        theme.ROAD_EDGE,
        panel_rect.topleft,
        panel_rect.bottomleft,
        2
    )

    x = panel_rect.x + 20
    y = panel_rect.y + 18

    draw_text(
        surface,
        fonts["title"],
        "ADAPTIVE TRAFFIC JUNCTION",
        theme.TEXT,
        x,
        y
    )

    y += 34

    status = "Paused" if simulation.paused else "Running"
    status_color = theme.YELLOW if simulation.paused else theme.GREEN

    draw_text(
        surface,
        fonts["small"],
        f"Status: {status}",
        status_color,
        x,
        y
    )

    y += 22

    draw_text(
        surface,
        fonts["small"],
        f"Mode: {mode.capitalize()}",
        theme.TEXT,
        x,
        y
    )

    y += 22

    draw_text(
        surface,
        fonts["small"],
        f"Phase: {simulation.signal_state.phase}",
        theme.TEXT,
        x,
        y
    )

    y += 22

    draw_text(
        surface,
        fonts["small"],
        f"Time: {simulation.time:.1f}s   Tick: {simulation.tick}",
        theme.TEXT_DIM,
        x,
        y
    )

    # Buttons are positioned by the application.
    for button in buttons:
        button.draw(surface, fonts["button"])

    # Statistics begin below the button area.
    y = 330

    stats = simulation.get_statistics()

    draw_text(
        surface,
        fonts["medium"],
        "Live Statistics",
        theme.TEXT,
        x,
        y
    )

    y += 26

    stat_lines = [
        f"Generated: {stats['total_generated']}",
        f"Passed: {stats['total_passed']}",
        f"Active: {stats['active_vehicles']}",
        f"Waiting: {stats['vehicles_currently_waiting']}",
        f"Avg wait finished: {stats['average_wait_time_finished']:.2f}s",
        f"Max wait observed: {stats['max_wait_time_observed']:.2f}s",
        f"Avg queue length: {stats['average_queue_length']:.2f}",
        f"Max queue length: {stats['max_queue_length']}",
    ]

    for line in stat_lines:
        draw_text(
            surface,
            fonts["small"],
            line,
            theme.TEXT_DIM,
            x,
            y
        )
        y += 20

    y += 6

    if mode.lower() == "adaptive":
        ns_demand = (
            stats["current_queue_by_direction"]["N"]
            + stats["current_queue_by_direction"]["S"]
        )

        ew_demand = (
            stats["current_queue_by_direction"]["E"]
            + stats["current_queue_by_direction"]["W"]
        )

        draw_text(
            surface,
            fonts["small"],
            f"NS demand: {ns_demand}   EW demand: {ew_demand}",
            theme.TEXT,
            x,
            y
        )

        y += 20

        draw_text(
            surface,
            fonts["small"],
            f"Green limits: {settings.MIN_GREEN_TIME:.0f}s to {settings.MAX_GREEN_TIME:.0f}s",
            theme.TEXT_DIM,
            x,
            y
        )

    else:
        draw_text(
            surface,
            fonts["small"],
            f"Fixed green: {settings.FIXED_GREEN_TIME:.1f}s",
            theme.TEXT,
            x,
            y
        )

        y += 20

        draw_text(
            surface,
            fonts["small"],
            f"Yellow: {settings.YELLOW_TIME:.1f}s   All-red: {settings.ALL_RED_TIME:.1f}s",
            theme.TEXT_DIM,
            x,
            y
        )

    y += 18

    draw_text(
        surface,
        fonts["medium"],
        "Queue by Direction",
        theme.TEXT,
        x,
        y
    )

    y += 26

    queue_by_direction = stats["current_queue_by_direction"]
    max_current_queue = max(queue_by_direction.values())
    scale = max(10, max_current_queue)

    for direction in settings.DIRECTIONS:
        count = queue_by_direction[direction]

        draw_text(
            surface,
            fonts["small"],
            direction,
            theme.TEXT,
            x,
            y + 2
        )

        draw_bar(
            surface,
            x + 28,
            y,
            200,
            14,
            count / scale,
            theme.VEHICLE_COLORS[direction]
        )

        draw_text(
            surface,
            fonts["small"],
            str(count),
            theme.TEXT_DIM,
            x + 28 + 200 + 10,
            y + 2
        )

        y += 24