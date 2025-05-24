import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Test etmek istediğimiz renk
test_renk = 'lightcoral'
test_alpha = 0.5 # İyi görünürlük için 0.5 kullanalım

print(f"Poligonu şu renkle çizmeye çalışılıyor: {test_renk}")

fig, ax = plt.subplots()

# Basit bir poligon tanımlayın (örneğin bir kare)
poligon_koordinatlari = [(0, 0), (1, 0), (1, 1), (0, 1)]
yamasi = Polygon(
    poligon_koordinatlari,
    closed=True,
    color=test_renk,
    alpha=test_alpha,
    label=f'Test Poligonu ({test_renk})'
)
ax.add_patch(yamasi)

# Karşılaştırma için bilinen standart bir renkle başka bir poligon ekleyin
yamasi_kirmizi = Polygon(
    [(1.5, 0), (2.5, 0), (2.5, 1), (1.5, 1)],
    closed=True,
    color='red', # Standart bir kırmızı
    alpha=0.5,
    label='Test Poligonu (kırmızı)'
)
ax.add_patch(yamasi_kirmizi)


ax.set_xlim(-0.5, 3.0)
ax.set_ylim(-0.5, 1.5)
ax.set_aspect('equal')
ax.legend()
ax.set_title(f"Renk Testi")
plt.show()

print("Test betiği tamamlandı.")