# simulation.py
import copy
from utils import calculate_distance, minutes_to_time_str
from pathfinding import find_path_a_star
from config import SIMULATION_START_TIME_MINS, FITNESS_PENALTY_WEIGHT

def simulate_drone_route(drone, delivery_sequence, all_deliveries_dict, no_fly_zones):
    """
    Simulates a single drone's route, checking constraints.
    Returns: (completed_delivery_ids, total_distance, total_energy, violations)
    Violations is a count of issues (battery, time window, NFZ).
    """
    drone.reset() # Reset drone state for this simulation run
    drone.current_time = SIMULATION_START_TIME_MINS
    current_pos = drone.start_pos
    current_battery = drone.battery_capacity
    completed_ids = []
    total_distance = 0.0
    total_energy = 0.0
    violations = 0

    for delivery_id in delivery_sequence:
        delivery = all_deliveries_dict.get(delivery_id)
        if not delivery: continue # Should not happen if sequence is valid

        # 1. Check Weight Constraint (should ideally be checked before assignment)
        if delivery.weight > drone.max_weight:
            # This indicates a flaw in chromosome generation/validation
            print(f"Error: Drone {drone.id} cannot carry delivery {delivery.id} (weight constraint)")
            violations += 10 # Heavy penalty for fundamental error
            continue # Skip this delivery

        # 2. Plan path to delivery location
        path, dist, energy, time_sec, violates_nfz = find_path_a_star(
            current_pos, delivery.pos, drone, no_fly_zones, drone.current_time
        )

        # 3. Check Constraints for this segment
        # NFZ Violation
        if violates_nfz:
            violations += 1
            # Option: Stop simulation for this drone, or just penalize and continue?
            # Let's penalize and assume the drone *would not* fly this if it were real.
            # The fitness penalty should discourage this route.

        # Battery Violation
        if current_battery < energy:
            violations += 1
            # Cannot complete this leg, stop this drone's route here
            break

        # Time Calculation
        time_minutes = time_sec / 60.0
        arrival_time_minutes = drone.current_time + time_minutes

        # Time Window Violation
        if not delivery.is_time_window_valid(arrival_time_minutes):
            violations += 1
            # Penalize, but maybe the drone still attempts it? Or skip?
            # Let's assume it's a violation but the delivery might still happen (e.g., late)
            # The fitness penalty handles this.

        # 4. If constraints allow (or are just penalized), execute the move
        current_battery -= energy
        total_energy += energy
        total_distance += dist
        drone.current_time = arrival_time_minutes
        current_pos = delivery.pos # Drone is now at the delivery location

        completed_ids.append(delivery.id)
        # print(f" Drone {drone.id}: Delivered {delivery.id} at {minutes_to_time_str(drone.current_time)} (Bat: {current_battery:.0f}mAh)")


        # TODO: Add return trip? Or assume drone stays out until next delivery?
        # For now, assume it stays at the last delivery point for the next leg.
        # A more realistic model might require returning to base or specific depots.

    return completed_ids, total_distance, total_energy, violations


def evaluate_solution(solution, drones, all_deliveries_dict, no_fly_zones):
    """
    Evaluates a full solution (assignments for all drones).
    'solution' is a list of lists, e.g., [[deliv_id1, deliv_id2], [deliv_id3], []]
    Returns: (total_delivered_count, total_energy_consumed, total_violations)
    """
    total_delivered = 0
    total_energy = 0
    total_violations = 0
    all_simulated_drone_routes = [] # Store results for potential analysis/visualization

    # Create deep copies of drones to avoid modifying originals during simulation
    sim_drones = [copy.deepcopy(d) for d in drones]

    if len(solution) != len(sim_drones):
         print(f"Error: Solution length ({len(solution)}) doesn't match drone count ({len(sim_drones)}).")
         return 0, float('inf'), float('inf') # Invalid solution

    for i, drone_route_ids in enumerate(solution):
        drone = sim_drones[i]
        completed_ids, route_dist, route_energy, route_violations = simulate_drone_route(
            drone, drone_route_ids, all_deliveries_dict, no_fly_zones
        )
        total_delivered += len(completed_ids)
        total_energy += route_energy
        total_violations += route_violations
        # Store drone's simulated path if needed later
        # all_simulated_drone_routes.append({'drone_id': drone.id, 'completed': completed_ids, 'distance': route_dist, 'energy': route_energy, 'violations': route_violations})


    return total_delivered, total_energy, total_violations