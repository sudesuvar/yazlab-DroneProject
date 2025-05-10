from helpers.distance import calculate_distance
from helpers.distance import calculate_cost
import matplotlib.pyplot as plt
import numpy as np


# Örnek veri
pos1 = (0, 0)
pos2 = (10, 10)
distance = calculate_distance(pos1, pos2)
weight = 2.5
priority = 3

# Maliyet hesaplama
cost = calculate_cost(distance, weight, priority)
print(f"Maliyet: {cost}")

# Teslimat noktaları (örnek)
delivery_points = [(2, 3), (5, 6), (8, 1), (7, 8)]

# Drone başlangıç noktası
drone_start = (0, 0)

# Rota: Başlangıç noktasından teslimat noktalarına giden rotalar
route = [drone_start] + delivery_points

# Rota çizimi
route_x, route_y = zip(*route)
plt.plot(route_x, route_y, marker='o', color='b', label='Rota')

# Teslimat noktalarını göster
delivery_x, delivery_y = zip(*delivery_points)
plt.scatter(delivery_x, delivery_y, color='r', label='Teslimat Noktaları')

# Başlangıç noktasını göster
plt.scatter(*drone_start, color='g', label='Drone Başlangıç')

# Harita başlığı ve etiketler
plt.title("Teslimat Rotası Görselleştirmesi")
plt.xlabel("X Koordinatı")
plt.ylabel("Y Koordinatı")
plt.legend()

# Görselleştirme
plt.grid(True)
plt.show()

