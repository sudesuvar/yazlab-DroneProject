import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from typing import List, Dict, Tuple
from model.data_structures import Drone, DeliveryPoint, NoFlyZone
from model.pathfinding import AStarPathfinder
import numpy as np
import os

class DeliveryVisualizer:
    def __init__(self, drones: List[Drone], deliveries: List[DeliveryPoint], no_fly_zones: List[NoFlyZone]):
        self.drones = drones
        self.deliveries = deliveries
        self.no_fly_zones = no_fly_zones
        self.colors = plt.cm.rainbow(np.linspace(0, 1, len(drones)))
        self.pathfinder = AStarPathfinder(no_fly_zones, grid_size=1.0)  # Smaller grid size for more precise paths
        
        # Create output directory if it doesn't exist
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def calculate_path_length(self, path: np.ndarray) -> float:
        """Calculate the total length of a path"""
        if path is None or path.size == 0 or path.shape[0] < 2:
            return 0.0
        # Calculate distances between consecutive points
        diffs = np.diff(path, axis=0)
        distances = np.sqrt(np.sum(diffs**2, axis=1))
        return np.sum(distances)

    def plot_drone_sequential_path(self, drone: Drone, color: np.ndarray):
        """Plot sequential path from drone to all delivery points"""
        plt.figure(figsize=(12, 8))
        
        # Plot no-fly zones
        for nfz in self.no_fly_zones:
            if nfz.polygon:
                polygon = MplPolygon(nfz.coordinates, alpha=0.3, color='red')
                plt.gca().add_patch(polygon)
                center = np.mean(nfz.coordinates, axis=0)
                plt.text(center[0], center[1], f"NFZ {nfz.id}\n{nfz.active_start_str}-{nfz.active_end_str}",
                        ha='center', va='center')

        # Plot delivery points
        for delivery in self.deliveries:
            plt.scatter(delivery.pos[0], delivery.pos[1], c='blue', marker='o', s=100)
            plt.text(delivery.pos[0], delivery.pos[1] + 2, f"D{delivery.id}\n{delivery.time_window_start_str}-{delivery.time_window_end_str}",
                    ha='center', va='bottom')

        # Plot drone start position
        plt.scatter(drone.start_pos[0], drone.start_pos[1], c='green', marker='^', s=300, edgecolor='black', linewidth=2)
        plt.text(drone.start_pos[0], drone.start_pos[1] - 3, f"Drone {drone.id}",
                ha='center', va='top', fontsize=12, fontweight='bold')

        print(f"\nFinding sequential path for Drone {drone.id}:")
        
        # Get delivery points in order
        delivery_points = [delivery.pos for delivery in self.deliveries]
        
        # Find sequential path
        path = self.pathfinder.find_sequential_path(drone.start_pos, delivery_points)
        
        if path:
            path = np.array(path)
            # Plot the complete path
            plt.plot(path[:, 0], path[:, 1], c=color, linestyle='-', linewidth=2, alpha=0.8)
            # Plot path points
            plt.scatter(path[:, 0], path[:, 1], c=[color], s=20, alpha=0.6)
            print(f"Found sequential path with {len(path)} points")
        else:
            print("No valid sequential path found")

        plt.title(f"Drone {drone.id} Sequential Path")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.grid(True)
        plt.axis('equal')
        
        # Save the plot for this drone
        output_path = os.path.join(self.output_dir, f"drone_{drone.id}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\nSaved sequential path for Drone {drone.id} to: {output_path}")

    def plot_scenario(self, solution: Dict[int, List[int]] = None):
        """Plot the delivery scenario with sequential paths for each drone"""
        # Create separate plots for each drone
        for i, drone in enumerate(self.drones):
            self.plot_drone_sequential_path(drone, self.colors[i])

        # Create a combined plot showing all drones and delivery points
        plt.figure(figsize=(12, 8))
        
        # Plot no-fly zones
        for nfz in self.no_fly_zones:
            if nfz.polygon:
                polygon = MplPolygon(nfz.coordinates, alpha=0.3, color='red')
                plt.gca().add_patch(polygon)
                center = np.mean(nfz.coordinates, axis=0)
                plt.text(center[0], center[1], f"NFZ {nfz.id}\n{nfz.active_start_str}-{nfz.active_end_str}",
                        ha='center', va='center')

        # Plot delivery points
        for delivery in self.deliveries:
            plt.scatter(delivery.pos[0], delivery.pos[1], c='blue', marker='o', s=100)
            plt.text(delivery.pos[0], delivery.pos[1] + 2, f"D{delivery.id}\n{delivery.time_window_start_str}-{delivery.time_window_end_str}",
                    ha='center', va='bottom')

        # Plot drone start positions
        for i, drone in enumerate(self.drones):
            plt.scatter(drone.start_pos[0], drone.start_pos[1], c='green', marker='^', s=300, edgecolor='black', linewidth=2)
            plt.text(drone.start_pos[0], drone.start_pos[1] - 3, f"Drone {drone.id}",
                    ha='center', va='top', fontsize=12, fontweight='bold')

        plt.title("Drone Delivery Scenario Overview")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.grid(True)
        plt.axis('equal')
        
        # Save the overview plot
        output_path = os.path.join(self.output_dir, "delivery_scenario_overview.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\nSaved scenario overview to: {output_path}")

    def plot_fitness_history(self, fitness_history: List[float]):
        """Plot the fitness history of the optimization process"""
        plt.figure(figsize=(10, 6))
        plt.plot(fitness_history)
        plt.title("Optimization Progress")
        plt.xlabel("Generation")
        plt.ylabel("Best Fitness Score")
        plt.grid(True)
        
        # Save the plot instead of showing it
        output_path = os.path.join(self.output_dir, "fitness_history.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\nSaved fitness history to: {output_path}") 