import os
import sys
import time
import logging
import numpy as np
import cv2
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RunTests')

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import test utilities
from tests.test_utils import setup_test_environment, teardown_test_environment
from tests.test_utils import get_mock_video_frame, get_mock_audio_data, MockNavSystem

def run_tests():
    """Run all tests and validate system functionality."""
    logger.info("Running all tests to validate system functionality")
    
    # Set up test environment
    test_env = setup_test_environment()
    
    try:
        # Import our modules
        from navsystem.bluetooth_receiver import BluetoothReceiver, video_queue, audio_queue
        from navsystem.video_processor import StellaVSLAMProcessor
        from navsystem.audio_processor import AudioToTextConverter
        from navsystem.navigation_system import NavigationSystem
        
        # Initialize components
        receiver = BluetoothReceiver()
        video_processor = StellaVSLAMProcessor()
        audio_processor = AudioToTextConverter()
        nav_system = MockNavSystem()
        
        logger.info("All components initialized successfully")
        
        # Test Bluetooth receiver
        logger.info("Testing Bluetooth receiver initialization")
        assert receiver.server_name == "NavSystem", "Bluetooth receiver name mismatch"
        assert not receiver.running, "Bluetooth receiver should not be running initially"
        
        # Test video processor
        logger.info("Testing video processor initialization")
        assert not video_processor.running, "Video processor should not be running initially"
        
        # Test audio processor
        logger.info("Testing audio processor initialization")
        assert not audio_processor.running, "Audio processor should not be running initially"
        
        # Test video queue functionality
        logger.info("Testing video queue functionality")
        test_frame = get_mock_video_frame(test_env['mock_data_dir'])
        video_queue.put(test_frame)
        assert not video_queue.empty(), "Video queue should not be empty after putting a frame"
        frame = video_queue.get()
        assert frame.shape == test_frame.shape, "Frame shape mismatch"
        
        # Test audio queue functionality
        logger.info("Testing audio queue functionality")
        test_audio = get_mock_audio_data(test_env['mock_data_dir'])
        audio_queue.put(test_audio)
        assert not audio_queue.empty(), "Audio queue should not be empty after putting audio data"
        audio_data = audio_queue.get()
        assert audio_data == test_audio, "Audio data mismatch"
        
        # Test video processor with queue
        logger.info("Testing video processor with queue")
        video_processor.start_processing()
        video_queue.put(test_frame)
        time.sleep(0.5)
        assert video_processor.position_data is not None, "Video processor should update position data"
        video_processor.stop_processing()
        
        # Test audio processor with queue
        logger.info("Testing audio processor with queue")
        audio_processor.start_processing()
        audio_queue.put(test_audio)
        time.sleep(0.5)
        audio_processor.stop_processing()
        
        # Test full integration
        logger.info("Testing full integration with simulated data")
        video_processor.start_processing()
        audio_processor.start_processing()
        
        # Simulate receiving video data
        for i in range(1, 4):
            test_frame = get_mock_video_frame(test_env['mock_data_dir'], index=min(i, 5))
            video_queue.put(test_frame)
            time.sleep(0.2)
        
        # Check that the video processor has updated its position data
        assert video_processor.position_data is not None, "Video processor should update position data"
        
        # Simulate integration with navigation system
        if video_processor.position_data:
            position = (
                video_processor.position_data['x'],
                video_processor.position_data['y'],
                video_processor.position_data['z']
            )
            orientation = video_processor.position_data['orientation']
            
            # Update the navigation system
            nav_system.set_current_position(position, orientation)
            
            # Check that the navigation system has been updated
            assert nav_system.current_position == position, "Navigation system position mismatch"
            assert nav_system.current_orientation == orientation, "Navigation system orientation mismatch"
        
        # Simulate receiving audio data
        test_audio = get_mock_audio_data(test_env['mock_data_dir'], index=1)
        audio_queue.put(test_audio)
        time.sleep(0.5)
        
        # Stop the components
        video_processor.stop_processing()
        audio_processor.stop_processing()
        
        logger.info("All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during tests: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up test environment
        teardown_test_environment(test_env)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
