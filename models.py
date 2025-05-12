class Drone:
    def __init__(self, drone_id, max_weight, battery, speed, start_pos):
        self.drone_id = drone_id
        self.max_weight = max_weight
        self.battery = battery
        self.speed = speed
        self.start_pos = start_pos

    def __str__(self):
        return (f"Drone_{self.drone_id} "
                f"(Max: {self.max_weight:.2f}kg, Battery: {self.battery}mAh, "
                f"Speed: {self.speed:.2f}m/s, Start Pos: {self.start_pos})")


class DeliveryPoint:
    def __init__(self, point_id, pos, weight, priority, time_window):
        self.point_id = point_id
        self.pos = pos
        self.weight = weight
        self.priority = priority
        self.time_window = time_window

    def __str__(self):
        return (f"Delivery_{self.point_id} (Priority: {self.priority}, Weight: {self.weight:.2f}kg, "
                f"Pos: {self.pos}, Time Window: {self.time_window})")


class NoFlyZone:
    def __init__(self, zone_id, coordinates, active_time):
        self.zone_id = zone_id
        self.coordinates = coordinates
        self.active_time = active_time

    def __str__(self):
        return (f"NoFlyZone_{self.zone_id} "
                f"(Points: {self.coordinates}, Active Time: {self.active_time})")
