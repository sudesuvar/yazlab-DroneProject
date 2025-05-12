import re
import math
import networkx as nx
import matplotlib.pyplot as plt

def calculate_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

def parse_delivery_points(file_path):
    delivery_points = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            match = re.match(
                r"Delivery_(\d+)\s+\(Priority:\s+(\d+),\s+Weight:\s+([\d.]+)kg,\s+Pos:\s+\(([\d.]+),\s+([\d.]+)\)",
                line.strip()
            )
            if match:
                id_ = int(match.group(1))
                priority = int(match.group(2))
                weight = float(match.group(3))
                pos = (float(match.group(4)), float(match.group(5)))
                delivery_points.append({
                    'id': id_,
                    'priority': priority,
                    'weight': weight,
                    'pos': pos
                })
    return delivery_points

def build_delivery_graph(delivery_points):
    G = nx.DiGraph()
    for dp in delivery_points:
        G.add_node(dp['id'], pos=dp['pos'])

    for i in delivery_points:
        for j in delivery_points:
            if i['id'] != j['id']:
                dist = calculate_distance(i['pos'], j['pos'])
                cost = dist * i['weight'] + (i['priority'] * 100)
                G.add_edge(i['id'], j['id'], weight=cost)
    return G

def draw_graph(G):
    pos = nx.get_node_attributes(G, 'pos')
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=800, node_color='skyblue', arrowsize=20)
    
    edge_labels = nx.get_edge_attributes(G, 'weight')
    formatted_labels = {k: f"{v:.1f}" for k, v in edge_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_labels, font_size=8)

    plt.title("Teslimat Noktası Ağı")
    plt.show()

if __name__ == "__main__":
    file_path = "data.txt"
    delivery_points = parse_delivery_points(file_path)
    graph = build_delivery_graph(delivery_points)
    print("Graf oluşturuldu. Kenarlar ve maliyetleri:")
    for u, v, data in graph.edges(data=True):
        print(f"{u} -> {v}, weight: {data['weight']:.2f}")

    # Grafiği çiz
    draw_graph(graph)
