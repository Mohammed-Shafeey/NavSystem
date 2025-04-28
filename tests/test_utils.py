import os
import sys
import time
import logging
import numpy as np
import cv2
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TestUtils')

def setup_test_environment():
    """
    Set up the test environment with mock data and configurations.
    
    Returns:
        dict: Test environment configuration
    """
    logger.info("Setting up test environment")
    
    # Create a test environment configuration
    test_env = {
        'mock_data_dir': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mock'),
        'temp_dir': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'temp'),
        'queues': {},
        'mocks': {}
    }
    
    # Create temporary directory if it doesn't exist
    os.makedirs(test_env['temp_dir'], exist_ok=True)
    
    # Create mock data directory if it doesn't exist
    os.makedirs(test_env['mock_data_dir'], exist_ok=True)
    
    # Create mock video frames if they don't exist
    create_mock_video_frames(test_env['mock_data_dir'])
    
    # Create mock audio data if it doesn't exist
    create_mock_audio_data(test_env['mock_data_dir'])
    
    return test_env

def teardown_test_environment(test_env):
    """
    Clean up the test environment.
    
    Args:
        test_env: Test environment configuration
    """
    logger.info("Cleaning up test environment")
    
    # Clean up temporary files
    for filename in os.listdir(test_env['temp_dir']):
        file_path = os.path.join(test_env['temp_dir'], filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")

def create_mock_video_frames(mock_data_dir):
    """
    Create mock video frames for testing.
    
    Args:
        mock_data_dir: Directory to store mock data
    """
    frames_dir = os.path.join(mock_data_dir, 'frames')
    os.makedirs(frames_dir, exist_ok=True)
    
    # Check if we already have mock frames
    if len([f for f in os.listdir(frames_dir) if f.endswith('.jpg')]) >= 5:
        logger.info("Mock video frames already exist")
        return
    
    logger.info("Creating mock video frames")
    
    # Create 5 test frames with different content
    for i in range(5):
        # Create a blank frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some content
        cv2.putText(frame, f"Test Frame {i+1}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 3)
        
        # Add some circles with different positions
        cv2.circle(frame, (200 + i*50, 200), 30, (0, 0, 255), -1)
        
        # Save the frame
        frame_path = os.path.join(frames_dir, f"frame_{i+1}.jpg")
        cv2.imwrite(frame_path, frame)
        
        # Also save an encoded version for testing Bluetooth data handling
        _, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        encoded_path = os.path.join(frames_dir, f"frame_{i+1}_encoded.bin")
        with open(encoded_path, 'wb') as f:
            f.write(encoded_frame.tobytes())
    
    logger.info(f"Created 5 mock video frames in {frames_dir}")

def create_mock_audio_data(mock_data_dir):
    """
    Create mock audio data for testing.
    
    Args:
        mock_data_dir: Directory to store mock data
    """
    audio_dir = os.path.join(mock_data_dir, 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    
    # Check if we already have mock audio data
    if len([f for f in os.listdir(audio_dir) if f.endswith('.bin')]) >= 3:
        logger.info("Mock audio data already exists")
        return
    
    logger.info("Creating mock audio data")
    
    # Create 3 mock audio samples (just binary data for testing)
    commands = [
        "navigate to library",
        "stop navigation",
        "where am I"
    ]
    
    for i, command in enumerate(commands):
        # Create a simple binary representation (not real audio, just for testing)
        # In a real implementation, you would use actual audio recordings
        mock_audio = command.encode('utf-8')
        
        # Save the mock audio data
        audio_path = os.path.join(audio_dir, f"command_{i+1}.bin")
        with open(audio_path, 'wb') as f:
            f.write(mock_audio)
        
        # Also save the text for reference
        text_path = os.path.join(audio_dir, f"command_{i+1}.txt")
        with open(text_path, 'w') as f:
            f.write(command)
    
    logger.info(f"Created 3 mock audio samples in {audio_dir}")

def get_mock_video_frame(mock_data_dir, index=1, encoded=False):
    """
    Get a mock video frame for testing.
    
    Args:
        mock_data_dir: Directory containing mock data
        index: Frame index (1-5)
        encoded: Whether to return the encoded frame
        
    Returns:
        numpy.ndarray or bytes: Video frame
    """
    frames_dir = os.path.join(mock_data_dir, 'frames')
    
    if encoded:
        frame_path = os.path.join(frames_dir, f"frame_{index}_encoded.bin")
        with open(frame_path, 'rb') as f:
            return f.read()
    else:
        frame_path = os.path.join(frames_dir, f"frame_{index}.jpg")
        return cv2.imread(frame_path)

def get_mock_audio_data(mock_data_dir, index=1):
    """
    Get mock audio data for testing.
    
    Args:
        mock_data_dir: Directory containing mock data
        index: Audio sample index (1-3)
        
    Returns:
        bytes: Audio data
    """
    audio_dir = os.path.join(mock_data_dir, 'audio')
    audio_path = os.path.join(audio_dir, f"command_{index}.bin")
    
    with open(audio_path, 'rb') as f:
        return f.read()

def get_mock_audio_text(mock_data_dir, index=1):
    """
    Get the text corresponding to mock audio data.
    
    Args:
        mock_data_dir: Directory containing mock data
        index: Audio sample index (1-3)
        
    Returns:
        str: Text corresponding to the audio data
    """
    audio_dir = os.path.join(mock_data_dir, 'audio')
    text_path = os.path.join(audio_dir, f"command_{index}.txt")
    
    with open(text_path, 'r') as f:
        return f.read()

class MockBluetoothReceiver:
    """Mock Bluetooth receiver for testing."""
    
    def __init__(self):
        self.server_name = "MockNavSystem"
        self.service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        self.server_sock = None
        self.client_socks = []
        self.running = False
        self.data_handlers = {
            'video': self._handle_video_data,
            'audio': self._handle_audio_data
        }
    
    def start_server(self):
        """Start the mock Bluetooth server."""
        self.running = True
        logger.info("Started mock Bluetooth server")
        return True
    
    def stop_server(self):
        """Stop the mock Bluetooth server."""
        self.running = False
        logger.info("Stopped mock Bluetooth server")
    
    def _handle_video_data(self, data):
        """Handle video data."""
        from navsystem.bluetooth_receiver import video_queue
        
        try:
            # Decode the video frame
            frame_data = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Put the frame in the video queue for processing
                video_queue.put(frame)
                logger.debug("Received mock video frame")
            else:
                logger.warning("Failed to decode mock video frame")
        except Exception as e:
            logger.error(f"Error handling mock video data: {e}")
    
    def _handle_audio_data(self, data):
        """Handle audio data."""
        from navsystem.bluetooth_receiver import audio_queue
        
        try:
            # Put the audio data in the audio queue for processing
            audio_queue.put(data)
            logger.debug("Received mock audio data")
        except Exception as e:
            logger.error(f"Error handling mock audio data: {e}")

class MockNavSystem:
    """Mock navigation system for testing."""
    
    def __init__(self):
        self.current_position = None
        self.current_orientation = None
        self.destination = None
        self.path = []
        self.is_navigating = False
    
    def set_current_position(self, position, orientation):
        """Set the current position and orientation."""
        self.current_position = position
        self.current_orientation = orientation
        logger.info(f"Mock navigation system position updated: {position}, {orientation}")
        return True
    
    def set_destination(self, destination_id):
        """Set the destination keyframe ID."""
        self.destination = destination_id
        logger.info(f"Mock navigation system destination set: {destination_id}")
        return True
    
    def calculate_path(self):
        """Calculate the path to the destination."""
        self.path = ["simulated_path_node_1", "simulated_path_node_2"]
        logger.info("Mock navigation system path calculated")
        return True
    
    def start_navigation(self):
        """Start navigation."""
        self.is_navigating = True
        logger.info("Mock navigation system started")
        return True
    
    def stop_navigation(self):
        """Stop navigation."""
        self.is_navigating = False
        logger.info("Mock navigation system stopped")
        return True
