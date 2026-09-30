# core/simulation.py

import settings
from core.vehicle import Vehicle
from core import movement
from core.stats import StatsTracker
from control.signal_state import SignalState


class Simulation:
    """
    Main simulation controller.

    This class keeps the current simulation state and updates it tick by tick.
    In Phase 5, it now includes live statistics tracking.
    """

    def __init__(self, traffic_generator=None, controller=None):
        """
        Create a new simulation.

        Args:
            traffic_generator: Optional TrafficGenerator object.
            controller: Optional signal controller object.
        """
        self.signal_state = SignalState()
        self.stats = StatsTracker()

        self.traffic_generator = traffic_generator
        self.controller = controller

        self.reset()

    def reset(self):
        """
        Reset the simulation state.

        This clears vehicles, counters, statistics, and time.
        The traffic generator and controller remain attached.
        """
        self.tick = 0
        self.time = 0.0

        self.vehicles = []
        self.next_vehicle_id = 1

        self.total_generated = 0
        self.total_exited = 0

        self.paused = False

        self.signal_state.reset()
        self.stats.reset()

        if getattr(self, "controller", None) is not None:
            self.controller.reset(self)

    def set_traffic_generator(self, traffic_generator):
        """
        Attach a traffic generator to the simulation.
        """
        self.traffic_generator = traffic_generator

    def set_controller(self, controller):
        """
        Attach a signal controller to the simulation.
        """
        self.controller = controller

        if self.controller is not None:
            self.controller.reset(self)

    def step(self, dt=None):
        """
        Advance the simulation by one tick.

        Args:
            dt: Time step in seconds. If None, use settings.TICK_DURATION.
        """
        if self.paused:
            return

        if dt is None:
            dt = settings.TICK_DURATION

        # Phase 2: generate traffic.
        if self.traffic_generator is not None:
            self.traffic_generator.generate(self, dt)

        # Phase 4: update signal controller if one is attached.
        if self.controller is not None:
            self.controller.update(self, dt)
        else:
            self.signal_state.update(dt)

        # Phase 3: update vehicle movement.
        movement.update(self, dt)

        # Advance simulation time.
        self.tick += 1
        self.time += dt

        # Phase 5: update live statistics after movement and time update.
        self.stats.update(self, dt)

    def get_statistics(self):
        """
        Return a summary of current simulation statistics.

        Returns:
            Dictionary of statistics.
        """
        return self.stats.get_summary(self)

    def pause(self):
        """
        Pause the simulation.
        """
        self.paused = True

    def resume(self):
        """
        Resume the simulation.
        """
        self.paused = False

    def toggle_pause(self):
        """
        Toggle between paused and running states.
        """
        self.paused = not self.paused

    def add_vehicle(self, direction):
        """
        Add one vehicle to the simulation.

        Args:
            direction: Direction from which the vehicle arrives.

        Returns:
            The newly created Vehicle object.
        """
        vehicle = Vehicle(
            id=self.next_vehicle_id,
            direction=direction,
            arrival_time=self.time
        )

        self.next_vehicle_id += 1
        self.vehicles.append(vehicle)
        self.total_generated += 1

        return vehicle

    def active_vehicle_count(self):
        """
        Return the number of vehicles currently active in the simulation.
        """
        return len(self.vehicles)