import numpy as np
from typing import List, Tuple, Dict
from model.data_structures import Drone, DeliveryPoint, NoFlyZone
from shapely.geometry import Polygon, LineString
from config import (
    POPULATION_SIZE, GENERATIONS, MUTATION_RATE,
    CROSSOVER_RATE, ELITE_SIZE, PENALTY_WEIGHTS,
    DEFAULT_CONSUMPTION_RATE_MAH_PER_METER
)

class DeliveryOptimizerLegacy:
    def __init__(self, drones: List[Drone], deliveries: List[DeliveryPoint], no_fly_zones: List[NoFlyZone]):
        self.drones = drones
        self.deliveries = deliveries
        self.no_fly_zones = no_fly_zones
        self.num_drones = len(drones)
        self.num_deliveries = len(deliveries)
        self.best_solution = None
        self.best_fitness = float('inf')

    def calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def evaluate_solution(self, solution: Dict[int, List[int]]) -> float:
        total_distance = 0
        total_time = 0
        total_priority = 0
        no_fly_violations = 0
        battery_violations = 0
        weight_violations = 0
        time_window_violations = 0

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
                distance = self.calculate_distance(current_pos, delivery.pos)
                battery_consumption = distance * DEFAULT_CONSUMPTION_RATE_MAH_PER_METER
                current_battery -= battery_consumption
                travel_time = distance / drone.speed
                current_time += travel_time
                if not delivery.is_valid_time_window(current_time):
                    time_window_violations += 1
                current_weight += delivery.weight
                if current_weight > drone.max_weight:
                    weight_violations += 1
                if current_battery < 0:
                    battery_violations += 1
                total_distance += distance
                total_time += travel_time
                total_priority += delivery.priority
                current_pos = delivery.pos

        score = (
            total_distance * PENALTY_WEIGHTS['distance'] +
            total_time * PENALTY_WEIGHTS['time'] +
            (self.num_deliveries - total_priority) * PENALTY_WEIGHTS['priority'] +
            no_fly_violations * PENALTY_WEIGHTS['no_fly_zone'] +
            battery_violations * PENALTY_WEIGHTS['battery'] +
            weight_violations * PENALTY_WEIGHTS['weight'] +
            time_window_violations * PENALTY_WEIGHTS['time_window']
        )
        return score 