import math
import pygame
import settings
from ui import theme


def _interpolate(value, from_min, from_max, to_min, to_max):
    """
    Linearly interpolate a value from one range to another.
    """
    if from_max == from_min:
        return to_min

    t = (value - from_min) / (from_max - from_min)

    return to_min + (to_max - to_min) * t


def simulation_area_rect():
    """
    Return the rectangle used for the junction view.
    """
    width = settings.WINDOW_WIDTH - settings.PANEL_WIDTH
    height = settings.WINDOW_HEIGHT

    return pygame.Rect(0, 0, width, height)


def draw_dashed_line(surface, color, start, end, width=2, dash_length=14, gap_length=10):
    """
    Draw a dashed line between two points.
    """
    x1, y1 = start
    x2, y2 = end

    dx = x2 - x1
    dy = y2 - y1

    distance = math.hypot(dx, dy)

    if distance <= 0:
        return

    dash_gap_total = dash_length + gap_length
    segment_count = int(distance // dash_gap_total) + 1

    for i in range(segment_count):
        segment_start = i * dash_gap_total
        segment_end = min(distance, segment_start + dash_length)

        if segment_start >= distance:
            break

        start_x = x1 + dx * segment_start / distance
        start_y = y1 + dy * segment_start / distance

        end_x = x1 + dx * segment_end / distance
        end_y = y1 + dy * segment_end / distance

        pygame.draw.line(
            surface,
            color,
            (start_x, start_y),
            (end_x, end_y),
            width
        )


def draw_roads(surface, sim_rect):
    """
    Draw the roads, lane markings, and stop lines.
    """
    center_x, center_y = sim_rect.center
    road_half = settings.ROAD_WIDTH // 2

    vertical_road = pygame.Rect(
        center_x - road_half,
        sim_rect.top,
        settings.ROAD_WIDTH,
        sim_rect.height
    )

    horizontal_road = pygame.Rect(
        sim_rect.left,
        center_y - road_half,
        sim_rect.width,
        settings.ROAD_WIDTH
    )

    pygame.draw.rect(surface, theme.ROAD, vertical_road)
    pygame.draw.rect(surface, theme.ROAD, horizontal_road)

    pygame.draw.rect(surface, theme.ROAD_EDGE, vertical_road, width=2)
    pygame.draw.rect(surface, theme.ROAD_EDGE, horizontal_road, width=2)

    junction_top = center_y - road_half
    junction_bottom = center_y + road_half
    junction_left = center_x - road_half
    junction_right = center_x + road_half

    # Vertical lane dashes.
    draw_dashed_line(
        surface,
        theme.LANE_MARK,
        (center_x, sim_rect.top),
        (center_x, junction_top)
    )

    draw_dashed_line(
        surface,
        theme.LANE_MARK,
        (center_x, junction_bottom),
        (center_x, sim_rect.bottom)
    )

    # Horizontal lane dashes.
    draw_dashed_line(
        surface,
        theme.LANE_MARK,
        (sim_rect.left, center_y),
        (junction_left, center_y)
    )

    draw_dashed_line(
        surface,
        theme.LANE_MARK,
        (junction_right, center_y),
        (sim_rect.right, center_y)
    )

    stop_offset = settings.SCREEN_STOP_OFFSET

    # North approach stop line.
    pygame.draw.line(
        surface,
        theme.STOP_LINE,
        (center_x - road_half, center_y - stop_offset),
        (center_x, center_y - stop_offset),
        4
    )

    # South approach stop line.
    pygame.draw.line(
        surface,
        theme.STOP_LINE,
        (center_x, center_y + stop_offset),
        (center_x + road_half, center_y + stop_offset),
        4
    )

    # East approach stop line.
    pygame.draw.line(
        surface,
        theme.STOP_LINE,
        (center_x + stop_offset, center_y),
        (center_x + stop_offset, center_y + road_half),
        4
    )

    # West approach stop line.
    pygame.draw.line(
        surface,
        theme.STOP_LINE,
        (center_x - stop_offset, center_y - road_half),
        (center_x - stop_offset, center_y),
        4
    )


def signal_color_for(phase, direction):
    """
    Return the signal color for a direction.
    """
    if direction in ("N", "S"):
        if phase == settings.NS_GREEN:
            return theme.GREEN

        if phase == settings.NS_YELLOW:
            return theme.YELLOW

        return theme.RED

    if direction in ("E", "W"):
        if phase == settings.EW_GREEN:
            return theme.GREEN

        if phase == settings.EW_YELLOW:
            return theme.YELLOW

        return theme.RED

    return theme.RED


def draw_signals(surface, simulation, sim_rect):
    """
    Draw traffic signal indicators for each approach.
    """
    phase = simulation.signal_state.phase

    center_x, center_y = sim_rect.center

    road_half = settings.ROAD_WIDTH // 2
    stop_offset = settings.SCREEN_STOP_OFFSET

    signal_positions = {
        "N": (center_x - road_half - 18, center_y - stop_offset),
        "S": (center_x + road_half + 18, center_y + stop_offset),
        "E": (center_x + stop_offset, center_y + road_half + 18),
        "W": (center_x - stop_offset, center_y - road_half - 18),
    }

    for direction, position in signal_positions.items():
        color = signal_color_for(phase, direction)

        pygame.draw.circle(surface, theme.PANEL_BG, position, 10)
        pygame.draw.circle(surface, color, position, 7)
        pygame.draw.circle(surface, theme.ROAD_EDGE, position, 10, width=2)


def vehicle_screen_center(vehicle, sim_rect):
    """
    Convert a vehicle simulation position to screen coordinates.

    Vehicles enter from off-screen and exit off-screen.
    """
    stop_line = settings.STOP_LINE_DISTANCE
    exit_position = stop_line + settings.JUNCTION_EXIT_DISTANCE

    center_x, center_y = sim_rect.center

    stop_offset = settings.SCREEN_STOP_OFFSET
    margin = settings.SCREEN_OFFSCREEN_MARGIN

    if vehicle.direction == "N":
        lane_x = center_x - settings.LANE_OFFSET
        stop_y = center_y - stop_offset

        if vehicle.position <= stop_line:
            front_y = _interpolate(
                vehicle.position,
                0.0,
                stop_line,
                sim_rect.top - margin,
                stop_y
            )
        else:
            front_y = _interpolate(
                vehicle.position,
                stop_line,
                exit_position,
                stop_y,
                sim_rect.bottom + margin
            )

        return (
            lane_x,
            front_y - vehicle.length / 2.0
        )

    if vehicle.direction == "S":
        lane_x = center_x + settings.LANE_OFFSET
        stop_y = center_y + stop_offset

        if vehicle.position <= stop_line:
            front_y = _interpolate(
                vehicle.position,
                0.0,
                stop_line,
                sim_rect.bottom + margin,
                stop_y
            )
        else:
            front_y = _interpolate(
                vehicle.position,
                stop_line,
                exit_position,
                stop_y,
                sim_rect.top - margin
            )

        return (
            lane_x,
            front_y + vehicle.length / 2.0
        )

    if vehicle.direction == "E":
        lane_y = center_y + settings.LANE_OFFSET
        stop_x = center_x + stop_offset

        if vehicle.position <= stop_line:
            front_x = _interpolate(
                vehicle.position,
                0.0,
                stop_line,
                sim_rect.right + margin,
                stop_x
            )
        else:
            front_x = _interpolate(
                vehicle.position,
                stop_line,
                exit_position,
                stop_x,
                sim_rect.left - margin
            )

        return (
            front_x + vehicle.length / 2.0,
            lane_y
        )

    # vehicle.direction == "W"
    lane_y = center_y - settings.LANE_OFFSET
    stop_x = center_x - stop_offset

    if vehicle.position <= stop_line:
        front_x = _interpolate(
            vehicle.position,
            0.0,
            stop_line,
            sim_rect.left - margin,
            stop_x
        )
    else:
        front_x = _interpolate(
            vehicle.position,
            stop_line,
            exit_position,
            stop_x,
            sim_rect.right + margin
        )

    return (
        front_x - vehicle.length / 2.0,
        lane_y
    )


def draw_vehicles(surface, simulation, sim_rect):
    """
    Draw all active vehicles.
    """
    for vehicle in simulation.vehicles:
        vehicle_center = vehicle_screen_center(vehicle, sim_rect)

        color = theme.VEHICLE_COLORS.get(vehicle.direction, theme.TEXT)

        if vehicle.direction in ("N", "S"):
            rect = pygame.Rect(
                0,
                0,
                settings.VEHICLE_WIDTH,
                vehicle.length
            )
        else:
            rect = pygame.Rect(
                0,
                0,
                vehicle.length,
                settings.VEHICLE_WIDTH
            )

        rect.center = vehicle_center

        # Draw a subtle brake outline for stopped vehicles.
        if vehicle.state == "approaching" and vehicle.speed <= settings.MOVEMENT_EPSILON:
            brake_rect = rect.inflate(4, 4)
            pygame.draw.rect(surface, theme.RED, brake_rect, border_radius=4)

        pygame.draw.rect(surface, color, rect, border_radius=3)
        pygame.draw.rect(surface, theme.ROAD_EDGE, rect, width=1, border_radius=3)


def draw_simulation(surface, simulation):
    """
    Draw the full junction view.
    """
    sim_rect = simulation_area_rect()

    pygame.draw.rect(surface, theme.BACKGROUND, sim_rect)

    draw_roads(surface, sim_rect)
    draw_signals(surface, simulation, sim_rect)
    draw_vehicles(surface, simulation, sim_rect)