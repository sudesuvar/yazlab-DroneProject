[⚠️ Suspicious Content] 
# Drone Project - YAZLAB II. Proje Ödevi

Bu proje, teslimat noktalarına sahip bir bölge üzerinde droneların uçuş rotalarını optimize etmeyi amaçlamaktadır. Rotalar, enerji limitleri, yük ağırlıkları, teslimat öncelikleri ve uçuş yasağı bölgeleri gibi çeşitli kısıtlar göz önünde bulundurularak A* algoritması, Genetik Algoritma (GA) ve Kısıt Tabanlı Planlama (CSP) yöntemleriyle hesaplanır.


## 🚀 Kullanılan Teknolojiler

- **Python 3.x**
- **numpy** 
- **Matplotlib** 


---

## 🧰 Kurulum ve Kullanım

```bash
python3 -m venv .venv
source .venv/bin/activate  # MacOS/Linux
.venv\Scripts\activate     # Windows 
```

## 🧰 Gereksinimleri Yükleyin


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

## Veri Formatı 

**DeliveryPoint (teslimat noktası):**
```plaintext
{"id": 1,
"pos": (15, 25), 
"weight": 1.5, 
"priority": 3, 
"time_window": (0, 60)},
```

**Drone:**
```plaintext
{"id": 1,
"max_weight": 4.0,
"battery": 12000,
"speed": 8.0, 
"start_pos": (10, 10)},
```

**NoFlyZone (Uçuş Yasağı Bölgesi):**
```plaintext
{"id": 1,
"coordinates": [(40, 30), (60, 30), (60, 50), (40, 50)],
"active_time": (0, 120)},
```

---

![Akış Şeması](https://github.com/sudesuvar/yazlab-DroneProject/blob/main/output/drone_1.png)

![Akış Şeması](https://github.com/sudesuvar/yazlab-DroneProject/blob/main/output/drone_2.png)

---


## 🚀 Hazırlayanlar
- SUDE DENİZ SUVAR
- ŞEVVAL ZEYNEP AYAR
- ABDÜLKADİR CAN KİNSİZ





