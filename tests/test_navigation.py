import unittest
import os
import sys
import time
import logging
import numpy as np
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TestNavigation')

# Import our modules
from navsystem.navigation_system import NavigationSystem
from navsystem.turn_recognition import TurnRecognizer
from navsystem.distance_calculator import DistanceCalculator

# Import test utilities
from .test_config import BaseTestCase
from .test_utils import MockNavSystem

class TestNavigation(BaseTestCase):
    """Test cases for the navigation system."""
    
    def setUp(self):
        """Set up before each test method."""
        super().setUp()
        
        # Set up paths to data files
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        self.keyframe_file = os.path.join(self.data_dir, 'keyframe_data.csv')
        
        # Initialize the navigation system with test data
        self.nav_system = NavigationSystem(keyframe_file=self.keyframe_file)
    
    def test_navigation_system_initialization(self):
        """Test that the navigation system can be initialized."""
        logger.info("Testing navigation system initialization")
        
        self.assertIsNotNone(self.nav_system)
        self.assertIsNotNone(self.nav_system.keyframe_data)
        self.assertIsNotNone(self.nav_system.graph)
    
    def test_turn_recognizer(self):
        """Test the turn recognizer component."""
        logger.info("Testing turn recognizer")
        
        turn_recognizer = TurnRecognizer()
        self.assertIsNotNone(turn_recognizer)
        
        # Test turn recognition with some sample orientations
        orientations = [0, 45, 90, 180, 270, 359]
        for i in range(len(orientations) - 1):
            turn = turn_recognizer.recognize_turn(orientations[i], orientations[i+1])
            self.assertIsNotNone(turn)
    
    def test_distance_calculator(self):
        """Test the distance calculator component."""
        logger.info("Testing distance calculator")
        
        distance_calculator = DistanceCalculator()
        self.assertIsNotNone(distance_calculator)
        
        # Test distance calculation with some sample positions
        pos1 = (0, 0, 0)
        pos2 = (3, 4, 0)
        distance = distance_calculator.calculate_distance(pos1, pos2)
        self.assertEqual(distance, 5.0)  # 3-4-5 triangle
    
    def test_path_finding(self):
        """Test the path finding functionality."""
        logger.info("Testing path finding")
        
        # Set current position to a known keyframe
        # For testing, we'll just use the first keyframe in the data
        first_keyframe_id = list(self.nav_system.keyframe_data.keys())[0]
        first_keyframe = self.nav_system.keyframe_data[first_keyframe_id]
        position = (first_keyframe['x'], first_keyframe['y'], first_keyframe['z'])
        orientation = first_keyframe['orientation']
        
        self.nav_system.set_current_position(position, orientation)
        
        # Set destination to another keyframe
        # For testing, we'll use the last keyframe in the data
        last_keyframe_id = list(self.nav_system.keyframe_data.keys())[-1]
        
        self.nav_system.set_destination(last_keyframe_id)
        
        # Calculate path
        path = self.nav_system.calculate_path()
        
        # Check that a path was found
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 0)
    
    def test_navigation_instructions(self):
        """Test generating navigation instructions."""
        logger.info("Testing navigation instructions")
        
        # Set up a simple path
        self.nav_system.path = ['keyframe_1', 'keyframe_2', 'keyframe_3']
        self.nav_system.current_path_index = 0
        
        # Get the next instruction
        instruction = self.nav_system.get_next_instruction()
        
        # Check that an instruction was generated
        self.assertIsNotNone(instruction)

if __name__ == "__main__":
    unittest.main()
