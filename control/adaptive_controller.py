import settings


class AdaptiveController:
    """
    Rule-based adaptive traffic signal controller.

    This controller observes queue lengths and waiting times to dynamically
    allocate green time to the busiest axis, while preventing starvation.
    """

    def __init__(
        self,
        min_green=None,
        max_green=None,
        yellow_time=None,
        all_red_time=None,
        time_per_vehicle=None,
    ):
        """
        Create an adaptive controller.
        """
        self.min_green = min_green if min_green is not None else settings.MIN_GREEN_TIME
        self.max_green = max_green if max_green is not None else settings.MAX_GREEN_TIME
        self.yellow_time = yellow_time if yellow_time is not None else settings.YELLOW_TIME
        self.all_red_time = all_red_time if all_red_time is not None else settings.ALL_RED_TIME
        self.time_per_vehicle = (
            time_per_vehicle
            if time_per_vehicle is not None
            else settings.SECONDS_ADDED_PER_WAITING_VEHICLE
        )

        # Fairness parameters to prevent starvation
        self.fairness_wait_threshold = 15.0  # seconds
        self.fairness_bonus = 5.0            # equivalent to 5 extra vehicles in demand

        self.last_green_axis = "EW"  # Tracks which axis just finished

        self._validate_times()

    def _validate_times(self):
        """Check that timing values are valid."""
        if self.min_green <= 0:
            raise ValueError("Minimum green time must be greater than zero.")
        if self.max_green < self.min_green:
            raise ValueError("Maximum green time cannot be less than minimum green time.")
        if self.yellow_time < 0:
            raise ValueError("Yellow time cannot be negative.")
        if self.all_red_time < 0:
            raise ValueError("All-red time cannot be negative.")
        if self.time_per_vehicle < 0:
            raise ValueError("Time per vehicle cannot be negative.")

    def reset(self, simulation=None):
        """
        Reset the controller to its initial state.
        """
        self.last_green_axis = "EW"
        
        if simulation is not None:
            # Start with NS_GREEN for the minimum green time
            simulation.signal_state.set_phase(settings.NS_GREEN, self.min_green)
            self.last_green_axis = "NS"

    def update(self, simulation, dt):
        """
        Update the adaptive controller for one simulation tick.
        """
        if dt <= 0:
            return

        signal = simulation.signal_state
        signal.time_remaining -= dt

        if signal.time_remaining <= settings.MOVEMENT_EPSILON:
            self._advance_phase(simulation)

    def _advance_phase(self, simulation):
        """
        Move to the next phase in the signal cycle.
        """
        signal = simulation.signal_state
        current_phase = signal.phase

        if current_phase == settings.NS_GREEN:
            signal.set_phase(settings.NS_YELLOW, self.yellow_time)
            
        elif current_phase == settings.NS_YELLOW:
            signal.set_phase(settings.ALL_RED, self.all_red_time)
            
        elif current_phase == settings.EW_GREEN:
            signal.set_phase(settings.EW_YELLOW, self.yellow_time)
            
        elif current_phase == settings.EW_YELLOW:
            signal.set_phase(settings.ALL_RED, self.all_red_time)
            
        elif current_phase == settings.ALL_RED:
            # Time to make the adaptive decision
            next_phase, green_time = self._decide_next_green(simulation)
            signal.set_phase(next_phase, green_time)
            
            if next_phase == settings.NS_GREEN:
                self.last_green_axis = "NS"
            else:
                self.last_green_axis = "EW"

    def _decide_next_green(self, simulation):
        """
        Calculate demand and decide the next green phase and duration.

        Returns:
            Tuple of (next_phase, green_time).
        """
        stats = simulation.stats

        # 1. Base demand from queue lengths
        ns_demand = (
            stats.current_queue_by_direction.get("N", 0) +
            stats.current_queue_by_direction.get("S", 0)
        )
        ew_demand = (
            stats.current_queue_by_direction.get("E", 0) +
            stats.current_queue_by_direction.get("W", 0)
        )

        # 2. Fairness check: prevent starvation
        ns_max_wait = 0.0
        ew_max_wait = 0.0

        for vehicle in simulation.vehicles:
            if vehicle.state == "approaching":
                if vehicle.direction in ("N", "S"):
                    if vehicle.wait_time > ns_max_wait:
                        ns_max_wait = vehicle.wait_time
                elif vehicle.direction in ("E", "W"):
                    if vehicle.wait_time > ew_max_wait:
                        ew_max_wait = vehicle.wait_time

        if ns_max_wait > self.fairness_wait_threshold:
            ns_demand += self.fairness_bonus
            
        if ew_max_wait > self.fairness_wait_threshold:
            ew_demand += self.fairness_bonus

        # 3. Decision: pick the axis with higher demand
        if ns_demand >= ew_demand:
            next_phase = settings.NS_GREEN
            demand = ns_demand
        else:
            next_phase = settings.EW_GREEN
            demand = ew_demand

        # 4. Calculate dynamic green time
        green_time = self.min_green + (demand * self.time_per_vehicle)

        # Clamp to limits
        if green_time > self.max_green:
            green_time = self.max_green

        return next_phase, green_time