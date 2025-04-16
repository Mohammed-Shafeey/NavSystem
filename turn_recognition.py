import numpy as np
import math
from enum import Enum

class TurnDirection(Enum):
    LEFT = "left"
    RIGHT = "right"
    STRAIGHT = "straight"

class TurnType(Enum):
    SLIGHT = "slight"
    NORMAL = "normal"
    SHARP = "sharp"
    UTURN = "u-turn"
    NONE = "none"

class TurnRecognizer:
    def __init__(self, 
                 slight_turn_threshold=15, 
                 normal_turn_threshold=45, 
                 sharp_turn_threshold=90,
                 uturn_threshold=150):
        """
        Initialize the TurnRecognizer with configurable thresholds.
        
        Args:
            slight_turn_threshold: Minimum angle (degrees) to classify as a slight turn
            normal_turn_threshold: Minimum angle (degrees) to classify as a normal turn
            sharp_turn_threshold: Minimum angle (degrees) to classify as a sharp turn
            uturn_threshold: Minimum angle (degrees) to classify as a U-turn
        """
        self.slight_turn_threshold = slight_turn_threshold
        self.normal_turn_threshold = normal_turn_threshold
        self.sharp_turn_threshold = sharp_turn_threshold
        self.uturn_threshold = uturn_threshold
    
    def normalize_angle(self, angle):
        """Normalize angle to be between -180 and 180 degrees"""
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle
    
    def detect_turn(self, prev_orientation, current_orientation):
        """
        Detect turn based on orientation change.
        
        Args:
            prev_orientation: Previous orientation in degrees
            current_orientation: Current orientation in degrees
            
        Returns:
            tuple: (TurnDirection, TurnType, angle_diff)
        """
        # Calculate the difference in orientation
        angle_diff = self.normalize_angle(current_orientation - prev_orientation)
        
        # Determine turn direction
        if abs(angle_diff) < self.slight_turn_threshold:
            direction = TurnDirection.STRAIGHT
            turn_type = TurnType.NONE
        elif angle_diff > 0:
            direction = TurnDirection.RIGHT
        else:
            direction = TurnDirection.LEFT
        
        # Determine turn type based on the absolute angle difference
        abs_diff = abs(angle_diff)
        if direction == TurnDirection.STRAIGHT:
            turn_type = TurnType.NONE
        elif abs_diff >= self.uturn_threshold:
            turn_type = TurnType.UTURN
        elif abs_diff >= self.sharp_turn_threshold:
            turn_type = TurnType.SHARP
        elif abs_diff >= self.normal_turn_threshold:
            turn_type = TurnType.NORMAL
        elif abs_diff >= self.slight_turn_threshold:
            turn_type = TurnType.SLIGHT
        else:
            turn_type = TurnType.NONE
            direction = TurnDirection.STRAIGHT
        
        return (direction, turn_type, abs_diff)
    
    def analyze_path(self, path_positions, orientations=None):
        """
        Analyze a path of positions to detect turns.
        
        Args:
            path_positions: List of position tuples (x, y, z)
            orientations: List of orientation values in degrees (optional)
            
        Returns:
            list: List of tuples (node_index, TurnDirection, TurnType, angle)
        """
        turns = []
        
        # Need at least 3 nodes to detect a turn (previous, current, next)
        if len(path_positions) < 3:
            return turns
        
        # If orientations are not provided, calculate them based on path direction
        if orientations is None:
            orientations = self._calculate_orientations(path_positions)
        
        # Analyze each node except first and last
        for i in range(1, len(path_positions)-1):
            prev_orientation = orientations[i-1]
            current_orientation = orientations[i]
            next_orientation = orientations[i+1]
            
            # Calculate orientation changes
            prev_to_current = self.detect_turn(prev_orientation, current_orientation)
            current_to_next = self.detect_turn(current_orientation, next_orientation)
            
            # If both segments indicate a turn in the same direction, it's a turn at the current node
            if (prev_to_current[0] == current_to_next[0] and 
                prev_to_current[0] != TurnDirection.STRAIGHT):
                
                # Use the more significant turn type
                if prev_to_current[1].value > current_to_next[1].value:
                    turn_type = prev_to_current[1]
                    angle = prev_to_current[2]
                else:
                    turn_type = current_to_next[1]
                    angle = current_to_next[2]
                
                turns.append((i, prev_to_current[0], turn_type, angle))
        
        return turns
    
    def _calculate_orientations(self, positions):
        """
        Calculate orientations based on path direction.
        
        Args:
            positions: List of position tuples (x, y, z)
            
        Returns:
            list: List of orientation values in degrees
        """
        orientations = []
        
        for i in range(len(positions)):
            if i == 0:
                # First node orientation is based on direction to second node
                dx = positions[1][0] - positions[0][0]
                dy = positions[1][1] - positions[0][1]
                orientation = np.degrees(np.arctan2(dy, dx))
            elif i == len(positions) - 1:
                # Last node orientation is same as second-to-last
                orientation = orientations[-1]
            else:
                # Middle nodes orientation is based on direction from previous to next
                dx = positions[i+1][0] - positions[i-1][0]
                dy = positions[i+1][1] - positions[i-1][1]
                orientation = np.degrees(np.arctan2(dy, dx))
            
            orientations.append(orientation)
        
        return orientations
