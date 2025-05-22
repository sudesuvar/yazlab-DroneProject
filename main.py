import time
from data_loader import load_data
from optimization import run_ga
from visualization import plot_results
from config import GENERATIONS


def run_scenario(filename, output_image):
    print(f"\n========== {filename.upper()} için Optimizasyon Başlatılıyor ==========")

    # 1. Load Data
    load_start_time = time.time()
    drones, deliveries, no_fly_zones = load_data(filename)
    load_time = time.time() - load_start_time
    print(f"Data loading took {load_time:.2f} seconds.")

    print(f"\n--- DEBUG: {filename} No-Fly Zone Bilgileri ---")
    print(f"Yüklenen no_fly_zones sayısı: {len(no_fly_zones)}")
    for i, nfz in enumerate(no_fly_zones):
        print(f"  NFZ {i}: ID={nfz.id}, Poligon Geçerli Mi={nfz.polygon is not None}")
        if nfz.polygon:
            print(f"    Koordinatlar: {list(nfz.polygon.exterior.coords)}")

    if not drones or not deliveries:
        print("HATA: Drone veya teslimat yüklenemedi. Çıkılıyor.")
        return

    # 2. Run Optimization
    print("\nOptimizasyon başlatılıyor...")
    ga_start_time = time.time()
    best_solution, best_fitness = run_ga(drones, deliveries, no_fly_zones)
    ga_time = time.time() - ga_start_time
    print(f"Optimizasyon süreci {ga_time:.2f} saniye sürdü ({ga_time / max(1, GENERATIONS):.3f} s/nesil).")

    if best_solution:
        final_delivered = sum(len(route) for route in best_solution)
        print(f"\nGA Tamamlandı.")
        print(f"  Fitness: {best_fitness:.2f}")
        print(f"  Tamamlanan Teslimatlar: {final_delivered}")
    else:
        print("\nGA bir çözüm bulamadı.")

    # 3. Visualize Results
    if best_solution:
        print("\nGörselleştirme oluşturuluyor...")
        plot_start_time = time.time()
        plot_results(drones, deliveries, no_fly_zones, best_solution, output_image)
        plot_time = time.time() - plot_start_time
        print(f"Çizim {plot_time:.2f} saniye sürdü.")
    else:
        print("Geçerli çözüm yok, çizim yapılmadı.")

    print(f"\n========== {filename.upper()} Senaryosu Tamamlandı ==========")


def main():
    print("--- Drone Fleet Optimization - Çoklu Senaryo ---")

    run_scenario("scenario_1.txt", "scenario1_routes.png")
    run_scenario("scenario_2.txt", "scenario2_routes.png")

    print("\n--- Tüm Senaryolar Tamamlandı ---")


if __name__ == "__main__":
    main()
