import heapq
from graph import calculate_distance


def a_star(graph, start_id, goal_id):
    open_set = []
    heapq.heappush(open_set, (0, start_id))
    
    came_from = {}
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start_id] = 0

    def heuristic(n1, n2):
        pos1 = graph.nodes[n1]['pos']
        pos2 = graph.nodes[n2]['pos']
        return calculate_distance(pos1, pos2)

    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current == goal_id:
            # Rota bulundu, geri sar
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]  # Baştan sona döndür

        for neighbor in graph.successors(current):
            tentative_g = g_score[current] + graph[current][neighbor]['weight']
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal_id)
                heapq.heappush(open_set, (f_score, neighbor))

    return None  # Yol yok
