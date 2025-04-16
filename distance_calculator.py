import numpy as np
import math

class DistanceCalculator:
    def __init__(self, distance_update_threshold=1.0):
        """
        Initialize the DistanceCalculator.
        
        Args:
            distance_update_threshold: Minimum distance change (meters) to trigger an update
        """
        self.distance_update_threshold = distance_update_threshold
        self.last_reported_distance = 0
    
    def calculate_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two 3D points.
        
        Args:
            point1: Tuple (x, y, z) coordinates
            point2: Tuple (x, y, z) coordinates
            
        Returns:
            float: Distance in meters
        """
        # Extract coordinates from points
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        
        # Calculate Euclidean distance
        return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
    
    def calculate_path_distance(self, positions):
        """
        Calculate the total distance along a path of positions.
        
        Args:
            positions: List of position tuples (x, y, z)
            
        Returns:
            float: Total path distance in meters
        """
        total_distance = 0
        
        for i in range(len(positions) - 1):
            total_distance += self.calculate_distance(positions[i], positions[i+1])
            
        return total_distance
    
    def calculate_distance_to_turn(self, current_position, path_positions, turn_indices):
        """
        Calculate distance from current position to the next turn.
        
        Args:
            current_position: Current position as (x, y, z)
            path_positions: List of position tuples (x, y, z) representing the path
            turn_indices: List of indices in the path where turns occur
            
        Returns:
            tuple: (distance_to_turn, turn_index) or (None, None) if no turns ahead
        """
        # Find the closest node in the path to the current position
        min_dist = float('inf')
        closest_node_idx = 0
        
        for i, position in enumerate(path_positions):
            dist = self.calculate_distance(current_position, position)
            if dist < min_dist:
                min_dist = dist
                closest_node_idx = i
        
        # Find the next turn after the closest node
        next_turn_idx = None
        for turn_idx in turn_indices:
            if turn_idx > closest_node_idx:
                next_turn_idx = turn_idx
                break
        
        if next_turn_idx is None:
            return None, None  # No turns ahead
        
        # Calculate distance from current position to the closest node
        distance = min_dist
        
        # Add distances between nodes from closest node to the turn
        for i in range(closest_node_idx, next_turn_idx):
            distance += self.calculate_distance(path_positions[i], path_positions[i+1])
        
        return distance, next_turn_idx
    
    def should_update_distance(self, new_distance):
        """
        Determine if a distance update should be reported based on threshold.
        
        Args:
            new_distance: Current calculated distance
            
        Returns:
            bool: True if update should be reported
        """
        if abs(new_distance - self.last_reported_distance) >= self.distance_update_threshold:
            self.last_reported_distance = new_distance
            return True
        return False
    
    def get_distance_description(self, distance):
        """
        Get a human-friendly description of a distance.
        
        Args:
            distance: Distance in meters
            
        Returns:
            str: Human-friendly distance description
        """
        if distance < 10:
            return f"{int(distance)} meters"
        elif distance < 100:
            # Round to nearest 5 meters
            rounded = round(distance / 5) * 5
            return f"{int(rounded)} meters"
        elif distance < 1000:
            # Round to nearest 10 meters
            rounded = round(distance / 10) * 10
            return f"{int(rounded)} meters"
        else:
            # Convert to kilometers for distances over 1000m
            km = distance / 1000
            return f"{km:.1f} kilometers"
