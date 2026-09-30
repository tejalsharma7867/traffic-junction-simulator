import random
import settings


class TrafficGenerator:
    """
    Generates vehicles randomly over time.

    The generator uses:
    - a base traffic intensity,
    - directional weights,
    - a random number generator.

    The generator can be seeded so that experiments are repeatable.
    """

    def __init__(self, intensity_name="MEDIUM", direction_weights=None, seed=None):
        """
        Create a traffic generator.

        Args:
            intensity_name: One of "LOW", "MEDIUM", or "HIGH".
            direction_weights: Optional dictionary of direction weights.
            seed: Optional random seed for repeatable behavior.
        """
        self.rng = random.Random(seed)

        self.set_intensity(intensity_name)

        self.direction_weights = settings.DEFAULT_DIRECTION_WEIGHTS.copy()

        if direction_weights is not None:
            self.set_direction_weights(direction_weights)

    def set_intensity(self, intensity_name):
        """
        Set the traffic intensity level.

        Args:
            intensity_name: One of "LOW", "MEDIUM", or "HIGH".
        """
        if intensity_name not in settings.TRAFFIC_INTENSITY:
            raise ValueError(f"Invalid traffic intensity: {intensity_name}")

        self.intensity_name = intensity_name
        self.base_rate = settings.TRAFFIC_INTENSITY[intensity_name]

    def set_direction_weights(self, weights):
        """
        Update directional traffic weights.

        Args:
            weights: Dictionary mapping directions to non-negative weights.
        """
        if not isinstance(weights, dict):
            raise ValueError("Direction weights must be a dictionary.")

        new_weights = self.direction_weights.copy()

        for direction, weight in weights.items():
            if direction not in settings.DIRECTIONS:
                raise ValueError(f"Invalid direction in weights: {direction}")

            if weight < 0:
                raise ValueError(f"Direction weight cannot be negative: {direction}")

            new_weights[direction] = weight

        self.direction_weights = new_weights

    def set_seed(self, seed):
        """
        Reset the random number generator with a new seed.
        """
        self.rng = random.Random(seed)

    def generate(self, simulation, dt=None):
        """
        Generate vehicles for this simulation tick.

        Args:
            simulation: The Simulation object.
            dt: Time step in seconds.

        Returns:
            A list of newly created Vehicle objects.
        """
        if dt is None:
            dt = settings.TICK_DURATION

        spawned_vehicles = []

        for direction in settings.DIRECTIONS:
            weight = self.direction_weights.get(direction, 1.0)

            # Expected number of vehicles from this direction during this tick.
            expected = self.base_rate * weight * dt

            if expected <= 0:
                continue

            # Split expected value into whole vehicles and a fractional chance.
            count = int(expected)
            fraction = expected - count

            if self.rng.random() < fraction:
                count += 1

            for _ in range(count):
                vehicle = simulation.add_vehicle(direction)
                spawned_vehicles.append(vehicle)

        return spawned_vehicles