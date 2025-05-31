# data_loader.py
from model.data_structures import Drone, DeliveryPoint, NoFlyZone
from config import DEFAULT_CONSUMPTION_RATE_MAH_PER_METER # config.py'den import
import ast
from shapely.geometry import Polygon

def load_data(filename: str):
    """
    Load scenario data from a Python file containing dictionaries
    Returns: (drones, deliveries, no_fly_zones)
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
            
        # Parse the Python dictionaries
        data = ast.literal_eval(content)
        
        # Convert dictionaries to objects
        drones = []
        for drone_dict in data['drones']:
            drone = Drone(
                id=drone_dict['id'],
                max_weight=drone_dict['max_weight'],
                battery_capacity=drone_dict['battery'],
                speed=drone_dict['speed'],
                start_pos=drone_dict['start_pos']
            )
            drones.append(drone)

        deliveries = []
        for delivery_dict in data['deliveries']:
            # Convert time window tuple to strings
            start_time = f"{delivery_dict['time_window'][0] // 60:02d}:{delivery_dict['time_window'][0] % 60:02d}"
            end_time = f"{delivery_dict['time_window'][1] // 60:02d}:{delivery_dict['time_window'][1] % 60:02d}"
            
            delivery = DeliveryPoint(
                id=delivery_dict['id'],
                pos=delivery_dict['pos'],
                weight=delivery_dict['weight'],
                priority=delivery_dict['priority'],
                time_window_start_str=start_time,
                time_window_end_str=end_time
            )
            deliveries.append(delivery)

        no_fly_zones = []
        for nfz_dict in data['no_fly_zones']:
            # Convert active time tuple to strings
            start_time = f"{nfz_dict['active_time'][0] // 60:02d}:{nfz_dict['active_time'][0] % 60:02d}"
            end_time = f"{nfz_dict['active_time'][1] // 60:02d}:{nfz_dict['active_time'][1] % 60:02d}"
            
            nfz = NoFlyZone(
                id=nfz_dict['id'],
                active_start_str=start_time,
                active_end_str=end_time,
                coordinates=nfz_dict['coordinates']
            )
            # Create polygon from coordinates
            nfz.polygon = Polygon(nfz.coordinates) if len(nfz.coordinates) >= 3 else None
            no_fly_zones.append(nfz)

        return drones, deliveries, no_fly_zones

    except Exception as e:
        print(f"Error loading data from {filename}: {e}")
        return [], [], []