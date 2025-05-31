# config.py
import math

# --- Simulation ---
SIMULATION_START_TIME_MINS = 8 * 60 # 08:00 AM in minutes

# --- A* Pathfinding ---
NO_FLY_ZONE_PENALTY = 1000.0 # Reduced penalty for entering NFZ

# --- Genetic Algorithm ---
POPULATION_SIZE = 100
GENERATIONS = 50
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.8
ELITE_SIZE = 2
# Fitness Weights (adjust as needed based on priorities)
FITNESS_DELIVERY_WEIGHT = 50
FITNESS_ENERGY_WEIGHT = 0.1
FITNESS_PENALTY_WEIGHT = 1000 # For constraint violations (time, battery, NFZ)

# --- Visualization ---
PLOT_SCALE = 1.1 # Scale factor for plot limits

# --- Drone ---
# Default consumption rate if not specified in data file
DEFAULT_CONSUMPTION_RATE_MAH_PER_METER = 0.1

# Penalty weights for fitness calculation
PENALTY_WEIGHTS = {
    'distance': 0.1,     # Reduced weight for total distance traveled
    'time': 0.1,        # Reduced weight for total time taken
    'priority': 1.0,    # Weight for delivery priority
    'no_fly_zone': 10.0, # Weight for no-fly zone violations
    'battery': 1.0,     # Reduced weight for battery violations
    'weight': 1.0,      # Reduced weight for weight limit violations
    'time_window': 1.0  # Reduced weight for time window violations
}