import time
from model.data_loader import load_data
from optimization import run_ga
from visualization import plot_results
from config import GENERATIONS
from simulation import evaluate_solution


def run_scenario(filename, output_image):
    print(f"\n========== {filename.upper()} için Optimizasyon Başlatılıyor ==========")

    # 1. Load Data
    load_start_time = time.time()
    drones, deliveries, no_fly_zones = load_data(filename)
    load_time = time.time() - load_start_time
    print(f"Veri yükleme süresi: {load_time:.2f} saniye.")

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

    metrics_text = ""
    if best_solution:
        final_delivered = sum(len(route) for route in best_solution)
        total_deliveries = len(deliveries)
        delivery_percentage = (final_delivered / total_deliveries) * 100 if total_deliveries > 0 else 0

        total_consumption = sum(d.battery_capacity - d.current_battery for d in drones)
        average_consumption = total_consumption / len(drones) if drones else 0

        print(f"\nGA Tamamlandı.")
        print(f"  Fitness: {best_fitness:.2f}")
        print(f"  Tamamlanan Teslimatlar: {final_delivered}/{total_deliveries}")
        print(f"\n--- METRİKLER ---")
        print(f"  Tamamlanan Teslimat Yüzdesi: %{delivery_percentage:.2f}")
        print(f"  Ortalama Enerji Tüketimi: {average_consumption:.2f} mAh")
        print(f"  Toplam GA Süresi: {ga_time:.2f} saniye")
        
        all_deliveries_dict = {delivery.id: delivery for delivery in deliveries}
        total_delivered, total_energy, total_violations = evaluate_solution(
            best_solution, drones, all_deliveries_dict, no_fly_zones)   

        # Metrik metni görselleştirme için hazırla
        metrics_text = (
            f"Teslimat Yüzdesi: %{delivery_percentage:.1f}\n"
            f"Ortalama Enerji: {average_consumption:.1f} mAh\n"
            f"Süre: {ga_time:.1f} s"
            f"✅ Başarıyla Teslim: {total_delivered}\n"
            f"🔋 Enerji: {total_energy:.2f} mAh\n"
            f"⚠️ İhlal: {total_violations}"
            
        )
    else:
        print("\nGA bir çözüm bulamadı.")

    # 3. Visualize Results
    if best_solution:
        print("\nGörselleştirme oluşturuluyor...")
        plot_start_time = time.time()
        plot_results(
            drones, deliveries, no_fly_zones,
            best_solution, output_image,
            metrics_text=metrics_text  # Metrik metni ekleniyor
        )
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
