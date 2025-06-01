import numpy as np
from typing import List, Tuple, Optional
from model.data_structures import NoFlyZone
from shapely.geometry import Point
import math

# A* Pathfinding File
class Node:
    def __init__(self, pos: Tuple[float, float], g_cost: float = 0, h_cost: float = 0, parent=None):
        self.pos = pos
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = parent

    def __lt__(self, other):
        return self.f_cost < other.f_cost

class AStarPathfinder:
    def __init__(self, no_fly_zones: List[NoFlyZone], grid_size: float = 1.0):
        self.no_fly_zones = no_fly_zones
        self.grid_size = grid_size

    def is_point_in_no_fly_zone(self, point: Tuple[float, float]) -> bool:
        """Check if a point is inside any no-fly zone"""
        point_obj = Point(point)
        for nfz in self.no_fly_zones:
            if nfz.polygon and nfz.polygon.contains(point_obj):
                return True
        return False

    def is_line_intersects_no_fly_zone(self, start: Tuple[float, float], end: Tuple[float, float], time: float) -> bool:
        """Check if a line segment intersects with any no-fly zone that is active at the given time"""
        line = np.array([start, end])
        for nfz in self.no_fly_zones:
            if not nfz.polygon:
                continue
            if not nfz.is_active_at_time(time):
                continue
            edges = np.array(nfz.coordinates)
            edges = np.vstack((edges, edges[0]))
            for i in range(len(edges) - 1):
                edge = np.array([edges[i], edges[i + 1]])
                if self.line_segments_intersect(line, edge):
                    return True
            if nfz.polygon.contains(Point(start)) or nfz.polygon.contains(Point(end)):
                return True
        return False

    def line_segments_intersect(self, line1: np.ndarray, line2: np.ndarray) -> bool:
        """Check if two line segments intersect"""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        A, B = line1
        C, D = line2
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    def get_neighbors(self, node: Node, goal: Tuple[float, float], current_time: float, speed: float) -> List[Node]:
        x, y = node.pos
        neighbors = []
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        for dx, dy in directions:
            new_x = x + dx * self.grid_size
            new_y = y + dy * self.grid_size
            new_pos = (new_x, new_y)
            # Segment travel time
            segment_distance = math.sqrt(dx*dx + dy*dy) * self.grid_size
            segment_time = segment_distance / speed if speed > 0 else 0
            neighbor_time = current_time + segment_time
            if self.is_point_in_no_fly_zone(new_pos):
                continue
            if self.is_line_intersects_no_fly_zone(node.pos, new_pos, neighbor_time):
                continue
            g_cost = node.g_cost + segment_distance
            h_cost = math.sqrt((new_x - goal[0])**2 + (new_y - goal[1])**2)
            neighbors.append(Node(new_pos, g_cost, h_cost, node))
        return neighbors

    def find_path(self, start: Tuple[float, float], goal: Tuple[float, float], current_time: float, speed: float = 10.0, battery: float = None, consumption_rate: float = 0.1) -> Optional[List[Tuple[float, float]]]:
        # print(f"Finding path from {start} to {goal} at time {current_time}")
        # Eğer başlangıç noktası aktif bir NFZ içindeyse, NFZ'nin bitiş saatine kadar bekle
        for nfz in self.no_fly_zones:
            if nfz.polygon and nfz.polygon.contains(Point(start)) and nfz.is_active_at_time(current_time):
                # Bekleme süresi: aktifliğin bitişine kadar
                wait_time = nfz.active_end - current_time
                if wait_time > 0:
                    print(f"Drone is in active NFZ, waiting {wait_time} minutes...")
                    current_time = nfz.active_end
        open_set = [Node(start, 0, math.sqrt((start[0] - goal[0])**2 + (start[1] - goal[1])**2))]
        closed_set = set()
        max_iterations = 2000
        iterations = 0
        while open_set and iterations < max_iterations:
            iterations += 1
            current = min(open_set)
            open_set.remove(current)
            closed_set.add(current.pos)
            if math.sqrt((current.pos[0] - goal[0])**2 + (current.pos[1] - goal[1])**2) < self.grid_size:
                path = []
                while current:
                    path.append(current.pos)
                    current = current.parent
                path.reverse()
                # print(f"Found path with {len(path)} points")
                return path
            for neighbor in self.get_neighbors(current, goal, current_time, speed):
                if neighbor.pos in closed_set:
                    continue
                if any(n.pos == neighbor.pos for n in open_set):
                    continue
                # Segment travel time ve enerji
                segment_distance = math.sqrt((neighbor.pos[0] - current.pos[0])**2 + (neighbor.pos[1] - current.pos[1])**2)
                segment_time = segment_distance / speed if speed > 0 else 0
                # Batarya kontrolü
                if battery is not None and consumption_rate is not None:
                    energy_needed = segment_distance * consumption_rate
                    if battery - energy_needed < 0:
                        continue  # Batarya yetmiyorsa bu neighbor'a gitme
                # NFZ aktifliği segment boyunca değişiyorsa bekle
                nfz_waited = False
                for nfz in self.no_fly_zones:
                    if nfz.polygon and nfz.polygon.contains(Point(current.pos)):
                        if nfz.is_active_at_time(current_time):
                            wait_time = nfz.active_end - current_time
                            if wait_time > 0:
                                current_time = nfz.active_end
                                nfz_waited = True
                    # Segmentin başında aktif, sonunda aktif değilse
                    if nfz.polygon and self.is_line_intersects_no_fly_zone(current.pos, neighbor.pos, current_time):
                        if nfz.is_active_at_time(current_time):
                            # Segmentin başında aktif, sonunda aktif değilse bekle
                            if not nfz.is_active_at_time(current_time + segment_time):
                                wait_time = nfz.active_end - current_time
                                if wait_time > 0:
                                    current_time = nfz.active_end
                                    nfz_waited = True
                # Eğer beklediysek, neighbor'ın zamanı güncellenmeli
                if nfz_waited:
                    neighbor_time = current_time + segment_time
                else:
                    neighbor_time = current_time + segment_time
                open_set.append(Node(neighbor.pos, neighbor.g_cost, neighbor.h_cost, current))
        print(f"No path found after {iterations} iterations")
        return None

    def find_sequential_path(self, start: Tuple[float, float], delivery_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Find a path that visits all delivery points in sequence"""
        if not delivery_points:
            return []
            
        current_pos = start
        complete_path = [start]
        
        for delivery_point in delivery_points:
            path = self.find_path(current_pos, delivery_point, 0)
            if path:
                complete_path.extend(path[1:])  # Skip first point as it's the current position
                current_pos = delivery_point
            else:
                print(f"Could not find path to delivery point {delivery_point}")
                return complete_path
                
        return complete_path 