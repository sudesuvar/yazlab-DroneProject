# optimization.py
import random
import copy
from simulation import evaluate_solution
from config import (POPULATION_SIZE, GENERATIONS, MUTATION_RATE, CROSSOVER_RATE,
                    FITNESS_DELIVERY_WEIGHT, FITNESS_ENERGY_WEIGHT, FITNESS_PENALTY_WEIGHT)

# --- Chromosome Representation ---
# A list of lists. Each inner list contains the delivery IDs assigned to a drone.
# Example: [[101, 103], [102], []] for 3 drones.

def calculate_fitness(delivered_count, total_energy, total_violations):
    """Calculates fitness based on the formula provided."""
    # Maximize deliveries, minimize energy and violations
    fitness = (delivered_count * FITNESS_DELIVERY_WEIGHT) \
              - (total_energy * FITNESS_ENERGY_WEIGHT) \
              - (total_violations * FITNESS_PENALTY_WEIGHT)
    return fitness

def create_initial_population(drones, deliveries, population_size):
    """Creates a random initial population of valid(ish) solutions."""
    population = []
    delivery_ids = [d.id for d in deliveries]
    num_drones = len(drones)

    for _ in range(population_size):
        chromosome = [[] for _ in range(num_drones)]
        shuffled_deliveries = random.sample(delivery_ids, len(delivery_ids))

        # Simple assignment: randomly distribute deliveries among drones
        # This doesn't guarantee feasibility (weight/battery), fitness eval handles that.
        for delivery_id in shuffled_deliveries:
            chosen_drone_idx = random.randrange(num_drones)
            chromosome[chosen_drone_idx].append(delivery_id)

        population.append(chromosome)
    return population

def selection(population_with_fitness):
    """Selects parents using tournament selection."""
    tournament_size = 5
    selected = []
    for _ in range(len(population_with_fitness)):
        tournament = random.sample(population_with_fitness, tournament_size)
        # Select the best individual from the tournament
        winner = max(tournament, key=lambda item: item[1]) # item is (chromosome, fitness)
        selected.append(winner[0]) # Add the chromosome to the selected list
    return selected

def crossover(parent1, parent2, num_drones):
    """Performs crossover between two parent chromosomes."""
    # Simple approach: For each drone, randomly pick assignments from parent1 or parent2
    # More sophisticated methods (like cycle crossover for permutations) exist but are complex here.
    if random.random() > CROSSOVER_RATE:
        return parent1[:], parent2[:] # No crossover

    child1 = [[] for _ in range(num_drones)]
    child2 = [[] for _ in range(num_drones)]

    # Gather all unique delivery IDs involved in both parents
    all_involved_deliveries = set()
    for i in range(num_drones):
        all_involved_deliveries.update(parent1[i])
        all_involved_deliveries.update(parent2[i])

    # Randomly assign each delivery to a drone, trying to respect parentage somewhat
    # This is a very basic crossover, might need refinement.
    deliveries_to_assign = list(all_involved_deliveries)
    random.shuffle(deliveries_to_assign)

    for delivery_id in deliveries_to_assign:
         # Assign to child 1
        drone_idx1 = random.randrange(num_drones)
        child1[drone_idx1].append(delivery_id)
         # Assign to child 2
        drone_idx2 = random.randrange(num_drones)
        child2[drone_idx2].append(delivery_id)


    # Alternative (simpler): Single point crossover on the list of lists (less meaningful)
    # crossover_point = random.randint(1, num_drones - 1)
    # child1 = parent1[:crossover_point] + parent2[crossover_point:]
    # child2 = parent2[:crossover_point] + parent1[crossover_point:]

    return child1, child2


def mutate(chromosome, all_delivery_ids, num_drones):
    """Performs mutation on a chromosome."""
    mutated_chromosome = copy.deepcopy(chromosome) # Work on a copy

    if random.random() < MUTATION_RATE:
        # Mutation type 1: Move a random delivery to a different drone (or unassign)
        non_empty_drone_indices = [i for i, route in enumerate(mutated_chromosome) if route]
        if non_empty_drone_indices:
            drone_idx_from = random.choice(non_empty_drone_indices)
            delivery_idx_to_move = random.randrange(len(mutated_chromosome[drone_idx_from]))
            delivery_id = mutated_chromosome[drone_idx_from].pop(delivery_idx_to_move)

            # Choose a new drone (can be the same one, effectively changing order)
            drone_idx_to = random.randrange(num_drones)
            # Insert at a random position in the target drone's route
            insert_pos = random.randint(0, len(mutated_chromosome[drone_idx_to]))
            mutated_chromosome[drone_idx_to].insert(insert_pos, delivery_id)

    if random.random() < MUTATION_RATE:
         # Mutation type 2: Swap two deliveries within the same drone's route
        non_empty_drone_indices = [i for i, route in enumerate(mutated_chromosome) if len(route) >= 2]
        if non_empty_drone_indices:
            drone_idx = random.choice(non_empty_drone_indices)
            idx1, idx2 = random.sample(range(len(mutated_chromosome[drone_idx])), 2)
            # Swap
            mutated_chromosome[drone_idx][idx1], mutated_chromosome[drone_idx][idx2] = \
                mutated_chromosome[drone_idx][idx2], mutated_chromosome[drone_idx][idx1]

    # Add more mutation types if needed (e.g., adding an unassigned delivery)

    return mutated_chromosome


def run_ga(drones, deliveries, no_fly_zones):
    """Runs the Genetic Algorithm."""
    num_drones = len(drones)
    all_deliveries_dict = {d.id: d for d in deliveries}
    all_delivery_ids = list(all_deliveries_dict.keys())

    # 1. Initialization
    population = create_initial_population(drones, deliveries, POPULATION_SIZE)
    best_solution = None
    best_fitness = -float('inf')

    print(f"Starting GA: Pop Size={POPULATION_SIZE}, Generations={GENERATIONS}")

    for generation in range(GENERATIONS):
        # 2. Evaluation
        population_with_fitness = []
        for chromosome in population:
            delivered_count, energy, violations = evaluate_solution(
                chromosome, drones, all_deliveries_dict, no_fly_zones
            )
            fitness = calculate_fitness(delivered_count, energy, violations)
            population_with_fitness.append((chromosome, fitness, delivered_count, energy, violations))

            # Track best solution found so far
            if fitness > best_fitness:
                best_fitness = fitness
                best_solution = chromosome
                print(f"Gen {generation}: New Best! Fitness={fitness:.2f}, Delivered={delivered_count}, Energy={energy:.1f}, Violations={violations}")


        # 3. Selection
        selected_parents = selection(population_with_fitness)

        # 4. Crossover & Mutation
        next_population = []
        for i in range(0, POPULATION_SIZE, 2):
             # Ensure we don't go out of bounds if POPULATION_SIZE is odd
            if i + 1 >= POPULATION_SIZE:
                next_population.append(selected_parents[i]) # Keep one parent
                break

            parent1 = selected_parents[i]
            parent2 = selected_parents[i+1]

            child1, child2 = crossover(parent1, parent2, num_drones)

            # Apply mutation
            child1 = mutate(child1, all_delivery_ids, num_drones)
            child2 = mutate(child2, all_delivery_ids, num_drones)

            next_population.extend([child1, child2])

        population = next_population

        if generation % 10 == 0 and generation > 0:
             # Find current best in population for progress update
            current_best_chrom, current_best_fit, *_ = max(population_with_fitness, key=lambda item: item[1])
            print(f"--- Gen {generation} Complete. Current Best Fitness: {current_best_fit:.2f} ---")


    print("\nGA Finished.")
    # Re-evaluate the best solution found to get final metrics
    final_delivered, final_energy, final_violations = evaluate_solution(
        best_solution, drones, all_deliveries_dict, no_fly_zones
    )
    print(f"Best Solution Found:")
    print(f"  Fitness: {best_fitness:.2f}")
    print(f"  Deliveries Completed: {final_delivered}")
    print(f"  Total Energy (mAh): {final_energy:.1f}")
    print(f"  Constraint Violations: {final_violations}")
    # print(f"  Route Plan: {best_solution}") # Can be very long

    return best_solution, best_fitness