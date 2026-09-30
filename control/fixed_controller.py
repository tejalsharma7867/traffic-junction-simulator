import settings


class FixedController:
    """
    Fixed-time traffic signal controller.

    This controller cycles through phases using fixed durations.
    It does not respond to traffic conditions.
    """

    def __init__(self, green_time=None, yellow_time=None, all_red_time=None):
        """
        Create a fixed-time controller.

        Args:
            green_time: Green phase duration in seconds.
            yellow_time: Yellow phase duration in seconds.
            all_red_time: All-red clearance duration in seconds.
        """
        if green_time is None:
            green_time = settings.FIXED_GREEN_TIME

        if yellow_time is None:
            yellow_time = settings.YELLOW_TIME

        if all_red_time is None:
            all_red_time = settings.ALL_RED_TIME

        self.green_time = green_time
        self.yellow_time = yellow_time
        self.all_red_time = all_red_time

        self._validate_times()

        # The fixed phase sequence.
        #
        # ALL_RED appears twice:
        # once after NS green, and once after EW green.
        self.phase_sequence = (
            settings.NS_GREEN,
            settings.NS_YELLOW,
            settings.ALL_RED,
            settings.EW_GREEN,
            settings.EW_YELLOW,
            settings.ALL_RED,
        )

        self.phase_index = 0

    def _validate_times(self):
        """
        Check that timing values are valid.
        """
        if self.green_time <= 0:
            raise ValueError("Green time must be greater than zero.")

        if self.yellow_time < 0:
            raise ValueError("Yellow time cannot be negative.")

        if self.all_red_time < 0:
            raise ValueError("All-red time cannot be negative.")

    def reset(self, simulation=None):
        """
        Reset the controller to the beginning of its cycle.

        Args:
            simulation: The Simulation object to update.
        """
        self.phase_index = 0

        if simulation is not None:
            self._apply_current_phase(simulation)

    def update(self, simulation, dt):
        """
        Update the fixed controller for one simulation tick.

        Args:
            simulation: The Simulation object.
            dt: Time step in seconds.
        """
        if dt <= 0:
            return

        signal = simulation.signal_state

        signal.time_remaining -= dt

        if signal.time_remaining <= settings.MOVEMENT_EPSILON:
            self._advance_to_next_valid_phase(simulation)

    def _advance_to_next_valid_phase(self, simulation):
        """
        Move to the next phase in the fixed sequence.

        If a phase has zero duration, skip it.

        Args:
            simulation: The Simulation object.
        """
        for _ in range(len(self.phase_sequence)):
            self.phase_index = (self.phase_index + 1) % len(self.phase_sequence)

            phase = self.phase_sequence[self.phase_index]
            duration = self.duration_for(phase)

            if duration > 0:
                simulation.signal_state.set_phase(phase, duration)
                return

        # This fallback should normally not be reached because green_time > 0.
        phase = self.phase_sequence[self.phase_index]
        simulation.signal_state.set_phase(phase, self.duration_for(phase))

    def _apply_current_phase(self, simulation):
        """
        Apply the current phase to the simulation signal state.

        Args:
            simulation: The Simulation object.
        """
        phase = self.phase_sequence[self.phase_index]
        duration = self.duration_for(phase)

        simulation.signal_state.set_phase(phase, duration)

    def duration_for(self, phase):
        """
        Return the duration for a given phase.

        Args:
            phase: Signal phase name.

        Returns:
            Duration in seconds.
        """
        if phase in (settings.NS_GREEN, settings.EW_GREEN):
            return self.green_time

        if phase in (settings.NS_YELLOW, settings.EW_YELLOW):
            return self.yellow_time

        if phase == settings.ALL_RED:
            return self.all_red_time

        raise ValueError(f"Unknown fixed-controller phase: {phase}")