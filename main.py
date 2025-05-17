from graph import parse_delivery_points, build_delivery_graph, draw_graph
from ga import a_star  # a_star ayrı dosyadaysa
# ya da aynı dosyadaysa doğrudan kullanılabilir

if __name__ == "__main__":
    file_path = "data.txt"
    delivery_points = parse_delivery_points(file_path)
    graph = build_delivery_graph(delivery_points)
    draw_graph(graph)

    start = delivery_points[0]['id']
    goal = delivery_points[-1]['id']

    path = a_star(graph, start, goal)
    print("En kısa yol (A*):", path)
