import settings


EPSILON = settings.MOVEMENT_EPSILON


def stop_line_position():
    """
    Return the position of the stop line.
    """
    return settings.STOP_LINE_DISTANCE


def exit_position():
    """
    Return the position where a vehicle has fully crossed the junction.
    """
    return settings.STOP_LINE_DISTANCE + settings.JUNCTION_EXIT_DISTANCE


def update(simulation, dt):
    """
    Update all vehicle movement for one simulation tick.

    Args:
        simulation: The Simulation object.
        dt: Time step in seconds.
    """
    if dt <= 0:
        return

    for direction in settings.DIRECTIONS:
        # Get all active vehicles in this direction.
        lane = [
            vehicle
            for vehicle in simulation.vehicles
            if vehicle.direction == direction and vehicle.state != "exited"
        ]

        # Sort vehicles from closest-to-junction to farthest-from-junction.
        # The first vehicle in this list is the leader.
        lane.sort(key=lambda vehicle: vehicle.position, reverse=True)

        for index, vehicle in enumerate(lane):
            leader = lane[index - 1] if index > 0 else None
            update_single_vehicle(simulation, vehicle, leader, dt)

    remove_exited(simulation)


def update_single_vehicle(simulation, vehicle, leader, dt):
    """
    Update one vehicle for one simulation tick.

    Args:
        simulation: The Simulation object.
        vehicle: The Vehicle object to update.
        leader: The vehicle directly ahead in the same lane, or None.
        dt: Time step in seconds.
    """
    stop_line = stop_line_position()
    exit_point = exit_position()

    # If the vehicle has clearly passed the stop line, it is crossing.
    if vehicle.state == "approaching" and vehicle.position > stop_line + EPSILON:
        vehicle.state = "crossing"

    # Determine the maximum position this vehicle is allowed to reach.
    if vehicle.state == "crossing":
        limit = exit_point

    elif (
        not simulation.signal_state.can_enter_junction(vehicle.direction)
        and vehicle.position <= stop_line + EPSILON
    ):
        # The signal is not green and the vehicle has not entered the junction.
        limit = stop_line

    else:
        # The vehicle is allowed to proceed through the junction.
        limit = exit_point

    # Prevent overlap with the vehicle ahead.
    if leader is not None:
        leader_limit = leader.position - leader.length - settings.VEHICLE_GAP

        if leader_limit < limit:
            limit = leader_limit

    # Calculate how far the vehicle can move safely this tick.
    distance_available = limit - vehicle.position

    if distance_available <= EPSILON:
        vehicle.speed = 0.0
        move_distance = 0.0
    else:
        vehicle.speed = min(settings.MAX_SPEED, distance_available / dt)
        move_distance = vehicle.speed * dt

        if move_distance > distance_available:
            move_distance = distance_available

    vehicle.position += move_distance

    if vehicle.position > limit:
        vehicle.position = limit

    # If the vehicle has reached its current safe limit, stop it.
    if vehicle.position >= limit - EPSILON:
        vehicle.speed = 0.0

    # Update vehicle state.
    if vehicle.position >= exit_point - EPSILON:
        vehicle.state = "exited"
        vehicle.speed = 0.0

    elif vehicle.state == "approaching" and vehicle.position > stop_line + EPSILON:
        vehicle.state = "crossing"

    # Accumulate waiting time if the vehicle is stopped before the junction.
    if (
        vehicle.state == "approaching"
        and vehicle.speed <= EPSILON
        and vehicle.position <= stop_line + EPSILON
    ):
        vehicle.wait_time += dt


def remove_exited(simulation):
    """
    Remove exited vehicles from the simulation and update counters.

    Args:
        simulation: The Simulation object.
    """
    remaining_vehicles = []

    for vehicle in simulation.vehicles:
        if vehicle.state == "exited":
            # Record statistics before removing the vehicle.
            stats = getattr(simulation, "stats", None)

            if stats is not None:
                stats.record_exited_vehicle(vehicle)

            simulation.total_exited += 1
        else:
            remaining_vehicles.append(vehicle)

    simulation.vehicles = remaining_vehicles