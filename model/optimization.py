import random
import numpy as np
from typing import List, Tuple, Dict
from model.data_structures import Drone, DeliveryPoint, NoFlyZone
from shapely.geometry import Polygon, LineString
from config import (
    POPULATION_SIZE, GENERATIONS, MUTATION_RATE,
    CROSSOVER_RATE, ELITE_SIZE, PENALTY_WEIGHTS,
    DEFAULT_CONSUMPTION_RATE_MAH_PER_METER
)
# Genetic Algorithm File
class DeliveryOptimizer:
    def __init__(self, drones: List[Drone], deliveries: List[DeliveryPoint], no_fly_zones: List[NoFlyZone]):
        self.drones = drones
        self.deliveries = deliveries
        self.no_fly_zones = no_fly_zones
        self.num_drones = len(drones)
        self.num_deliveries = len(deliveries)
        self.best_solution = None
        self.best_fitness = float('inf')

    def calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def check_no_fly_zone_violation(self, path: List[Tuple[float, float]], time: float) -> bool:
        """Check if path intersects with any active no-fly zone"""
        for i in range(len(path) - 1):
            for nfz in self.no_fly_zones:
                if nfz.is_active_at_time(time):
                    # Create a line segment from the path
                    line = LineString([path[i], path[i+1]])
                    if nfz.polygon.intersects(line):
                        return True
        return False

    def evaluate_solution(self, solution: Dict[int, List[int]]) -> float:
        """Evaluate a solution using the new fitness formula"""
        total_energy = 0
        total_violations = 0
        successful_deliveries = 0

        for drone_id, delivery_sequence in solution.items():
            if not delivery_sequence:
                continue

            drone = next(d for d in self.drones if d.id == drone_id)
            current_pos = drone.start_pos
            current_time = 0
            current_weight = 0
            current_battery = drone.battery_capacity

            for delivery_id in delivery_sequence:
                delivery = next(d for d in self.deliveries if d.id == delivery_id)
                # Mesafe ve enerji hesaplama
                distance = self.calculate_distance(current_pos, delivery.pos)
                energy = distance * DEFAULT_CONSUMPTION_RATE_MAH_PER_METER
                total_energy += energy
                current_battery -= energy

                # Zaman ve zaman penceresi kontrolü
                travel_time = distance / drone.speed
                current_time += travel_time
                violation = False

                if not delivery.is_valid_time_window(current_time):
                    total_violations += 1
                    violation = True

                # Ağırlık kontrolü
                current_weight += delivery.weight
                if current_weight > drone.max_weight:
                    total_violations += 1
                    violation = True

                # Batarya kontrolü
                if current_battery < 0:
                    total_violations += 1
                    violation = True

                # No-fly zone kontrolü (yalnızca yolun başı ve sonu için)
                # Daha detaylı kontrol istenirse path üzerinden de bakılabilir
                # (Burada basit kontrol yapılıyor)
                # Not: Eğer path kontrolü istenirse, ilgili fonksiyon çağrılabilir

                if not violation:
                    successful_deliveries += 1

                current_pos = delivery.pos

        fitness = (successful_deliveries * 50) - (total_energy * 0.1) - (total_violations * 1000)
        return fitness

    def create_initial_population(self) -> List[Dict[int, List[int]]]:
        """Create initial population of solutions"""
        population = []
        for _ in range(POPULATION_SIZE):
            solution = {}
            # Randomly assign deliveries to drones
            for drone in self.drones:
                num_deliveries = np.random.randint(0, len(self.deliveries) + 1)
                delivery_sequence = np.random.permutation(self.deliveries)[:num_deliveries]
                solution[drone.id] = [d.id for d in delivery_sequence]
            population.append(solution)
        return population

    def crossover(self, parent1: Dict[int, List[int]], parent2: Dict[int, List[int]]) -> Tuple[Dict[int, List[int]], Dict[int, List[int]]]:
        """Perform crossover between two parents"""
        child1 = {}
        child2 = {}
        
        for drone in self.drones:
            if np.random.random() < CROSSOVER_RATE:
                # Swap delivery sequences between parents
                child1[drone.id] = parent2[drone.id].copy()
                child2[drone.id] = parent1[drone.id].copy()
            else:
                # Keep original sequences
                child1[drone.id] = parent1[drone.id].copy()
                child2[drone.id] = parent2[drone.id].copy()
        
        return child1, child2

    def mutate(self, solution: Dict[int, List[int]]) -> Dict[int, List[int]]:
        """Mutate a solution"""
        mutated = solution.copy()
        
        for drone_id in mutated:
            if not mutated[drone_id]:  # If drone has no deliveries
                if np.random.random() < MUTATION_RATE:
                    # Add a random delivery
                    available_deliveries = [d.id for d in self.deliveries if d.id not in [d for seq in mutated.values() for d in seq]]
                    if available_deliveries:
                        mutated[drone_id] = [np.random.choice(available_deliveries)]
            elif len(mutated[drone_id]) == 1:  # If drone has only one delivery
                if np.random.random() < MUTATION_RATE:
                    if np.random.random() < 0.5:
                        # Remove the delivery
                        mutated[drone_id] = []
                    else:
                        # Add another delivery
                        available_deliveries = [d.id for d in self.deliveries if d.id not in [d for seq in mutated.values() for d in seq]]
                        if available_deliveries:
                            mutated[drone_id].append(np.random.choice(available_deliveries))
            else:  # If drone has multiple deliveries
                if np.random.random() < MUTATION_RATE:
                    if np.random.random() < 0.5:
                        # Swap two deliveries
                        idx1, idx2 = np.random.choice(len(mutated[drone_id]), 2, replace=False)
                        mutated[drone_id][idx1], mutated[drone_id][idx2] = mutated[drone_id][idx2], mutated[drone_id][idx1]
                    else:
                        # Remove or add a delivery
                        if np.random.random() < 0.5:
                            # Remove a random delivery
                            idx = np.random.randint(len(mutated[drone_id]))
                            mutated[drone_id].pop(idx)
                        else:
                            # Add a random delivery
                            available_deliveries = [d.id for d in self.deliveries if d.id not in [d for seq in mutated.values() for d in seq]]
                            if available_deliveries:
                                mutated[drone_id].append(np.random.choice(available_deliveries))
        
        return mutated

    def optimize(self) -> Tuple[Dict[int, List[int]], List[float]]:
        """Run the genetic algorithm optimization"""
        # Create initial population
        population = self.create_initial_population()
        best_solution = None
        best_fitness = float('inf')
        fitness_history = []

        # Evolution loop
        for generation in range(GENERATIONS):
            # Evaluate population
            fitness_scores = [self.evaluate_solution(solution) for solution in population]
            
            # Update best solution
            min_fitness_idx = np.argmin(fitness_scores)
            if fitness_scores[min_fitness_idx] < best_fitness:
                best_fitness = fitness_scores[min_fitness_idx]
                best_solution = population[min_fitness_idx].copy()
            
            fitness_history.append(best_fitness)
            
            # Create new population
            new_population = []
            
            # Elitism: Keep best solution
            new_population.append(best_solution)
            
            # Create rest of new population
            while len(new_population) < POPULATION_SIZE:
                # Tournament selection
                tournament_size = 3
                tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
                tournament_fitness = [fitness_scores[i] for i in tournament_indices]
                parent1_idx = tournament_indices[np.argmin(tournament_fitness)]
                
                tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
                tournament_fitness = [fitness_scores[i] for i in tournament_indices]
                parent2_idx = tournament_indices[np.argmin(tournament_fitness)]
                
                # Crossover
                child1, child2 = self.crossover(population[parent1_idx], population[parent2_idx])
                
                # Mutation
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.extend([child1, child2])
            
            # Update population
            population = new_population[:POPULATION_SIZE]
            
            # Print progress
            if (generation + 1) % 10 == 0:
                print(f"Generation {generation + 1}/{GENERATIONS}, Best Fitness: {best_fitness:.2f}")

        return best_solution, fitness_history 