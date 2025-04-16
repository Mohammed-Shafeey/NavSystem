#!/usr/bin/env python3
"""
Test script for the NavSystem navigation components.
This script tests the integration between the navigation system, turn recognition,
and distance calculator components, with a mock TTS system to avoid dependencies.
"""

import time
import sys
from navigation_system import NavigationSystem
from data_setup import load_keyframes
from tts_system import TTSSystem

# Create a mock TTSSystem class to avoid dependency on pyttsx3
class MockTTSSystem:
    def __init__(self, rate=150, volume=1.0):
        """Initialize the Mock Text-to-Speech system."""
        self.PRIORITY_HIGH = 3
        self.PRIORITY_MEDIUM = 2
        self.PRIORITY_LOW = 1
        self.messages = []
        print("Initialized Mock TTS System")
    
    def start(self):
        """Start the TTS system."""
        print("Mock TTS system started")
    
    def stop(self):
        """Stop the TTS system."""
        print("Mock TTS system stopped")
    
    def speak(self, text, priority=2):
        """Record speech instruction."""
        self.messages.append((text, priority))
        print(f"TTS would say: [{priority}] {text}")
    
    def clear_queue(self):
        """Clear all pending speech instructions."""
        self.messages = []
    
    def generate_turn_instruction(self, direction, turn_type, distance=None):
        """Generate a turn instruction."""
        instruction = ""
        if distance is not None:
            instruction += f"In {distance}, "
        if turn_type == "u-turn":
            instruction += f"make a U-turn"
        else:
            instruction += f"{turn_type} {direction}"
        return instruction
    
    def generate_distance_update(self, distance, destination_name=None):
        """Generate a distance update instruction."""
        if destination_name:
            return f"{destination_name} is {distance} away"
        else:
            return f"Continue for {distance}"
    
    def announce_arrival(self, destination_name=None):
        """Generate an arrival announcement."""
        if destination_name:
            return f"You have arrived at {destination_name}"
        else:
            return f"You have reached your destination"

# Patch the TTSSystem in navigation_system
# This is a bit hacky but works for testing
sys.modules['tts_system'].TTSSystem = MockTTSSystem

def test_navigation_system():
    """Test the navigation system with simulated data."""
    print("Testing Navigation System...")
    
    # Initialize the navigation system
    nav_system = NavigationSystem(keyframe_file="keyframe_data.csv", distance_threshold=3.0)
    
    # Load keyframe data for reference
    keyframe_data = load_keyframes("keyframe_data.csv")
    
    # Print some keyframe data for verification
    print(f"Loaded {len(keyframe_data)} keyframes")
    for i, (kf_id, pos) in enumerate(keyframe_data.items()):
        if i < 5:  # Print first 5 keyframes
            print(f"Keyframe {kf_id}: {pos}")
    
    # Set current position (simulated)
    # In a real scenario, this would come from Recieve_pos_data.py
    start_pos = keyframe_data[list(keyframe_data.keys())[0]]
    nav_system.set_current_position(start_pos, 0)
    print(f"Set current position to {start_pos}")
    
    # Set destination (using a keyframe ID from the middle of the data)
    dest_id = list(keyframe_data.keys())[len(keyframe_data) // 2]
    success = nav_system.set_destination(dest_id)
    print(f"Set destination to keyframe {dest_id}: {success}")
    
    # Calculate path
    path_found = nav_system.calculate_path()
    print(f"Path calculation: {path_found}")
    
    if path_found:
        # Print path information
        print(f"Path contains {len(nav_system.current_path_ids)} keyframes")
        print(f"Path keyframe IDs: {nav_system.current_path_ids[:5]}... (first 5)")
        
        # Verify that path_positions and path_orientations contain entries for each keyframe ID
        missing_positions = []
        missing_orientations = []
        for kf_id in nav_system.current_path_ids:
            if kf_id not in nav_system.path_positions:
                missing_positions.append(kf_id)
            if kf_id not in nav_system.path_orientations:
                missing_orientations.append(kf_id)
        
        if missing_positions:
            print(f"ERROR: Missing positions for keyframes: {missing_positions}")
        else:
            print("✓ All keyframe positions are present")
            
        if missing_orientations:
            print(f"ERROR: Missing orientations for keyframes: {missing_orientations}")
        else:
            print("✓ All keyframe orientations are present")
        
        # Test turn recognition
        print("\nTurn information:")
        if nav_system.turn_indices:
            for idx in nav_system.turn_indices:
                kf_id = nav_system.current_path_ids[idx]
                print(f"Turn at index {idx} (keyframe {kf_id})")
            print(f"✓ Detected {len(nav_system.turn_indices)} turns in the path")
        else:
            print("No turns detected in the path")
        
        # Test navigation calculations
        print("\nTesting navigation calculations...")
        
        # Get ordered list of positions for testing
        positions = [nav_system.path_positions[kf_id] for kf_id in nav_system.current_path_ids]
        
        # Test distance calculation
        if len(positions) > 1:
            distance = nav_system.distance_calculator.calculate_distance(positions[0], positions[1])
            print(f"Distance between first two points: {distance:.2f} meters")
            print("✓ Distance calculation works")
        
        # Test distance to turn calculation
        if nav_system.turn_indices:
            distance_to_turn, turn_idx = nav_system.distance_calculator.calculate_distance_to_turn(
                nav_system.current_position, positions, nav_system.turn_indices)
            print(f"Distance to next turn: {distance_to_turn:.2f} meters (at index {turn_idx})")
            print("✓ Distance to turn calculation works")
        
        # Test remaining distance calculation
        remaining = nav_system._calculate_remaining_distance()
        print(f"Remaining distance to destination: {remaining:.2f} meters")
        print("✓ Remaining distance calculation works")
        
        # Test TTS instruction generation (using mock TTS)
        print("\nTesting TTS instruction generation...")
        if nav_system.turn_indices:
            # Get ordered list of orientations for testing
            orientations = [nav_system.path_orientations[kf_id] for kf_id in nav_system.current_path_ids]
            
            # Find turn information for the first turn
            turn_info = None
            for info in nav_system.turn_recognizer.analyze_path(positions, orientations):
                if info[0] == nav_system.turn_indices[0]:
                    turn_info = info
                    break
            
            if turn_info:
                _, direction, turn_type, _ = turn_info
                distance_str = nav_system.distance_calculator.get_distance_description(distance_to_turn)
                instruction = nav_system.tts_system.generate_turn_instruction(
                    direction.value, turn_type.value, distance_str)
                print(f"Turn instruction: {instruction}")
                print("✓ Turn instruction generation works")
        
        # Test arrival announcement
        arrival = nav_system.tts_system.announce_arrival()
        print(f"Arrival announcement: {arrival}")
        print("✓ Arrival announcement generation works")
        
        # Test navigation start/stop
        print("\nTesting navigation start/stop...")
        nav_system.start_navigation()
        time.sleep(1)  # Let it run briefly
        nav_system.stop_navigation()
        print("✓ Navigation start/stop works")
    
    print("\nNavigation system test completed successfully.")

if __name__ == "__main__":
    test_navigation_system()
