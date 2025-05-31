# data_structures.py
from shapely.geometry import Polygon
from utils import time_str_to_minutes
from dataclasses import dataclass
from typing import Tuple, List
import math
import numpy as np

@dataclass
class Drone:
    id: int
    max_weight: float
    battery_capacity: float
    speed: float
    start_pos: Tuple[float, float]
    consumption_rate: float = 1.0  # mAh per meter
    current_battery: float = 0.0
    current_time: float = 0.0

    def reset(self):
        """Reset drone state for a new simulation"""
        self.current_battery = self.battery_capacity
        self.current_time = 0.0

@dataclass
class DeliveryPoint:
    id: int
    pos: Tuple[float, float]
    weight: float
    priority: int
    time_window_start_str: str
    time_window_end_str: str

    def __post_init__(self):
        """Convert time window strings to minutes"""
        self.time_window_start = self._time_to_minutes(self.time_window_start_str)
        self.time_window_end = self._time_to_minutes(self.time_window_end_str)

    def _time_to_minutes(self, time_str: str) -> int:
        """Convert time string (HH:MM) to minutes since midnight"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def is_valid_time_window(self, time: float) -> bool:
        """Check if the given time is within the delivery time window"""
        return self.time_window_start <= time <= self.time_window_end

    @property
    def time_window_end_min(self) -> int:
        """Convert time string to minutes since midnight"""
        hours, minutes = map(int, self.time_window_end_str.split(':'))
        return hours * 60 + minutes

    def is_time_window_valid(self, arrival_time_minutes: float) -> bool:
        """Check if arrival time is within the delivery time window"""
        return self.time_window_start_min <= arrival_time_minutes <= self.time_window_end_min

@dataclass
class NoFlyZone:
    id: int
    active_start_str: str
    active_end_str: str
    coordinates: List[Tuple[float, float]]
    polygon = None  # Will be set when creating the polygon

    @property
    def active_start_min(self) -> int:
        """Convert time string to minutes since midnight"""
        hours, minutes = map(int, self.active_start_str.split(':'))
        return hours * 60 + minutes

    @property
    def active_end_min(self) -> int:
        """Convert time string to minutes since midnight"""
        hours, minutes = map(int, self.active_end_str.split(':'))
        return hours * 60 + minutes

    def is_active_at_time(self, time_minutes: float) -> bool:
        """Check if the no-fly zone is active at the given time"""
        return self.active_start_min <= time_minutes <= self.active_end_min

    def __repr__(self):
        start_t = self.active_start_min if self.active_start_min is not None else "N/A"
        end_t = self.active_end_min if self.active_end_min is not None else "N/A"
        return f"NFZ(id={self.id}, active=[{start_t}-{end_t}], area={self.polygon.area if self.polygon else 0})"

    def is_active(self, current_time_minutes):
        """Checks if the NFZ is active at the given time."""
        if self.active_start_min is None or self.active_end_min is None:
            return True # Always active if no time specified
        if self.polygon is None:
            return False # Invalid polygon definition
        return self.active_start_min <= current_time_minutes <= self.active_end_min