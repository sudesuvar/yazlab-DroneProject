# data_loader.py
from data_structures import Drone, DeliveryPoint, NoFlyZone
from config import DEFAULT_CONSUMPTION_RATE_MAH_PER_METER # config.py'den import

def load_data(filepath="data.txt"):
    drones = []
    deliveries = []
    no_fly_zones = []
    current_section = None
    print(f"--- DATA_LOADER DEBUG BAŞLANGIÇ ---")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line == "DRONES":
                    current_section = "DRONES"
                    print(f"  DATA_LOADER: DRONES bölümüne geçildi.")
                    continue
                elif line == "DELIVERIES":
                    current_section = "DELIVERIES"
                    print(f"  DATA_LOADE R: DELIVERIES bölümüne geçildi.")
                    continue
                elif line == "NOFLYZONES":
                    current_section = "NOFLYZONES"
                    print(f"  DATA_LOADER: NOFLYZONES bölümüne geçildi.")
                    continue

                parts = line.split(',')
                if not parts: continue

                try:
                    if current_section == "DRONES":
                        # ... (drone yükleme kodu aynı kalabilir) ...
                        if len(parts) < 6: continue
                        drone_id = int(parts[0].strip())
                        max_w = float(parts[1].strip())
                        batt = int(parts[2].strip())
                        speed = float(parts[3].strip())
                        start_x = float(parts[4].strip())
                        start_y = float(parts[5].strip())
                        consumption = float(parts[6].strip()) if len(parts) > 6 else DEFAULT_CONSUMPTION_RATE_MAH_PER_METER
                        drones.append(Drone(drone_id, max_w, batt, speed, (start_x, start_y), consumption))
                    elif current_section == "DELIVERIES":
                        # ... (delivery yükleme kodu aynı kalabilir) ...
                        if len(parts) < 7: continue
                        del_id = int(parts[0].strip())
                        pos_x = float(parts[1].strip())
                        pos_y = float(parts[2].strip())
                        weight = float(parts[3].strip())
                        prio = int(parts[4].strip())
                        tw_start = parts[5].strip()
                        tw_end = parts[6].strip()
                        deliveries.append(DeliveryPoint(del_id, (pos_x, pos_y), weight, prio, tw_start, tw_end))
                    elif current_section == "NOFLYZONES":
                        print(f"    DATA_LOADER: NOFLYZONES satır {line_num} işleniyor: '{line}'")
                        if len(parts) < 4:
                            print(f"      UYARI: Satır {line_num} NFZ için yetersiz parça ({len(parts)}), atlanıyor.")
                            continue
                        nfz_id_str = parts[0].strip()
                        active_start_str = parts[1].strip()
                        active_end_str = parts[2].strip()
                        coord_parts_str = parts[3].strip()
                        print(f"      Ayrıştırılan parçalar: id='{nfz_id_str}', active='{active_start_str}-{active_end_str}', coords_str='{coord_parts_str}'")

                        try:
                            nfz_id = int(nfz_id_str)
                        except ValueError:
                            print(f"      HATA: NFZ ID '{nfz_id_str}' integer değil, satır atlanıyor.")
                            continue

                        coord_parts = coord_parts_str.split()
                        if len(coord_parts) < 6 or len(coord_parts) % 2 != 0: # En az 3 nokta (6 koordinat)
                            print(f"      UYARI: NFZ {nfz_id} için yetersiz veya tek sayıda koordinat ({len(coord_parts)}), atlanıyor.")
                            continue

                        coordinates = []
                        valid_coords_in_line = True
                        for i in range(0, len(coord_parts), 2):
                            try:
                                x = float(coord_parts[i])
                                y = float(coord_parts[i+1])
                                coordinates.append((x, y))
                            except ValueError:
                                print(f"      HATA: NFZ {nfz_id} için geçersiz koordinat değeri: '{coord_parts[i]}' veya '{coord_parts[i+1]}', bu NFZ atlanıyor.")
                                valid_coords_in_line = False
                                break
                        if not valid_coords_in_line:
                            continue

                        print(f"      NFZ {nfz_id} için ayrıştırılan koordinatlar: {coordinates}")
                        if len(coordinates) < 3: # Shapely Polygon için en az 3 nokta gerekir
                             print(f"      UYARI: NFZ {nfz_id} için poligon oluşturmak üzere yetersiz nokta ({len(coordinates)} < 3), atlanıyor.")
                             continue

                        new_nfz = NoFlyZone(nfz_id, active_start_str, active_end_str, coordinates)
                        if new_nfz.polygon:
                            print(f"      BAŞARILI: NFZ {nfz_id} oluşturuldu ve poligonu geçerli. Listeye ekleniyor.")
                            no_fly_zones.append(new_nfz)
                        else:
                            print(f"      UYARI: NFZ {nfz_id} oluşturuldu ANCAK poligonu geçersiz (None). Listeye EKLENMİYOR (veya eklendi ama çizilmeyecek).")
                            # Eğer None poligonlu NFZ'leri de listede tutmak isterseniz bu satırı değiştirin.
                            # Şimdilik, sadece geçerli poligonu olanları ekliyoruz.
                except (ValueError, IndexError) as e:
                    print(f"    UYARI: Bölüm {current_section}, satır {line_num} işlenirken hata: {line} - Hata: {e}")

    except FileNotFoundError:
        print(f"HATA: Veri dosyası bulunamadı: {filepath}")
        return [], [], []
    except Exception as e:
        print(f"Veri yüklenirken genel bir hata oluştu: {e}")
        return [], [], []

    print(f"  DATA_LOADER: Yüklendi: {len(drones)} drone, {len(deliveries)} teslimat, {len(no_fly_zones)} no-fly zone.")
    print(f"--- DATA_LOADER DEBUG SONU ---")
    return drones, deliveries, no_fly_zones