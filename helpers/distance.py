import math

#mesafe
def calculate_distance(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)


#maliyet
def calculate_cost(distance, weight, priority):
    base_cost = distance * 0.1 
    penalty = weight * 0.5  
    priority_penalty = (5 - priority) * 2  
    return base_cost + penalty + priority_penalty

