# config.py
import math

# --- Simulation ---
SIMULATION_START_TIME_MINS = 8 * 60 # 08:00 AM in minutes

# --- A* Pathfinding ---
NO_FLY_ZONE_PENALTY = 1000000.0 # High cost penalty for entering NFZ

# --- Genetic Algorithm ---
POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.8
# Fitness Weights (adjust as needed based on priorities)
FITNESS_DELIVERY_WEIGHT = 50
FITNESS_ENERGY_WEIGHT = 0.1
FITNESS_PENALTY_WEIGHT = 1000 # For constraint violations (time, battery, NFZ)

# --- Visualization ---
PLOT_SCALE = 1.1 # Scale factor for plot limits

# --- Drone ---
# Default consumption rate if not specified in data file
DEFAULT_CONSUMPTION_RATE_MAH_PER_METER = 0.5