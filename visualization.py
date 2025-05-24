# visualization.py
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from model.data_structures import Drone, DeliveryPoint, NoFlyZone
from pathfinding import find_path_a_star
import copy

TARGET_NFZ_COLOR = 'lightcoral'
TARGET_NFZ_ALPHA = 0.4

def plot_results(drones, deliveries, no_fly_zones, best_solution, filename="delivery_routes.png", metrics_text=None):
    fig, ax = plt.subplots(figsize=(12, 10))

    all_deliveries_dict = {d.id: d for d in deliveries}
    sim_drones = [copy.deepcopy(d) for d in drones]

    print(f"\n--- VISUALIZATION DEBUG BAŞLANGIÇ ---")
    print(f"plot_results fonksiyonu başında TARGET_NFZ_COLOR: {TARGET_NFZ_COLOR}")
    print(f"plot_results fonksiyonuna gelen no_fly_zones listesinin UZUNLUĞU: {len(no_fly_zones)}")
    if no_fly_zones:
        for idx, nfz_check in enumerate(no_fly_zones):
            print(f"  Gelen NFZ {idx}: ID={nfz_check.id}, Poligon Geçerli Mi={nfz_check.polygon is not None}")
            if nfz_check.polygon:
                 print(f"    Koordinatlar: {list(nfz_check.polygon.exterior.coords)}")
    else:
        print("  plot_results fonksiyonuna BOŞ bir no_fly_zones listesi geldi.")

    nfz_plotted_in_legend = False
    for nfz_idx, nfz in enumerate(no_fly_zones):
        print(f"  NFZ döngüsü içinde, nfz_idx: {nfz_idx}, nfz.id: {nfz.id}")
        if nfz.polygon:
            coords = list(nfz.polygon.exterior.coords)
            print(f"    NFZ {nfz.id} için poligon geçerli, koordinatlar: {coords}. Renk: {TARGET_NFZ_COLOR}")
            patch = MplPolygon(
                coords,
                closed=True,
                color=TARGET_NFZ_COLOR,
                alpha=TARGET_NFZ_ALPHA,
                label='No-Fly Zone' if not nfz_plotted_in_legend else ""
            )
            ax.add_patch(patch)
            nfz_plotted_in_legend = True
        else:
            print(f"    UYARI: NFZ {nfz.id} için geçerli bir poligon bulunamadı (nfz.polygon is None), çizilmeyecek.")

    all_assigned_ids = set(item for sublist in best_solution for item in sublist) if best_solution else set()
    pending_x = [d.pos[0] for d in deliveries if d.id not in all_assigned_ids]
    pending_y = [d.pos[1] for d in deliveries if d.id not in all_assigned_ids]
    assigned_x = [d.pos[0] for d in deliveries if d.id in all_assigned_ids]
    assigned_y = [d.pos[1] for d in deliveries if d.id in all_assigned_ids]

    if assigned_x:
        ax.scatter(assigned_x, assigned_y, c='blue', marker='o', label='Delivery Points (Assigned)', s=50, zorder=3)
    if pending_x:
         ax.scatter(pending_x, pending_y, c='gray', marker='x', label='Delivery Points (Not Assigned/Failed)', s=50, zorder=3)

    start_x = [d.start_pos[0] for d in drones]
    start_y = [d.start_pos[1] for d in drones]
    ax.scatter(start_x, start_y, c='green', marker='s', s=100, label='Drone Start', zorder=4)
    for i, drone_obj in enumerate(drones):
        ax.annotate(f" D{drone_obj.id}", (start_x[i], start_y[i]), zorder=5)

    colors = plt.cm.viridis([i / max(1, len(sim_drones)) for i in range(len(sim_drones))])
    all_x_coords = start_x + [d.pos[0] for d in deliveries]
    all_y_coords = start_y + [d.pos[1] for d in deliveries]

    if best_solution:
        for i, drone_route_ids in enumerate(best_solution):
            if i >= len(sim_drones): continue

            drone = sim_drones[i]
            drone.reset()
            drone.current_time = 0

            current_pos = drone.start_pos
            path_x = [current_pos[0]]
            path_y = [current_pos[1]]
            route_color = colors[i % len(colors)]

            for delivery_id in drone_route_ids:
                delivery = all_deliveries_dict.get(delivery_id)
                if not delivery: continue

                path_segment, dist, energy, time_sec, violates_nfz = find_path_a_star(
                    current_pos, delivery.pos, drone, no_fly_zones, drone.current_time
                )

                line_style = '--' if violates_nfz else '-'
                line_alpha = 0.6 if violates_nfz else 0.9
                line_color = 'deeppink' if violates_nfz else route_color

                if drone.current_battery >= energy and delivery.weight <= drone.max_weight:
                    ax.plot([current_pos[0], delivery.pos[0]], [current_pos[1], delivery.pos[1]],
                            color=line_color, linestyle=line_style, marker='', alpha=line_alpha, linewidth=1.5, zorder=2)
                    drone.current_battery -= energy
                    drone.current_time += time_sec / 60.0
                    current_pos = delivery.pos
                    path_x.append(current_pos[0])
                    path_y.append(current_pos[1])
                else:
                    ax.plot([current_pos[0], delivery.pos[0]], [current_pos[1], delivery.pos[1]],
                            color='dimgray', linestyle=':', marker='x', alpha=0.7, linewidth=1, zorder=2)
                    break

            if len(path_x) > 1:
                drone_label = f'Drone {drone.id} Route'
                ax.plot(path_x, path_y, color=route_color, linestyle='', marker='.', label=drone_label, markersize=5, zorder=2.5)

    if all_x_coords or all_y_coords:
        for nfz_item in no_fly_zones:
            if nfz_item.polygon:
                nfz_x, nfz_y = nfz_item.polygon.exterior.xy
                all_x_coords.extend(nfz_x)
                all_y_coords.extend(nfz_y)

        min_x = min(all_x_coords) if all_x_coords else -1000
        max_x = max(all_x_coords) if all_x_coords else 1000
        min_y = min(all_y_coords) if all_y_coords else -1000
        max_y = max(all_y_coords) if all_y_coords else 1000

        range_x = max_x - min_x if (max_x - min_x) > 0 else 100
        range_y = max_y - min_y if (max_y - min_y) > 0 else 100
        padding_x = range_x * 0.1
        padding_y = range_y * 0.1
        ax.set_xlim(min_x - padding_x, max_x + padding_x)
        ax.set_ylim(min_y - padding_y, max_y + padding_y)
    else:
        ax.set_xlim(-1000, 1000)
        ax.set_ylim(-1000, 1000)

    ax.set_xlabel("X Coordinate (meters)")
    ax.set_ylabel("Y Coordinate (meters)")
    ax.set_title("Optimized Drone Delivery Routes with No-Fly Zones")

    handles, labels = ax.get_legend_handles_labels()
    by_label = {}
    for handle, label in zip(handles, labels):
        if label not in by_label:
            by_label[label] = handle
    if by_label:
        ax.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0.)

    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    # METRİKLERİ HESAPLA VE SAĞA EKLE
    total_energy = 0
    total_time = 0
    total_deliveries = 0
    nfz_violations = 0

    for i, drone_route_ids in enumerate(best_solution):
        if i >= len(sim_drones): continue
        drone = copy.deepcopy(sim_drones[i])
        current_pos = drone.start_pos

        for delivery_id in drone_route_ids:
            delivery = all_deliveries_dict.get(delivery_id)
            if not delivery: continue

            _, dist, energy, time_sec, violates_nfz = find_path_a_star(
                current_pos, delivery.pos, drone, no_fly_zones, drone.current_time
            )

            if drone.current_battery >= energy and delivery.weight <= drone.max_weight:
                total_energy += energy
                total_time += time_sec
                total_deliveries += 1
                if violates_nfz:
                    nfz_violations += 1
                drone.current_battery -= energy
                drone.current_time += time_sec / 60.0
                current_pos = delivery.pos

    metrics_text = (
        f"Total Energy: {total_energy:.2f} J\n"
        f"Total Time: {total_time / 60:.2f} min\n"
        f"Total Deliveries: {total_deliveries}\n"
        f"No-Fly Zone Violations: {nfz_violations}"
        
        
    )
    plt.gcf().text(0.86, 0.5, metrics_text, fontsize=10, va='center', bbox=dict(facecolor='white', edgecolor='gray'))

    try:
        plt.savefig(filename, bbox_inches='tight')
        print(f"Route visualization saved to {filename}")
    except Exception as e:
        print(f"Error saving plot: {e}")
    plt.show()
    print(f"--- VISUALIZATION DEBUG SONU ---")
