import numpy as np
from turn_recognition import TurnRecognizer
from distance_calculator import DistanceCalculator
from tts_system import TTSSystem
from data_setup import load_keyframes, build_graph, find_nearest_keyframe
from path_finding import PathFinder
import time
import threading

class NavigationSystem:
    def __init__(self, keyframe_file="keyframe_data.csv", distance_threshold=3.0):
        """
        Initialize the complete navigation system.
        
        Args:
            keyframe_file: Path to the keyframe data CSV file
            distance_threshold: Threshold for building the navigation graph
        """
        # Load keyframe data and build graph
        self.keyframe_data = load_keyframes(keyframe_file)
        self.graph = build_graph(self.keyframe_data, distance_threshold)
        
        # Initialize pathfinder
        self.path_finder = PathFinder(self.keyframe_data, self.graph)
        
        # Initialize components
        self.turn_recognizer = TurnRecognizer()
        self.distance_calculator = DistanceCalculator()
        self.tts_system = TTSSystem()
        
        # Navigation state
        self.current_position = None
        self.current_orientation = None
        self.destination = None
        self.current_path_ids = []  # List of keyframe IDs
        self.path_positions = {}    # Dictionary mapping keyframe IDs to positions
        self.path_orientations = {} # Dictionary mapping keyframe IDs to orientations
        self.turn_indices = []      # Indices in the path where turns occur
        
        # Control flags
        self.is_navigating = False
        self.navigation_thread = None
    
    def set_current_position(self, position, orientation):
        """
        Update the current position and orientation.
        
        Args:
            position: Tuple (x, y, z) of current position
            orientation: Current orientation in degrees
        """
        self.current_position = position
        self.current_orientation = orientation
    
    def set_destination(self, destination_id):
        """
        Set the destination keyframe.
        
        Args:
            destination_id: ID of the destination keyframe
            
        Returns:
            bool: True if destination is valid and path is found
        """
        if destination_id not in self.keyframe_data:
            print(f"Error: Destination keyframe {destination_id} not found")
            return False
        
        self.destination = destination_id
        return True
    
    def calculate_path(self):
        """
        Calculate the path from current position to destination.
        
        Returns:
            bool: True if path is found
        """
        if self.current_position is None:
            print("Error: Current position not set")
            return False
        
        if self.destination is None:
            print("Error: Destination not set")
            return False
        
        # Find nearest keyframe to current position
        start_id, _ = find_nearest_keyframe(self.current_position, self.keyframe_data)
        
        # Calculate path using A* algorithm - returns list of keyframe IDs
        path_ids = self.path_finder.astar(start_id, self.destination)
        
        if path_ids is None:
            print("Error: No path found to destination")
            return False
        
        # Store the keyframe IDs
        self.current_path_ids = path_ids
        
        # Clear previous path data
        self.path_positions = {}
        self.path_orientations = {}
        
        # Convert keyframe IDs to positions and store in dictionary
        for kf_id in path_ids:
            self.path_positions[kf_id] = self.keyframe_data[kf_id]
        
        # In a real implementation, orientation would come from SLAM data
        # For now, calculate orientations based on path direction
        self._calculate_orientations()
        
        # Analyze path for turns
        self.analyze_path_turns()
        
        return True
    
    def _calculate_orientations(self):
        """
        Calculate orientations based on path direction.
        
        In a production environment, this would be replaced with orientation data from SLAM.
        """
        # Get ordered list of positions based on path IDs
        positions = [self.path_positions[kf_id] for kf_id in self.current_path_ids]
        
        for i, kf_id in enumerate(self.current_path_ids):
            if i == 0:
                # First node orientation is based on direction to second node
                if len(positions) > 1:
                    dx = positions[1][0] - positions[0][0]
                    dy = positions[1][1] - positions[0][1]
                    orientation = np.degrees(np.arctan2(dy, dx))
                else:
                    orientation = 0  # Default if only one position
            elif i == len(positions) - 1:
                # Last node orientation is same as second-to-last
                orientation = self.path_orientations[self.current_path_ids[i-1]]
            else:
                # Middle nodes orientation is based on direction from previous to next
                dx = positions[i+1][0] - positions[i-1][0]
                dy = positions[i+1][1] - positions[i-1][1]
                orientation = np.degrees(np.arctan2(dy, dx))
            
            self.path_orientations[kf_id] = orientation
    
    def analyze_path_turns(self):
        """Analyze the current path to identify turns."""
        # Get ordered list of positions and orientations based on path IDs
        positions = [self.path_positions[kf_id] for kf_id in self.current_path_ids]
        orientations = [self.path_orientations[kf_id] for kf_id in self.current_path_ids]
        
        # Get turn information from the turn recognizer
        turn_info = self.turn_recognizer.analyze_path(positions, orientations)
        
        # Extract turn indices
        self.turn_indices = [info[0] for info in turn_info]
        
        # Print turn information for debugging
        for idx, direction, turn_type, angle in turn_info:
            kf_id = self.current_path_ids[idx]
            print(f"Turn at node {idx} (keyframe {kf_id}): {direction.value} {turn_type.value} ({angle:.1f} degrees)")
    
    def start_navigation(self):
        """Start the navigation process."""
        if self.is_navigating:
            print("Navigation already in progress")
            return
        
        if not self.current_path_ids:
            print("No path calculated. Call calculate_path() first.")
            return
        
        # Start TTS system
        self.tts_system.start()
        
        # Welcome message
        self.tts_system.speak("Starting navigation. Please follow the instructions.", 
                             self.tts_system.PRIORITY_HIGH)
        
        # Set navigation flag
        self.is_navigating = True
        
        # Start navigation thread
        self.navigation_thread = threading.Thread(target=self._navigation_loop)
        self.navigation_thread.daemon = True
        self.navigation_thread.start()
    
    def stop_navigation(self):
        """Stop the navigation process."""
        if not self.is_navigating:
            return
        
        # Clear navigation flag
        self.is_navigating = False
        
        # Wait for navigation thread to end
        if self.navigation_thread:
            self.navigation_thread.join(timeout=1.0)
        
        # Stop TTS system
        self.tts_system.speak("Navigation stopped.", self.tts_system.PRIORITY_HIGH)
        self.tts_system.stop()
    
    def update_position_from_slam(self):
        """
        Update position and orientation from SLAM system.
        In a real implementation, this would call get_latest_position() from Recieve_pos_data.py
        and parse the returned data.
        """
        
        from Recieve_pos_data import get_latest_position
        data = get_latest_position()
        parts = data.split(',')
        if len(parts) >= 4:
            x, y, z, orientation = float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])
            self.set_current_position((x, y, z), orientation)
    
    def _navigation_loop(self):
        """Main navigation loop that runs in a separate thread."""
        last_turn_announcement = -1
        last_distance_update = time.time() - 10  # Ensure immediate first update
        
        while self.is_navigating:
            try:
                # In production, update position from SLAM
                # self.update_position_from_slam()
                
                # Check if we've reached the destination
                if self._check_destination_reached():
                    self.tts_system.speak(self.tts_system.announce_arrival(), 
                                         self.tts_system.PRIORITY_HIGH)
                    self.is_navigating = False
                    break
                
                # Get current time
                current_time = time.time()
                
                # Get ordered list of positions for distance calculations
                positions = [self.path_positions[kf_id] for kf_id in self.current_path_ids]
                
                # Check for upcoming turns
                distance_to_turn, turn_idx = self.distance_calculator.calculate_distance_to_turn(
                    self.current_position, positions, self.turn_indices)
                
                # Announce turns when approaching
                if distance_to_turn is not None and turn_idx != last_turn_announcement:
                    # Get ordered list of positions and orientations for turn recognition
                    orientations = [self.path_orientations[kf_id] for kf_id in self.current_path_ids]
                    
                    # Find turn information
                    turn_info = None
                    for info in self.turn_recognizer.analyze_path(positions, orientations):
                        if info[0] == turn_idx:
                            turn_info = info
                            break
                    
                    if turn_info:
                        _, direction, turn_type, _ = turn_info
                        
                        # Generate distance description
                        distance_str = self.distance_calculator.get_distance_description(distance_to_turn)
                        
                        # Generate and speak turn instruction
                        instruction = self.tts_system.generate_turn_instruction(
                            direction.value, turn_type.value, distance_str)
                        
                        self.tts_system.speak(instruction, self.tts_system.PRIORITY_MEDIUM)
                        
                        # Remember this turn was announced
                        last_turn_announcement = turn_idx
                
                # Provide regular distance updates (every 10 seconds)
                if current_time - last_distance_update >= 10:
                    # Calculate remaining distance to destination
                    remaining_distance = self._calculate_remaining_distance()
                    
                    if remaining_distance is not None:
                        # Generate distance description
                        distance_str = self.distance_calculator.get_distance_description(remaining_distance)
                        
                        # Generate and speak distance update
                        update = self.tts_system.generate_distance_update(distance_str)
                        self.tts_system.speak(update, self.tts_system.PRIORITY_LOW)
                        
                        # Update last distance update time
                        last_distance_update = current_time
                
                # Sleep to avoid high CPU usage
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error in navigation loop: {e}")
                time.sleep(1)  # Sleep on error to avoid rapid error loops
    
    def _check_destination_reached(self):
        """
        Check if the destination has been reached.
        
        Returns:
            bool: True if destination reached
        """
        if not self.current_path_ids:
            return False
        
        # Get destination position (last keyframe in path)
        destination_id = self.current_path_ids[-1]
        destination_position = self.path_positions[destination_id]
        
        # Calculate distance to destination
        distance = self.distance_calculator.calculate_distance(
            self.current_position, destination_position)
        
        # Consider destination reached if within 2 meters
        return distance < 2.0
    
    def _calculate_remaining_distance(self):
        """
        Calculate the remaining distance to the destination.
        
        Returns:
            float: Remaining distance in meters or None if not available
        """
        if not self.current_path_ids:
            return None
        
        # Get ordered list of positions for distance calculations
        positions = [self.path_positions[kf_id] for kf_id in self.current_path_ids]
        
        # Find the closest node in the path to the current position
        min_dist = float('inf')
        closest_node_idx = 0
        
        for i, position in enumerate(positions):
            dist = self.distance_calculator.calculate_distance(
                self.current_position, position)
            if dist < min_dist:
                min_dist = dist
                closest_node_idx = i
        
        # Calculate distance from current position to the closest node
        remaining_distance = min_dist
        
        # Add distances between nodes from closest node to the end
        for i in range(closest_node_idx, len(positions) - 1):
            remaining_distance += self.distance_calculator.calculate_distance(
                positions[i], positions[i+1])
        
        return remaining_distance
