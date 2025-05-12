import random
from datetime import datetime, timedelta
from models import Drone, DeliveryPoint, NoFlyZone

class LoadData:
    @staticmethod
    def random_time_in_range(start_time_str, end_time_str):
        """Generates a random time between start_time_str and end_time_str."""
        start_time = datetime.strptime(start_time_str, "%H:%M")
        end_time = datetime.strptime(end_time_str, "%H:%M")
        delta = end_time - start_time
        random_minutes = random.randint(0, delta.seconds // 60)
        random_time = start_time + timedelta(minutes=random_minutes)
        return random_time.strftime("%H:%M")

    @staticmethod
    def random_position(min_x, max_x, min_y, max_y):
        """Generates a random position within the specified range."""
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        return (x, y)

    @staticmethod
    def generate_random_data():
        """Generates random drones, delivery points, and no-fly zones."""
        num_drones = 5
        num_delivery_points = 10
        num_no_fly_zones = 3

        drones = []
        delivery_points = []
        no_fly_zones = []

        # Generate random drones
        for i in range(1, num_drones + 1):
            drone = Drone(
                drone_id=i,
                max_weight=random.uniform(0.5, 5.0),  # Max weight between 0.5kg and 5.0kg
                battery=random.randint(1000, 5000),  # Battery between 1000mAh and 5000mAh
                speed=random.uniform(5.0, 15.0),  # Speed between 5 m/s and 15 m/s
                start_pos=LoadData.random_position(0, 100, 0, 100)  # Random start position within 0-100 x and y
            )
            drones.append(drone)

        # Generate random delivery points
        for i in range(1, num_delivery_points + 1):
            delivery_point = DeliveryPoint(
                point_id=i,
                pos=LoadData.random_position(0, 100, 0, 100),  # Random position within 0-100 x and y
                weight=random.uniform(0.5, 3.0),  # Weight between 0.5kg and 3.0kg
                priority=random.randint(1, 5),  # Random priority between 1 and 5
                time_window=(LoadData.random_time_in_range("08:00", "09:00"), LoadData.random_time_in_range("09:00", "10:00"))
            )
            delivery_points.append(delivery_point)

        # Generate random no-fly zones
        for i in range(1, num_no_fly_zones + 1):
            no_fly_zone = NoFlyZone(
                zone_id=i,
                coordinates=[LoadData.random_position(0, 100, 0, 100) for _ in range(5)],  # Random polygon with 5 points
                active_time=(LoadData.random_time_in_range("08:00", "09:00"), LoadData.random_time_in_range("09:00", "10:00"))
            )
            no_fly_zones.append(no_fly_zone)

        return drones, delivery_points, no_fly_zones

    @staticmethod
    def save_data_to_txt(drones, delivery_points, no_fly_zones, filename="data.txt"):
        """Saves the generated data to a text file."""
        with open(filename, 'w') as f:
            f.write("Drones:\n")
            for drone in drones:
                f.write(f"{drone}\n")

            f.write("\nDelivery Points:\n")
            for delivery_point in delivery_points:
                f.write(f"{delivery_point}\n")

            f.write("\nNo Fly Zones:\n")
            for no_fly_zone in no_fly_zones:
                f.write(f"{no_fly_zone}\n")

# Generate and save random data
drones, delivery_points, no_fly_zones = LoadData.generate_random_data()
LoadData.save_data_to_txt(drones, delivery_points, no_fly_zones)

print("random_data.txt has been saved.")