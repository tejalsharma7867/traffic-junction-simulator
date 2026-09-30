import settings


class SignalState:
    """
    Represents the current traffic signal state.

    This Phase 3 version only stores the current phase and remaining time.
    The actual fixed and adaptive controllers will be added later.
    """

    def __init__(self):
        """
        Initialize the signal state.
        """
        self.reset()

    def reset(self):
        """
        Reset the signal state to the default state.
        """
        self.phase = settings.ALL_RED
        self.time_remaining = 0.0

    def set_phase(self, phase, duration=0.0):
        """
        Set the current signal phase.

        Args:
            phase: One of the valid signal phases.
            duration: Optional time remaining in this phase.
        """
        if phase not in settings.SIGNAL_PHASES:
            raise ValueError(f"Invalid signal phase: {phase}")

        if duration < 0:
            raise ValueError("Signal phase duration cannot be negative.")

        self.phase = phase
        self.time_remaining = duration

    def update(self, dt):
        """
        Reduce remaining phase time.

        Args:
            dt: Time step in seconds.
        """
        if self.time_remaining > 0:
            self.time_remaining -= dt

            if self.time_remaining < 0:
                self.time_remaining = 0.0

    def is_green_for(self, direction):
        """
        Check whether the current phase gives green to a direction.

        Args:
            direction: One of "N", "S", "E", or "W".

        Returns:
            True if the direction currently has green, otherwise False.
        """
        if direction in ("N", "S"):
            return self.phase == settings.NS_GREEN

        if direction in ("E", "W"):
            return self.phase == settings.EW_GREEN

        return False

    def can_enter_junction(self, direction):
        """
        Check whether a vehicle from this direction may enter the junction.

        Args:
            direction: One of "N", "S", "E", or "W".

        Returns:
            True if the vehicle may enter the junction, otherwise False.
        """
        return self.is_green_for(direction)