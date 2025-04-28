import bluetooth as bt
import threading
import json
import time
import os
import cv2
import numpy as np
import speech_recognition as sr
import logging
from queue import Queue

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('BluetoothReceiver')

# Data queues for different types of data
video_queue = Queue()
audio_queue = Queue()

class BluetoothReceiver:
    def __init__(self, server_name="NavSystem", service_uuid="94f39d29-7d6d-437d-973b-fba39e49d4ee"):
        """
        Initialize the Bluetooth receiver.
        
        Args:
            server_name: Name of the Bluetooth server
            service_uuid: UUID for the Bluetooth service
        """
        self.server_name = server_name
        self.service_uuid = service_uuid
        self.server_sock = None
        self.client_socks = []
        self.running = False
        self.data_handlers = {
            'video': self._handle_video_data,
            'audio': self._handle_audio_data
        }
        
    def start_server(self):
        """Start the Bluetooth server and listen for connections."""
        try:
            self.server_sock = bt.BluetoothSocket(bt.RFCOMM)
            self.server_sock.bind(("", bt.PORT_ANY))
            self.server_sock.listen(5)
            
            port = self.server_sock.getsockname()[1]
            
            # Advertise the service
            bt.advertise_service(
                self.server_sock, 
                self.server_name,
                service_id=self.service_uuid,
                service_classes=[self.service_uuid, bt.SERIAL_PORT_CLASS],
                profiles=[bt.SERIAL_PORT_PROFILE]
            )
            
            logger.info(f"Started Bluetooth server on port {port}")
            logger.info(f"Service Name: {self.server_name}")
            logger.info(f"Service UUID: {self.service_uuid}")
            
            self.running = True
            
            # Start a thread to accept connections
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            return True
        except Exception as e:
            logger.error(f"Failed to start Bluetooth server: {e}")
            return False
    
    def stop_server(self):
        """Stop the Bluetooth server and close all connections."""
        self.running = False
        
        # Close all client connections
        for sock in self.client_socks:
            try:
                sock.close()
            except:
                pass
        
        # Close the server socket
        if self.server_sock:
            try:
                self.server_sock.close()
            except:
                pass
        
        logger.info("Bluetooth server stopped")
    
    def _accept_connections(self):
        """Accept incoming Bluetooth connections."""
        while self.running:
            try:
                client_sock, client_info = self.server_sock.accept()
                logger.info(f"Accepted connection from {client_info}")
                
                self.client_socks.append(client_sock)
                
                # Start a thread to handle this client
                client_thread = threading.Thread(target=self._handle_client, args=(client_sock, client_info))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
                time.sleep(1)
    
    def _handle_client(self, client_sock, client_info):
        """
        Handle communication with a connected client.
        
        Args:
            client_sock: Client socket
            client_info: Client information
        """
        buffer = b""
        header_size = 8  # Size of the header in bytes
        
        try:
            while self.running:
                # Receive data
                data = client_sock.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages
                while len(buffer) >= header_size:
                    # Parse header
                    header = buffer[:header_size]
                    data_type = header[:5].decode('utf-8').strip()
                    data_size = int.from_bytes(header[5:], byteorder='big')
                    
                    # Check if we have the complete message
                    if len(buffer) < header_size + data_size:
                        break
                    
                    # Extract the message
                    message = buffer[header_size:header_size + data_size]
                    buffer = buffer[header_size + data_size:]
                    
                    # Handle the message based on data type
                    if data_type in self.data_handlers:
                        self.data_handlers[data_type](message)
                    else:
                        logger.warning(f"Unknown data type: {data_type}")
        
        except Exception as e:
            logger.error(f"Error handling client {client_info}: {e}")
        
        finally:
            # Clean up
            try:
                client_sock.close()
                if client_sock in self.client_socks:
                    self.client_socks.remove(client_sock)
            except:
                pass
            
            logger.info(f"Connection closed with {client_info}")
    
    def _handle_video_data(self, data):
        """
        Handle incoming video data.
        
        Args:
            data: Video frame data
        """
        try:
            # Decode the video frame
            frame_data = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Put the frame in the video queue for processing
                video_queue.put(frame)
                logger.debug("Received video frame")
            else:
                logger.warning("Failed to decode video frame")
        except Exception as e:
            logger.error(f"Error handling video data: {e}")
    
    def _handle_audio_data(self, data):
        """
        Handle incoming audio data.
        
        Args:
            data: Audio data
        """
        try:
            # Put the audio data in the audio queue for processing
            audio_queue.put(data)
            logger.debug("Received audio data")
        except Exception as e:
            logger.error(f"Error handling audio data: {e}")

# Function to process video frames for stella vslam
def process_video_for_vslam():
    """Process video frames from the queue for stella vslam."""
    while True:
        if not video_queue.empty():
            frame = video_queue.get()
            # TODO: Implement stella vslam processing
            # This would involve passing the frame to stella vslam
            # For now, we'll just log that we received a frame
            logger.info("Processing video frame for stella vslam")
        else:
            time.sleep(0.01)

# Function to convert audio to text
def process_audio_to_text():
    """Process audio data from the queue and convert to text."""
    recognizer = sr.Recognizer()
    
    while True:
        if not audio_queue.empty():
            audio_data = audio_queue.get()
            
            try:
                # Convert the audio data to an AudioData object
                # Note: This is a simplified example. In a real implementation,
                # you would need to properly format the audio data.
                audio = sr.AudioData(audio_data, 16000, 2)
                
                # Perform speech recognition
                text = recognizer.recognize_google(audio)
                logger.info(f"Speech recognized: {text}")
                
                # TODO: Implement logic to interpret the recognized text
                # and take appropriate actions
            except sr.UnknownValueError:
                logger.warning("Speech Recognition could not understand audio")
            except sr.RequestError as e:
                logger.error(f"Could not request results from Speech Recognition service: {e}")
            except Exception as e:
                logger.error(f"Error processing audio data: {e}")
        else:
            time.sleep(0.01)

# Main function to start the Bluetooth receiver
def main():
    receiver = BluetoothReceiver()
    if receiver.start_server():
        logger.info("Bluetooth receiver started successfully")
        
        # Start video processing thread
        video_thread = threading.Thread(target=process_video_for_vslam)
        video_thread.daemon = True
        video_thread.start()
        
        # Start audio processing thread
        audio_thread = threading.Thread(target=process_audio_to_text)
        audio_thread.daemon = True
        audio_thread.start()
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            receiver.stop_server()
    else:
        logger.error("Failed to start Bluetooth receiver")

if __name__ == "__main__":
    main()
