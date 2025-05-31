import random
from datetime import datetime, timedelta
from model.data_structures import Drone, DeliveryPoint, NoFlyZone

class LoadData:
    @staticmethod
    def random_time_in_range(start_time_str, end_time_str):
        start_time = datetime.strptime(start_time_str, "%H:%M")
        end_time = datetime.strptime(end_time_str, "%H:%M")
        delta = end_time - start_time
        random_minutes = random.randint(0, delta.seconds // 60)
        random_time = start_time + timedelta(minutes=random_minutes)
        return random_time.strftime("%H:%M")

    @staticmethod
    def random_position(min_x, max_x, min_y, max_y):
        x = random.uniform(min_x, max_x)
        y = random.uniform(min_y, max_y)
        return (x, y)

    @staticmethod
    def generate_random_data(num_drones, num_delivery_points, num_no_fly_zones):
        drones = []
        delivery_points = []
        no_fly_zones = []

        for i in range(1, num_drones + 1):
            drone = Drone(
                id=i,
                max_weight=random.uniform(0.5, 5.0),
                battery=random.randint(1000, 5000),
                speed=random.uniform(5.0, 15.0),
                start_pos=LoadData.random_position(0, 100, 0, 100),
                consumption_rate=random.uniform(0.5, 2.0)  # mAh per meter
            )
            drones.append(drone)

        for i in range(1, num_delivery_points + 1):
            start_time = LoadData.random_time_in_range("08:00", "09:00")
            end_time = LoadData.random_time_in_range("09:00", "18:00")
            delivery_point = DeliveryPoint(
                id=i,
                pos=LoadData.random_position(0, 100, 0, 100),
                weight=random.uniform(0.5, 3.0),
                priority=random.randint(1, 5),
                time_window_start_str=start_time,
                time_window_end_str=end_time
            )
            delivery_points.append(delivery_point)

        for i in range(1, num_no_fly_zones + 1):
            start_time = LoadData.random_time_in_range("08:00", "10:00")
            end_time = LoadData.random_time_in_range("10:00", "18:00")
            coordinates = [LoadData.random_position(0, 100, 0, 100) for _ in range(5)]
            no_fly_zone = NoFlyZone(
                id=i,
                active_start_str=start_time,
                active_end_str=end_time,
                coordinates=coordinates
            )
            no_fly_zones.append(no_fly_zone)

        return drones, delivery_points, no_fly_zones

    @staticmethod
    def save_data_to_txt(drones, delivery_points, no_fly_zones, filename="random_data.txt"):
        with open(filename, 'w') as f:
            # Drones
            f.write("DRONES\n")
            for drone in drones:
                f.write(f"{drone.id}, {round(drone.max_weight, 1)}, {int(drone.battery_capacity * 1000)}, "
                        f"{round(drone.speed, 1)}, {int(drone.start_pos[0])}, {int(drone.start_pos[1])}, "
                        f"{round(drone.consumption_rate, 1)}\n")

            # Deliveries
            f.write("\nDELIVERIES\n")
            for dp in delivery_points:
                f.write(f"{100 + dp.id}, {int(dp.pos[0] * 10)}, {int(dp.pos[1] * 10)}, "
                        f"{round(dp.weight, 1)}, {dp.priority}, {dp.time_window_start_min}, {dp.time_window_end_min}\n")

            # No Fly Zones
            f.write("\nNOFLYZONES\n")
            for nfz in no_fly_zones:
                coords_float = list(nfz.polygon.exterior.coords)
                coords_str = " ".join(f"{int(coord[0])} {int(coord[1])}" for coord in coords_float)
                f.write(f"{200 + nfz.id}, {nfz.active_start_min}, {nfz.active_end_min}, {coords_str}\n")


if __name__ == "__main__":
    # Senaryo 1
    drones1, delivery_points1, no_fly_zones1 = LoadData.generate_random_data(5, 20, 2)
    LoadData.save_data_to_txt(drones1, delivery_points1, no_fly_zones1, "scenario_1.txt")

    # Senaryo 2
    drones2, delivery_points2, no_fly_zones2 = LoadData.generate_random_data(10, 50, 5)
    LoadData.save_data_to_txt(drones2, delivery_points2, no_fly_zones2, "scenario_2.txt")
