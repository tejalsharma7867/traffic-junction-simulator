from dataclasses import dataclass
import settings


@dataclass
class Vehicle:
    """
    Represents one vehicle in the simulation.

    Attributes:
        id: Unique vehicle identification number.
        direction: Direction from which the vehicle arrives.
        arrival_time: Simulation time when the vehicle entered the system.
        position: Distance travelled along its approach lane.
        speed: Current speed of the vehicle.
        length: Length of the vehicle.
        wait_time: Total time spent waiting.
        state: Current state of the vehicle.
    """

    id: int
    direction: str
    arrival_time: float = 0.0
    position: float = 0.0
    speed: float = 0.0
    length: float = settings.VEHICLE_LENGTH
    wait_time: float = 0.0
    state: str = "approaching"

    def __post_init__(self):
        """
        Validate vehicle data after initialization.
        """
        if self.direction not in settings.DIRECTIONS:
            raise ValueError(f"Invalid vehicle direction: {self.direction}")