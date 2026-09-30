import settings


class StatsTracker:
    """
    Tracks simulation statistics.

    This class stores cumulative statistics and also keeps the most recent
    live values for display or analysis.
    """

    def __init__(self):
        """
        Create a new statistics tracker.
        """
        self.reset()

    def reset(self):
        """
        Reset all statistics to zero.
        """
        self.total_exited_recorded = 0
        self.total_wait_time_exited = 0.0
        self.max_wait_time_observed = 0.0

        self.queue_length_samples = 0
        self.total_queue_length_sum = 0.0
        self.max_queue_length = 0

        self.passed_by_direction = {
            direction: 0
            for direction in settings.DIRECTIONS
        }

        self.current_waiting_count = 0
        self.current_total_queue_length = 0
        self.current_max_active_wait = 0.0

        self.current_queue_by_direction = {
            direction: 0
            for direction in settings.DIRECTIONS
        }

    def record_exited_vehicle(self, vehicle):
        """
        Record statistics for a vehicle that has exited the simulation.

        Args:
            vehicle: The Vehicle object that exited.
        """
        self.total_exited_recorded += 1
        self.total_wait_time_exited += vehicle.wait_time

        if vehicle.wait_time > self.max_wait_time_observed:
            self.max_wait_time_observed = vehicle.wait_time

        if vehicle.direction in self.passed_by_direction:
            self.passed_by_direction[vehicle.direction] += 1
        else:
            self.passed_by_direction[vehicle.direction] = 1

    def update(self, simulation, dt=None):
        """
        Update live statistics using the current simulation state.

        Args:
            simulation: The Simulation object.
            dt: Time step in seconds. Currently unused but kept for future use.
        """
        stop_limit = settings.STOP_LINE_DISTANCE + settings.MOVEMENT_EPSILON

        total_queue_length = 0
        waiting_count = 0
        max_active_wait = 0.0

        queue_by_direction = {
            direction: 0
            for direction in settings.DIRECTIONS
        }

        for vehicle in simulation.vehicles:
            # Track maximum active waiting time.
            if vehicle.wait_time > max_active_wait:
                max_active_wait = vehicle.wait_time

            # Queue length counts vehicles that have not entered the junction.
            if vehicle.state == "approaching":
                total_queue_length += 1

                if vehicle.direction in queue_by_direction:
                    queue_by_direction[vehicle.direction] += 1
                else:
                    queue_by_direction[vehicle.direction] = 1

                # Currently waiting means stopped before/at the stop line.
                if (
                    vehicle.speed <= settings.MOVEMENT_EPSILON
                    and vehicle.position <= stop_limit
                ):
                    waiting_count += 1

        self.current_total_queue_length = total_queue_length
        self.current_waiting_count = waiting_count
        self.current_queue_by_direction = queue_by_direction
        self.current_max_active_wait = max_active_wait

        if max_active_wait > self.max_wait_time_observed:
            self.max_wait_time_observed = max_active_wait

        self.queue_length_samples += 1
        self.total_queue_length_sum += total_queue_length

        if total_queue_length > self.max_queue_length:
            self.max_queue_length = total_queue_length

    def average_wait_time_finished(self):
        """
        Return the average waiting time of vehicles that have exited.

        Returns:
            Average waiting time in seconds.
        """
        if self.total_exited_recorded == 0:
            return 0.0

        return self.total_wait_time_exited / self.total_exited_recorded

    def average_queue_length(self):
        """
        Return the average total queue length over all sampled ticks.

        Returns:
            Average queue length.
        """
        if self.queue_length_samples == 0:
            return 0.0

        return self.total_queue_length_sum / self.queue_length_samples

    def get_summary(self, simulation):
        """
        Return a dictionary summarizing the current statistics.

        Args:
            simulation: The Simulation object.

        Returns:
            Dictionary of statistics.
        """
        vehicles_remaining_by_direction = {
            direction: 0
            for direction in settings.DIRECTIONS
        }

        for vehicle in simulation.vehicles:
            if vehicle.direction in vehicles_remaining_by_direction:
                vehicles_remaining_by_direction[vehicle.direction] += 1
            else:
                vehicles_remaining_by_direction[vehicle.direction] = 1

        return {
            "simulation_duration": simulation.time,
            "tick": simulation.tick,

            "total_generated": simulation.total_generated,
            "total_passed": simulation.total_exited,
            "total_exited_recorded": self.total_exited_recorded,
            "active_vehicles": simulation.active_vehicle_count(),

            "vehicles_currently_waiting": self.current_waiting_count,
            "current_total_queue_length": self.current_total_queue_length,

            "average_wait_time_finished": self.average_wait_time_finished(),
            "max_wait_time_observed": self.max_wait_time_observed,
            "current_max_active_wait": self.current_max_active_wait,

            "average_queue_length": self.average_queue_length(),
            "max_queue_length": self.max_queue_length,
            "queue_length_samples": self.queue_length_samples,

            "current_queue_by_direction": self.current_queue_by_direction.copy(),
            "passed_by_direction": self.passed_by_direction.copy(),
            "vehicles_remaining_by_direction": vehicles_remaining_by_direction,
        }