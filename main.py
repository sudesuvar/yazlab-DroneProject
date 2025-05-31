import time
from model.data_loader import load_data
from model.data_structures import Drone, DeliveryPoint, NoFlyZone
from model.optimization import DeliveryOptimizer
from model.visualization import DeliveryVisualizer
import numpy as np
import os
from shapely.geometry import Point

def print_scenario_info(drones: list[Drone], deliveries: list[DeliveryPoint], no_fly_zones: list[NoFlyZone]):
    """Print information about the loaded scenario"""
    print("\nLoaded Scenario Information:")
    print(f"Number of Drones: {len(drones)}")
    print(f"Number of Delivery Points: {len(deliveries)}")
    print(f"Number of No-Fly Zones: {len(no_fly_zones)}")

def main():
    # Load scenario data
    print("Loading scenario data...")
    drones, deliveries, no_fly_zones = load_data("s1.txt")
    
    if not drones or not deliveries:
        print("Error: Failed to load scenario data")
        return
    
    # Print scenario information
    print_scenario_info(drones, deliveries, no_fly_zones)
    start_time = time.time()
    # Create visualizer
    visualizer = DeliveryVisualizer(drones, deliveries, no_fly_zones)
    
    # Show initial scenario
    print("\nShowing initial scenario...")
    visualizer.plot_scenario()
    
    # Create optimizer
    optimizer = DeliveryOptimizer(drones, deliveries, no_fly_zones)
    
    # Run optimization
    print("\nStarting optimization...")
    best_solution, fitness_history = optimizer.optimize()
    
    print(f"Best solution found:")
    for drone_id, delivery_sequence in best_solution.items():
        print(f"Drone {drone_id}: {delivery_sequence}")

    # --- Ekstra Raporlama ---
    total_deliveries = sum(len(seq) for seq in best_solution.values())
    total_possible = len(deliveries) * len(drones)
    completed_deliveries = 0
    total_energy = 0
    drone_reports = []
    rapor_lines = []
    for drone in drones:
        seq = best_solution.get(drone.id, [])
        current_pos = drone.start_pos
        current_battery = drone.battery_capacity
        completed = 0
        energy_used = 0
        current_time = 8 * 60
        wait_info = ""
        # Başlangıçta NFZ'de bekleme kontrolü
        for nfz in no_fly_zones:
            if nfz.polygon and nfz.polygon.contains(Point(current_pos)):
                if nfz.is_active_at_time(current_time):
                    wait_time = nfz.active_end - current_time
                    if wait_time > 0:
                        wait_info = f"Başlangıçta NFZ'de {wait_time} dakika bekledi."
                        current_time = nfz.active_end
        for delivery_id in seq:
            delivery = next(d for d in deliveries if d.id == delivery_id)
            # --- NFZ'de bekleme kontrolü ---
            nfz_waited = False
            for nfz in no_fly_zones:
                if nfz.polygon and nfz.polygon.contains(Point(current_pos)):
                    if nfz.is_active_at_time(current_time):
                        wait_time = nfz.active_end - current_time
                        if wait_time > 0:
                            current_time = nfz.active_end
                            nfz_waited = True
            distance = np.sqrt((current_pos[0] - delivery.pos[0])**2 + (current_pos[1] - delivery.pos[1])**2)
            energy = distance * drone.consumption_rate if hasattr(drone, 'consumption_rate') else distance * 0.1
            travel_time = distance / drone.speed if drone.speed > 0 else 0
            # Segmentin başında veya sonunda NFZ aktifliği değişiyorsa bekle
            for nfz in no_fly_zones:
                if nfz.polygon and nfz.polygon.contains(Point(delivery.pos)):
                    if nfz.is_active_at_time(current_time):
                        if not nfz.is_active_at_time(current_time + travel_time):
                            wait_time = nfz.active_end - current_time
                            if wait_time > 0:
                                current_time = nfz.active_end
                                nfz_waited = True
            # Batarya kontrolü
            if current_battery - energy < 0:
                break
            current_battery -= energy
            energy_used += energy
            completed += 1
            current_time += travel_time
            current_pos = delivery.pos
        completed_deliveries += completed
        avg_energy = (energy_used / completed) if completed > 0 else 0
        battery_percent = (current_battery / drone.battery_capacity) * 100 if drone.battery_capacity > 0 else 0
        drone_reports.append((drone.id, completed, len(seq), avg_energy, battery_percent, wait_info))

    rapor_lines.append("\n--- Drone Raporları ---")
    for drone_id, completed, assigned, avg_energy, battery_percent, wait_info in drone_reports:
        if assigned == 0:
            percent = 0
            rapor_lines.append(f"Drone {drone_id}: Tamamlanan teslimat %: 0 | Ortalama enerji tüketimi: 0.00 mAh | Kalan batarya: 100.0% | Not: Hiç teslimat atanmadı. {wait_info}")
        else:
            percent = 100 * completed / assigned if assigned > 0 else 0
            rapor_lines.append(f"Drone {drone_id}: Tamamlanan teslimat %: {percent:.1f} | Ortalama enerji tüketimi: {avg_energy:.2f} mAh | Kalan batarya: {battery_percent:.1f}% {wait_info}")
    total_percent = 100 * completed_deliveries / total_deliveries if total_deliveries > 0 else 0
    rapor_lines.append(f"\nToplam tamamlanan teslimat yüzdesi: {total_percent:.1f}%")
    rapor_lines.append(f"Toplam ortalama enerji tüketimi: {sum(r[3] for r in drone_reports)/len(drone_reports):.2f} mAh")
    end_time = time.time()
    rapor_lines.append(f"Algoritma çalışma süresi: {end_time - start_time:.2f} saniye")


    # Print to terminal
    for line in rapor_lines:
        print(line)

    # Write to file
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, "rapor.txt"), "w", encoding="utf-8") as f:
        for line in rapor_lines:
            f.write(line + "\n")

    # Show optimization progress
    print("\nShowing optimization progress...")
    visualizer.plot_fitness_history(fitness_history)

if __name__ == "__main__":
    main()
