# Drone Project - YAZLAB II. Proje Ödevi

Bu proje, teslimat noktalarına sahip bir bölge üzerinde droneların uçuş rotalarını optimize etmeyi amaçlamaktadır. Rotalar, enerji limitleri, yük ağırlıkları, teslimat öncelikleri ve uçuş yasağı bölgeleri gibi çeşitli kısıtlar göz önünde bulundurularak A* algoritması, Genetik Algoritma (GA) ve Kısıt Tabanlı Planlama (CSP) yöntemleriyle hesaplanır.


## 🚀 Kullanılan Teknolojiler

- **Python 3.x**
- **NetworkX** → Grafik yapısı ve algoritmalar
- **Matplotlib** → Grafik görselleştirme
- **Heapq** → A* algoritmasında öncelik kuyruğu
- **math, re** → Mesafe hesaplama, veri ayrıştırma


---

## 🧰 Kurulum ve Kullanım

```bash
python3 -m venv .venv
source .venv/bin/activate  # MacOS/Linux
.venv\Scripts\activate     # Windows 
```

## 🧰 Gereksinimleri Yükleyin

```bash
pip install networkx matplotlib
```
```bash
pip install -r requirements.txt
```

###  Projeyi Çalıştır

```bash
 python main.py

```



### 1. Projeyi Klonla
```bash
git clone https://github.com/sudesuvar/yazlab-DroneProject
cd yazlab-DroneProject
```

## Veri Formatı – data.txt

Veriler aşağıdaki formatta data.txt dosyasında olmalıdır.

**DeliveryPoint (teslimat noktası):**
```plaintext
Delivery_1 (
Priority: 2,
Weight: 1.5kg,
Pos: (10.0, 20.0))
```

**Drone:**
```plaintext
Drone_1 (
Max: 1.98kg,
Battery: 3144mAh,
Speed: 7.93m/s,
Start Pos: (5.173075, 44.670)
)
```

**NoFlyZone (Uçuş Yasağı Bölgesi):**
```plaintext
NoFlyZone_1 (
  Points: [
    (45.1664, 55.854),
    (14.8087, 66.5933),
    (77.389, 7.98802),
    (81.33379774, 1.136),
    (24.9431123, 85.582939)
  ],
  Active Time: ('08:35', '09:32')
)
```


## 🚀 Hazırlayanlar
- SUDE DENİZ SUVAR
- ŞEVVAL ZEYNEP AYAR
- ABDÜLKADİR CAN KİNSİZ