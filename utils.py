# utils.py
import math
from datetime import datetime, timedelta
from shapely.geometry import Point, LineString, Polygon

def time_str_to_minutes(time_str):
    """Converts HH:MM string to minutes since midnight."""
    if not time_str or ':' not in time_str:
        return None # Or raise error
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    except ValueError:
        return None # Or raise error

def minutes_to_time_str(minutes):
    """Converts minutes since midnight to HH:MM string."""
    if minutes is None:
        return "N/A"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02d}:{mins:02d}"

def calculate_distance(pos1, pos2):
    """Calculates Euclidean distance between two (x, y) points."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def check_nfz_intersection(point1, point2, no_fly_zones, current_time_minutes):
    """Checks if the path segment between point1 and point2 intersects any active NFZ."""
    path_segment = LineString([point1, point2])
    for nfz in no_fly_zones:
        if nfz.is_active(current_time_minutes):
            if path_segment.intersects(nfz.polygon):
                return True # Intersects an active NFZ
    return False # No intersection with active NFZs

def estimate_segment_time_seconds(distance, speed_mps):
    """Estimates time in seconds to travel a distance at a given speed."""
    if speed_mps <= 0:
        return float('inf')
    return distance / speed_mps

def estimate_segment_energy(distance, consumption_rate_mah_per_meter):
    """Estimates energy consumption in mAh for a distance."""
    return distance * consumption_rate_mah_per_meter