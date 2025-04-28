import unittest
import os
import sys
import time
import logging
import numpy as np
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TestConfig')

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# Import test utilities
from test_utils import setup_test_environment, teardown_test_environment

class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown methods."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for the whole test case."""
        logger.info(f"Setting up test environment for {cls.__name__}")
        cls.test_env = setup_test_environment()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in the test case."""
        logger.info(f"Cleaning up test environment for {cls.__name__}")
        teardown_test_environment(cls.test_env)
    
    def setUp(self):
        """Set up before each test method."""
        logger.info(f"Setting up test: {self._testMethodName}")
        
        # Clear any queues
        from navsystem.bluetooth_receiver import video_queue, audio_queue
        while not video_queue.empty():
            video_queue.get()
        
        while not audio_queue.empty():
            audio_queue.get()
    
    def tearDown(self):
        """Clean up after each test method."""
        logger.info(f"Cleaning up test: {self._testMethodName}")
