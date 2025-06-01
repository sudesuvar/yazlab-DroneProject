import time
import os
import random
import shutil
import numpy as np
import json
from shapely.geometry import Polygon

# Burada data_structures'daki sınıfları import ediyoruz
from model.data_structures import Drone, DeliveryPoint, NoFlyZone
from model.optimization import DeliveryOptimizer
from model.visualization import DeliveryVisualizer
from model.data_loader import load_data  # Sabit senaryo dosyası için


def clear_output_folder(path="output"):
    if os.path.exists(path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        os.makedirs(path)


def generate_random_scenario_v2(num_drones=10, num_deliveries=30, num_no_fly_zones=5, area_size=(100, 100)):
    def random_time_str(start=0, end=1440):
        total_minutes = random.randint(start, end)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02}:{minutes:02}"

    drones = []
    for i in range(1, num_drones + 1):
        drone = {
            "id": i,
            "max_weight": round(random.uniform(2.0, 6.0), 1),
            "battery_capacity": random.randint(8000, 20000),
            "speed": round(random.uniform(5.0, 12.0), 1),
            "start_pos": (random.randint(0, area_size[0]), random.randint(0, area_size[1])),
            "consumption_rate": round(random.uniform(0.05, 0.2), 3)
        }
        drones.append(drone)

    deliveries = []
    for i in range(1, num_deliveries + 1):
        first_time = random_time_str(300, 900)  # 05:00 - 15:00 arası
        last_time = random_time_str(901, 1200)   # 15:01 - 20:00 arası
        delivery = {
            "id": i,
            "pos": (random.randint(0, area_size[0]), random.randint(0, area_size[1])),
            "weight": round(random.uniform(0.5, 5.0), 1),
            "priority": random.randint(1, 5),
            "time_window_start_str": first_time,
            "time_window_end_str": last_time,
        }
        deliveries.append(delivery)

    no_fly_zones = []
    for i in range(1, num_no_fly_zones + 1):
        x1 = random.randint(10, area_size[0] - 30)
        y1 = random.randint(10, area_size[1] - 30)
        width = random.randint(10, 20)
        height = random.randint(10, 20)
        active_start = random_time_str(300, 700)
        active_end = random_time_str(701, 1000)
        zone = {
            "id": i,
            "coordinates": [
                (x1, y1),
                (x1 + width, y1),
                (x1 + width, y1 + height),
                (x1, y1 + height)
            ],
            "active_start_str": active_start,
            "active_end_str": active_end
        }
        no_fly_zones.append(zone)

    return {
        "drones": drones,
        "deliveries": deliveries,
        "no_fly_zones": no_fly_zones
    }


def print_scenario_info(drones: list[Drone], deliveries: list[DeliveryPoint], no_fly_zones: list[NoFlyZone]):
    print("\nLoaded Scenario Information:")
    print(f"Number of Drones: {len(drones)}")
    print(f"Number of Delivery Points: {len(deliveries)}")
    print(f"Number of No-Fly Zones: {len(no_fly_zones)}")


def main():
    # Senaryo çalışmaya başlamadan önce output klasörünü temizle
    clear_output_folder("output")

    # Senaryo seçimi
    print("Senaryo Seçimi:")
    print("1 - Sabit Veri (s1.txt)")
    print("2 - Rastgele Senaryo (Random Scenario)")
    choice = input("Seçiminizi yapın (1 veya 2): ")

    if choice == "1":
        print("Loading scenario data from file...")
        drones, deliveries, no_fly_zones = load_data("s1.txt")

    elif choice == "2":
        print("Generating random scenario...")
        scenario = generate_random_scenario_v2()

        # Random senaryoyu s2.txt dosyasına JSON olarak kaydet
        with open("s2.txt", "w", encoding="utf-8") as f:
            json.dump(scenario, f, indent=2, ensure_ascii=False)
        print("Random senaryo s2.txt dosyasına kaydedildi.")

        drones = [Drone(**d) for d in scenario["drones"]]
        deliveries = [DeliveryPoint(**d) for d in scenario["deliveries"]]
        no_fly_zones = [NoFlyZone(**z) for z in scenario["no_fly_zones"]]

    else:
        print("Geçersiz seçim. Program sonlandırılıyor.")
        return

    # Polygonları oluştur
    for zone in no_fly_zones:
        zone.polygon = Polygon(zone.coordinates)

    if not drones or not deliveries:
        print("Error: Failed to load scenario data")
        return
    start_time = time.time() # Start timer
    print_scenario_info(drones, deliveries, no_fly_zones)

    visualizer = DeliveryVisualizer(drones, deliveries, no_fly_zones)

    print("\nShowing initial scenario...")
    visualizer.plot_scenario()

    optimizer = DeliveryOptimizer(drones, deliveries, no_fly_zones)

    print("\nStarting optimization...")
    
    best_solution, fitness_history = optimizer.optimize()
    print(f"Best solution found:")
    for drone_id, delivery_sequence in best_solution.items():
        print(f"Drone {drone_id}: {delivery_sequence}")

    # --- Raporlama ---
    completed_deliveries = 0
    drone_reports = []
    rapor_lines = []
    for drone in drones:
        seq = best_solution.get(drone.id, [])
        current_pos = drone.start_pos
        current_battery = drone.battery_capacity
        completed = 0
        energy_used = 0
        for delivery_id in seq:
            delivery = next(d for d in deliveries if d.id == delivery_id)
            distance = np.sqrt((current_pos[0] - delivery.pos[0])**2 + (current_pos[1] - delivery.pos[1])**2)
            energy = distance * drone.consumption_rate if hasattr(drone, 'consumption_rate') else distance * 0.1
            if current_battery - energy < 0:
                break
            current_battery -= energy
            energy_used += energy
            completed += 1
            current_pos = delivery.pos
        completed_deliveries += completed
        avg_energy = (energy_used / completed) if completed > 0 else 0
        battery_percent = (current_battery / drone.battery_capacity) * 100 if drone.battery_capacity > 0 else 0
        drone_reports.append((drone.id, completed, len(seq), avg_energy, battery_percent))

    rapor_lines.append("\n--- Drone Raporları ---")
    for drone_id, completed, assigned, avg_energy, battery_percent in drone_reports:
        percent = 100 * completed / assigned if assigned > 0 else 0
        rapor_lines.append(f"Drone {drone_id}: Tamamlanan teslimat %: {percent:.1f} | Ortalama enerji tüketimi: {avg_energy:.2f} mAh | Kalan batarya: {battery_percent:.1f}%")

    total_deliveries = sum(len(seq) for seq in best_solution.values())
    total_percent = 100 * completed_deliveries / total_deliveries if total_deliveries > 0 else 0
    rapor_lines.append(f"\nToplam tamamlanan teslimat yüzdesi: {total_percent:.1f}%")
    end_time = time.time() # End timer
    rapor_lines.append(f"Algoritma çalışma süresi: {end_time - start_time:.2f} saniye")

    for line in rapor_lines:
        print(line)

    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, "rapor.txt"), "w", encoding="utf-8") as f:
        for line in rapor_lines:
            f.write(line + "\n")

    print("\nShowing optimization progress...")
    visualizer.plot_fitness_history(fitness_history)


if __name__ == "__main__":
    main()
