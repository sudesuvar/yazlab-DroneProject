# main.py
import time
from data_loader import load_data
from optimization import run_ga
from visualization import plot_results
from config import GENERATIONS

def main():
    print("--- Drone Fleet Optimization ---")

    # 1. Load Data
    load_start_time = time.time()
    drones, deliveries, no_fly_zones = load_data("data.txt")
    load_time = time.time() - load_start_time
    print(f"Data loading took {load_time:.2f} seconds.")

    print(f"\n--- MAIN DEBUG: Veri Yükleme Sonrası ---")
    print(f"Yüklenen no_fly_zones sayısı: {len(no_fly_zones)}")
    if no_fly_zones:
        for i, nfz_item in enumerate(no_fly_zones):
            print(f"  NFZ {i}: ID={nfz_item.id}, Poligon Geçerli Mi={nfz_item.polygon is not None}")
            if nfz_item.polygon:
                print(f"    Koordinatlar: {list(nfz_item.polygon.exterior.coords)}")
    else:
        print("  Hiçbir No-Fly Zone yüklenmedi veya hepsi geçersizdi.")
    print(f"--- MAIN DEBUG BİTİŞ ---\n")


    if not drones or not deliveries:
        print("HATA: Drone veya teslimat yüklenemedi. Çıkılıyor.")
        return

    # 2. Run Optimization (Genetic Algorithm)
    print("\nOptimizasyon başlatılıyor...")
    ga_start_time = time.time()
    # run_ga fonksiyonuna no_fly_zones listesini de geçirdiğinizden emin olun
    best_solution, best_fitness = run_ga(drones, deliveries, no_fly_zones)
    ga_time = time.time() - ga_start_time
    print(f"Optimizasyon süreci {ga_time:.2f} saniye sürdü ({ga_time/max(1,GENERATIONS):.3f} s/nesil).")

    # GA sonuçlarını yazdır
    if best_solution:
        # Bu kısmı önceki çıktınızdan aldım, gerekirse güncelleyin
        final_delivered = sum(len(route) for route in best_solution) # Basit bir tahmin, evaluate_solution'dan alınmalı
        # final_energy, final_violations değerleri evaluate_solution ile tekrar hesaplanmalı
        print(f"\nGA Tamamlandı.")
        print(f"En İyi Çözüm Bulundu:")
        print(f"  Fitness: {best_fitness:.2f}")
        # Gerçek değerler için evaluate_solution'ı burada tekrar çağırabilirsiniz
        # print(f"  Tamamlanan Teslimatlar: {final_delivered}")
        # print(f"  Toplam Enerji (mAh): {final_energy:.1f}")
        # print(f"  Kısıt İhlalleri: {final_violations}")
    else:
        print("\nGA bir çözüm bulamadı.")


    # 3. Visualize Results (if a solution was found)
    if best_solution:
        print("\n--- MAIN DEBUG: Görselleştirme Öncesi ---")
        print(f"plot_results çağrılmadan önce no_fly_zones sayısı: {len(no_fly_zones)}")
        print(f"--- MAIN DEBUG BİTİŞ ---\n")

        print("\nGörselleştirme oluşturuluyor...")
        plot_start_time = time.time()
        plot_results(drones, deliveries, no_fly_zones, best_solution, "delivery_routes.png")
        plot_time = time.time() - plot_start_time
        print(f"Çizim {plot_time:.2f} saniye sürdü.")
    else:
        print("\nGA tarafından geçerli bir çözüm bulunamadığı için görselleştirme yapılmayacak.")

    print("\n--- Program Tamamlandı ---")

if __name__ == "__main__":
    main()