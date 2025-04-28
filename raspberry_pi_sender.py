#!/usr/bin/env python3
import bluetooth as bt
import cv2
import numpy as np
import time
import threading
import argparse
import os
import logging
import pyaudio
import wave
import struct
from queue import Queue

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RaspberryPiSender')

class BluetoothSender:
    """
    Class to send video and audio data from Raspberry Pi to the NavSystem via Bluetooth.
    """
    def __init__(self, server_mac=None, port=1, service_uuid="94f39d29-7d6d-437d-973b-fba39e49d4ee"):
        """
        Initialize the Bluetooth sender.
        
        Args:
            server_mac: MAC address of the server to connect to
            port: RFCOMM port to connect to
            service_uuid: UUID of the service to connect to
        """
        self.server_mac = server_mac
        self.port = port
        self.service_uuid = service_uuid
        self.client_sock = None
        self.connected = False
        self.running = False
        
        # Queues for video and audio data
        self.video_queue = Queue()
        self.audio_queue = Queue()
        
        logger.info("BluetoothSender initialized")
    
    def discover_server(self):
        """
        Discover available Bluetooth servers.
        
        Returns:
            list: List of discovered devices
        """
        logger.info("Discovering Bluetooth devices...")
        nearby_devices = bt.discover_devices(lookup_names=True)
        logger.info(f"Found {len(nearby_devices)} devices")
        
        for addr, name in nearby_devices:
            logger.info(f"  {addr} - {name}")
        
        return nearby_devices
    
    def find_service(self):
        """
        Find the NavSystem service on available devices.
        
        Returns:
            tuple: (server_mac, port) or (None, None) if not found
        """
        if self.server_mac:
            logger.info(f"Searching for service on {self.server_mac}...")
            services = bt.find_service(uuid=self.service_uuid, address=self.server_mac)
        else:
            logger.info("Searching for service on all devices...")
            services = bt.find_service(uuid=self.service_uuid)
        
        if len(services) == 0:
            logger.warning("No matching services found")
            return None, None
        
        for svc in services:
            logger.info(f"Found service: {svc['name']} on {svc['host']}")
            return svc['host'], svc['port']
        
        return None, None
    
    def connect(self):
        """
        Connect to the NavSystem server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # If server_mac is not provided, try to find the service
            if not self.server_mac or self.port == 1:
                self.server_mac, self.port = self.find_service()
                
                if not self.server_mac:
                    logger.error("Could not find NavSystem service")
                    return False
            
            # Create a new socket and connect
            self.client_sock = bt.BluetoothSocket(bt.RFCOMM)
            self.client_sock.connect((self.server_mac, self.port))
            
            logger.info(f"Connected to {self.server_mac} on port {self.port}")
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the server."""
        if self.client_sock:
            try:
                self.client_sock.close()
            except:
                pass
            
        self.connected = False
        logger.info("Disconnected from server")
    
    def start(self):
        """Start sending data to the server."""
        if not self.connected:
            if not self.connect():
                logger.error("Cannot start sending: not connected")
                return False
        
        self.running = True
        
        # Start sender threads
        self.video_thread = threading.Thread(target=self._video_sender_thread)
        self.video_thread.daemon = True
        self.video_thread.start()
        
        self.audio_thread = threading.Thread(target=self._audio_sender_thread)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        logger.info("Sender threads started")
        return True
    
    def stop(self):
        """Stop sending data to the server."""
        self.running = False
        
        # Wait for threads to finish
        if hasattr(self, 'video_thread'):
            self.video_thread.join(timeout=1.0)
        
        if hasattr(self, 'audio_thread'):
            self.audio_thread.join(timeout=1.0)
        
        self.disconnect()
        logger.info("Sender stopped")
    
    def send_video_frame(self, frame):
        """
        Queue a video frame to be sent.
        
        Args:
            frame: Video frame to send
        """
        self.video_queue.put(frame)
    
    def send_audio_data(self, audio_data):
        """
        Queue audio data to be sent.
        
        Args:
            audio_data: Audio data to send
        """
        self.audio_queue.put(audio_data)
    
    def _video_sender_thread(self):
        """Thread to send video frames from the queue."""
        while self.running:
            try:
                if not self.video_queue.empty():
                    # Get a frame from the queue
                    frame = self.video_queue.get()
                    
                    # Encode the frame as JPEG
                    _, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_data = encoded_frame.tobytes()
                    
                    # Create header: 'video' + size (3 bytes)
                    header = b'video' + len(frame_data).to_bytes(3, byteorder='big')
                    
                    # Send the header and frame data
                    if self.connected:
                        self.client_sock.send(header + frame_data)
                        logger.debug(f"Sent video frame: {len(frame_data)} bytes")
                else:
                    time.sleep(0.01)
            except Exception as e:
                logger.error(f"Error sending video frame: {e}")
                time.sleep(0.1)
                
                # Try to reconnect if connection was lost
                if not self.connected:
                    self.connect()
    
    def _audio_sender_thread(self):
        """Thread to send audio data from the queue."""
        while self.running:
            try:
                if not self.audio_queue.empty():
                    # Get audio data from the queue
                    audio_data = self.audio_queue.get()
                    
                    # Create header: 'audio' + size (3 bytes)
                    header = b'audio' + len(audio_data).to_bytes(3, byteorder='big')
                    
                    # Send the header and audio data
                    if self.connected:
                        self.client_sock.send(header + audio_data)
                        logger.debug(f"Sent audio data: {len(audio_data)} bytes")
                else:
                    time.sleep(0.01)
            except Exception as e:
                logger.error(f"Error sending audio data: {e}")
                time.sleep(0.1)
                
                # Try to reconnect if connection was lost
                if not self.connected:
                    self.connect()

class VideoCapture:
    """
    Class to capture video from a camera.
    """
    def __init__(self, camera_id=0, width=640, height=480, fps=30):
        """
        Initialize the video capture.
        
        Args:
            camera_id: Camera ID (0 for default camera)
            width: Frame width
            height: Frame height
            fps: Frames per second
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self.running = False
        
        logger.info(f"VideoCapture initialized with camera {camera_id}, {width}x{height} at {fps} fps")
    
    def start(self):
        """Start capturing video."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            if not self.cap.isOpened():
                logger.error("Failed to open camera")
                return False
            
            self.running = True
            logger.info("Video capture started")
            return True
        except Exception as e:
            logger.error(f"Error starting video capture: {e}")
            return False
    
    def stop(self):
        """Stop capturing video."""
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        logger.info("Video capture stopped")
    
    def read_frame(self):
        """
        Read a frame from the camera.
        
        Returns:
            numpy.ndarray: Frame or None if capture failed
        """
        if not self.running or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            logger.warning("Failed to capture frame")
            return None
        
        return frame

class AudioCapture:
    """
    Class to capture audio from a microphone.
    """
    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024, format=pyaudio.paInt16):
        """
        Initialize the audio capture.
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels
            chunk_size: Number of frames per buffer
            format: Audio format
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = format
        self.audio = None
        self.stream = None
        self.running = False
        
        logger.info(f"AudioCapture initialized with {sample_rate} Hz, {channels} channels")
    
    def start(self):
        """Start capturing audio."""
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.running = True
            logger.info("Audio capture started")
            return True
        except Exception as e:
            logger.error(f"Error starting audio capture: {e}")
            return False
    
    def stop(self):
        """Stop capturing audio."""
        self.running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        logger.info("Audio capture stopped")
    
    def read_audio(self):
        """
        Read audio data from the microphone.
        
        Returns:
            bytes: Audio data or None if capture failed
        """
        if not self.running or not self.stream:
            return None
        
        try:
            data = self.stream.read(self.chunk_size)
            return data
        except Exception as e:
            logger.warning(f"Failed to capture audio: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Raspberry Pi Bluetooth Sender for NavSystem')
    parser.add_argument('--server-mac', help='MAC address of the server to connect to')
    parser.add_argument('--camera-id', type=int, default=0, help='Camera ID (default: 0)')
    parser.add_argument('--width', type=int, default=640, help='Frame width (default: 640)')
    parser.add_argument('--height', type=int, default=480, help='Frame height (default: 480)')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second (default: 30)')
    parser.add_argument('--sample-rate', type=int, default=16000, help='Audio sample rate in Hz (default: 16000)')
    parser.add_argument('--channels', type=int, default=1, help='Number of audio channels (default: 1)')
    parser.add_argument('--video-only', action='store_true', help='Send only video data')
    parser.add_argument('--audio-only', action='store_true', help='Send only audio data')
    args = parser.parse_args()
    
    # Initialize the Bluetooth sender
    sender = BluetoothSender(server_mac=args.server_mac)
    
    # Discover servers if no MAC address is provided
    if not args.server_mac:
        sender.discover_server()
    
    # Connect to the server
    if not sender.connect():
        logger.error("Failed to connect to server")
        return
    
    # Start the sender
    if not sender.start():
        logger.error("Failed to start sender")
        return
    
    try:
        # Initialize video capture if needed
        video_capture = None
        if not args.audio_only:
            video_capture = VideoCapture(
                camera_id=args.camera_id,
                width=args.width,
                height=args.height,
                fps=args.fps
            )
            
            if not video_capture.start():
                logger.error("Failed to start video capture")
                sender.stop()
                return
        
        # Initialize audio capture if needed
        audio_capture = None
        if not args.video_only:
            audio_capture = AudioCapture(
                sample_rate=args.sample_rate,
                channels=args.channels
            )
            
            if not audio_capture.start():
                logger.error("Failed to start audio capture")
                if video_capture:
                    video_capture.stop()
                sender.stop()
                return
        
        logger.info("Press Ctrl+C to stop")
        
        # Main loop
        while True:
            # Capture and send video frame
            if video_capture:
                frame = video_capture.read_frame()
                if frame is not None:
                    sender.send_video_frame(frame)
            
            # Capture and send audio data
            if audio_capture:
                audio_data = audio_capture.read_audio()
                if audio_data is not None:
                    sender.send_audio_data(audio_data)
            
            # Sleep to control the loop rate
            time.sleep(0.001)
    
    except KeyboardInterrupt:
        logger.info("Stopping...")
    
    finally:
        # Clean up
        if video_capture:
            video_capture.stop()
        
        if audio_capture:
            audio_capture.stop()
        
        sender.stop()
        
        logger.info("Exited cleanly")

if __name__ == "__main__":
    main()
