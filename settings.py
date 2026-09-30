# Global configuration for the Adaptive Traffic Junction Simulator.

# ------------------------------------------------------------
# Simulation timing
# ------------------------------------------------------------
TICKS_PER_SECOND = 20
TICK_DURATION = 1.0 / TICKS_PER_SECOND

# ------------------------------------------------------------
# Directions
# ------------------------------------------------------------
# N = vehicle comes from the north and moves south
# S = vehicle comes from the south and moves north
# E = vehicle comes from the east and moves west
# W = vehicle comes from the west and moves east
DIRECTIONS = ("N", "S", "E", "W")

# ------------------------------------------------------------
# Default directional traffic weights
# ------------------------------------------------------------
# A weight of 1.0 means normal traffic for that direction.
# A weight of 2.0 means twice as much traffic.
# A weight of 0.0 means no traffic from that direction.
DEFAULT_DIRECTION_WEIGHTS = {
    "N": 1.0,
    "S": 1.0,
    "E": 1.0,
    "W": 1.0,
}

# ------------------------------------------------------------
# Vehicle defaults
# ------------------------------------------------------------
VEHICLE_LENGTH = 20.0
VEHICLE_GAP = 12.0
MAX_SPEED = 80.0
ACCELERATION = 60.0
DECELERATION = 120.0

# ------------------------------------------------------------
# Junction geometry
# ------------------------------------------------------------
# These values will be used later for movement and drawing.
ROAD_LENGTH = 350.0
STOP_LINE_DISTANCE = 180.0
JUNCTION_EXIT_DISTANCE = 180.0

# ------------------------------------------------------------
# Traffic intensity presets
# ------------------------------------------------------------
# These are approximate spawn rates per direction per second.
TRAFFIC_INTENSITY = {
    "LOW": 0.25,
    "MEDIUM": 0.60,
    "HIGH": 1.10,
}

# ------------------------------------------------------------
# Fixed signal timing
# ------------------------------------------------------------
FIXED_GREEN_TIME = 6.0
YELLOW_TIME = 1.5
ALL_RED_TIME = 0.5

# ------------------------------------------------------------
# Signal phases
# ------------------------------------------------------------
NS_GREEN = "NS_GREEN"
NS_YELLOW = "NS_YELLOW"
EW_GREEN = "EW_GREEN"
EW_YELLOW = "EW_YELLOW"
ALL_RED = "ALL_RED"

SIGNAL_PHASES = (
    NS_GREEN,
    NS_YELLOW,
    EW_GREEN,
    EW_YELLOW,
    ALL_RED,
)

# Small value used to avoid floating-point comparison problems.
MOVEMENT_EPSILON = 1e-6

# ------------------------------------------------------------
# Adaptive controller limits
# ------------------------------------------------------------
MIN_GREEN_TIME = 3.0
MAX_GREEN_TIME = 12.0
SECONDS_ADDED_PER_WAITING_VEHICLE = 0.35

# ------------------------------------------------------------
# Window settings
# ------------------------------------------------------------
WINDOW_WIDTH = 1150
WINDOW_HEIGHT = 720

# ------------------------------------------------------------
# Visual and UI settings
# ------------------------------------------------------------
ROAD_WIDTH = 140
LANE_OFFSET = 35
VEHICLE_WIDTH = 12

PANEL_WIDTH = 360
FPS = 60

# ------------------------------------------------------------
# Exit animation settings
# ------------------------------------------------------------
SCREEN_STOP_OFFSET = ROAD_WIDTH // 2 + 20
SCREEN_OFFSCREEN_MARGIN = 80