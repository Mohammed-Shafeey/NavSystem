import unittest
import os
import sys
import time
import logging
import numpy as np
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TestBluetoothIntegration')

# Import our modules
from navsystem.bluetooth_receiver import BluetoothReceiver, video_queue, audio_queue
from navsystem.video_processor import StellaVSLAMProcessor
from navsystem.audio_processor import AudioToTextConverter

# Import test utilities
from .test_config import BaseTestCase
from .test_utils import get_mock_video_frame, get_mock_audio_data

class TestBluetoothIntegration(BaseTestCase):
    """Test cases for the Bluetooth integration."""
    
    def test_bluetooth_receiver_initialization(self):
        """Test that the Bluetooth receiver can be initialized."""
        logger.info("Testing Bluetooth receiver initialization")
        
        receiver = BluetoothReceiver()
        self.assertIsNotNone(receiver)
        self.assertEqual(receiver.server_name, "NavSystem")
        self.assertFalse(receiver.running)
    
    def test_video_processor_initialization(self):
        """Test that the video processor can be initialized."""
        logger.info("Testing video processor initialization")
        
        processor = StellaVSLAMProcessor()
        self.assertIsNotNone(processor)
        self.assertFalse(processor.running)
    
    def test_audio_processor_initialization(self):
        """Test that the audio processor can be initialized."""
        logger.info("Testing audio processor initialization")
        
        processor = AudioToTextConverter()
        self.assertIsNotNone(processor)
        self.assertFalse(processor.running)
    
    def test_video_queue_functionality(self):
        """Test that the video queue works correctly."""
        logger.info("Testing video queue functionality")
        
        # Get a mock video frame
        test_frame = get_mock_video_frame(self.test_env['mock_data_dir'])
        
        # Put the frame in the queue
        video_queue.put(test_frame)
        
        # Check that the queue is not empty
        self.assertFalse(video_queue.empty())
        
        # Get the frame from the queue
        frame = video_queue.get()
        
        # Check that the frame is the same as the test frame
        self.assertEqual(frame.shape, test_frame.shape)
        self.assertTrue(np.array_equal(frame, test_frame))
    
    def test_audio_queue_functionality(self):
        """Test that the audio queue works correctly."""
        logger.info("Testing audio queue functionality")
        
        # Get mock audio data
        test_audio = get_mock_audio_data(self.test_env['mock_data_dir'])
        
        # Put the audio data in the queue
        audio_queue.put(test_audio)
        
        # Check that the queue is not empty
        self.assertFalse(audio_queue.empty())
        
        # Get the audio data from the queue
        audio_data = audio_queue.get()
        
        # Check that the audio data is the same as the test audio data
        self.assertEqual(audio_data, test_audio)
    
    def test_video_processor_with_queue(self):
        """Test that the video processor can process frames from the queue."""
        logger.info("Testing video processor with queue")
        
        # Initialize the processor
        processor = StellaVSLAMProcessor()
        
        # Start the processor
        processor.start_processing()
        
        # Get a mock video frame
        test_frame = get_mock_video_frame(self.test_env['mock_data_dir'])
        
        # Put the frame in the queue
        video_queue.put(test_frame)
        
        # Wait for the processor to process the frame
        time.sleep(0.5)
        
        # Check that the processor has updated its position data
        self.assertIsNotNone(processor.position_data)
        
        # Stop the processor
        processor.stop_processing()
    
    def test_audio_processor_with_queue(self):
        """Test that the audio processor can process audio data from the queue."""
        logger.info("Testing audio processor with queue")
        
        # Initialize the processor
        processor = AudioToTextConverter()
        
        # Start the processor
        processor.start_processing()
        
        # Get mock audio data
        test_audio = get_mock_audio_data(self.test_env['mock_data_dir'])
        
        # Put the audio data in the queue
        audio_queue.put(test_audio)
        
        # Wait for the processor to process the audio data
        time.sleep(0.5)
        
        # Stop the processor
        processor.stop_processing()
        
        # Note: We can't easily test the actual speech recognition without real audio data,
        # so we're just testing that the processor doesn't crash when given data.

if __name__ == "__main__":
    unittest.main()
