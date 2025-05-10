# data_structures.py
from shapely.geometry import Polygon
from utils import time_str_to_minutes

class Drone:
    def __init__(self, id, max_weight, battery, speed, start_pos, consumption_rate):
        self.id = id
        self.max_weight = float(max_weight)
        self.battery_capacity = int(battery)
        self.current_battery = float(battery) # Start fully charged
        self.speed = float(speed) # m/s
        self.start_pos = tuple(map(float, start_pos))
        self.current_pos = self.start_pos
        self.consumption_rate = float(consumption_rate) # mAh per meter
        self.current_payload_weight = 0.0
        self.route = [] # List of delivery point IDs assigned
        self.completed_deliveries = []
        self.current_time = 0 # Simulation time for this drone (in minutes)

    def __repr__(self):
        return f"Drone(id={self.id}, max_w={self.max_weight}, batt={self.battery_capacity}mAh, speed={self.speed}m/s, start={self.start_pos})"

    def reset(self):
        """Resets drone state for a new simulation/evaluation."""
        self.current_battery = float(self.battery_capacity)
        self.current_pos = self.start_pos
        self.current_payload_weight = 0.0
        self.route = []
        self.completed_deliveries = []
        self.current_time = 0 # Reset simulation time

class DeliveryPoint:
    def __init__(self, id, pos, weight, priority, time_window_start_str, time_window_end_str):
        self.id = id
        self.pos = tuple(map(float, pos))
        self.weight = float(weight)
        self.priority = int(priority) # 1 (low) to 5 (high)
        self.time_window_start_min = time_str_to_minutes(time_window_start_str)
        self.time_window_end_min = time_str_to_minutes(time_window_end_str)
        self.assigned_drone_id = None
        self.status = "pending" # pending, assigned, completed, failed

    def __repr__(self):
        start_t = self.time_window_start_min if self.time_window_start_min is not None else "N/A"
        end_t = self.time_window_end_min if self.time_window_end_min is not None else "N/A"
        return f"Delivery(id={self.id}, pos={self.pos}, w={self.weight}kg, prio={self.priority}, win=[{start_t}-{end_t}])"

    def is_time_window_valid(self, arrival_time_minutes):
        """Checks if arrival time is within the delivery time window."""
        if self.time_window_start_min is None or self.time_window_end_min is None:
            return True # No time window constraint
        return self.time_window_start_min <= arrival_time_minutes <= self.time_window_end_min

class NoFlyZone:
    def __init__(self, id, active_start_str, active_end_str, coordinates):
        self.id = id
        self.active_start_min = time_str_to_minutes(active_start_str)
        self.active_end_min = time_str_to_minutes(active_end_str)
        # Ensure coordinates are tuples of floats
        coords_float = [tuple(map(float, p)) for p in coordinates]
        self.polygon = Polygon(coords_float) if len(coords_float) >= 3 else None

    def __repr__(self):
        start_t = self.active_start_min if self.active_start_min is not None else "N/A"
        end_t = self.active_end_min if self.active_end_min is not None else "N/A"
        return f"NFZ(id={self.id}, active=[{start_t}-{end_t}], area={self.polygon.area if self.polygon else 0})"

    def is_active(self, current_time_minutes):
        """Checks if the NFZ is active at the given time."""
        if self.active_start_min is None or self.active_end_min is None:
            return True # Always active if no time specified
        if self.polygon is None:
            return False # Invalid polygon definition
        return self.active_start_min <= current_time_minutes <= self.active_end_min