import speech_recognition as sr
import threading
import queue
import logging
import os
import time
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AudioProcessor')

# This queue will be imported from the receiver module in the final structure
# For now, define it here for standalone testing/development if needed
try:
    from .bluetooth_receiver import audio_queue
except ImportError:
    logger.warning("Could not import audio_queue from bluetooth_receiver. Creating a local queue.")
    audio_queue = queue.Queue()

class AudioToTextConverter:
    """
    Class to convert audio data to text using speech recognition.
    """
    def __init__(self, language="en-US", sample_rate=16000, channels=1):
        """
        Initialize the audio to text converter.
        
        Args:
            language: Language code for speech recognition
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels
        """
        self.language = language
        self.sample_rate = sample_rate
        self.channels = channels
        self.recognizer = sr.Recognizer()
        self.running = False
        self.commands = []
        self.last_command = None
        
        # Create output directory for transcripts if it doesn't exist
        self.output_dir = os.path.join(os.getcwd(), 'transcripts')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load command definitions
        self._load_commands()
        
        logger.info("AudioToTextConverter initialized")
    
    def _load_commands(self):
        """Load predefined commands and their actions."""
        self.commands = [
            {
                "keywords": ["navigate", "go", "take me"],
                "action": "navigate",
                "description": "Navigate to a specified location"
            },
            {
                "keywords": ["stop", "halt", "pause"],
                "action": "stop",
                "description": "Stop navigation"
            },
            {
                "keywords": ["restart", "resume", "continue"],
                "action": "restart",
                "description": "Restart or resume navigation"
            },
            {
                "keywords": ["where am i", "location", "position"],
                "action": "get_location",
                "description": "Get current location information"
            },
            {
                "keywords": ["help", "assistance", "commands"],
                "action": "help",
                "description": "List available commands"
            }
        ]
        logger.info(f"Loaded {len(self.commands)} command definitions")
    
    def start_processing(self):
        """Start processing audio data from the queue."""
        if self.running:
            logger.warning("Audio processor is already running")
            return False
        
        self.running = True
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_audio)
        self.process_thread.daemon = True
        self.process_thread.start()
        
        logger.info("Audio processing started")
        return True
    
    def stop_processing(self):
        """Stop processing audio data."""
        self.running = False
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=1.0)
        logger.info("Audio processing stopped")
    
    def _process_audio(self):
        """Process audio data from the queue."""
        while self.running:
            try:
                if not audio_queue.empty():
                    # Get audio data from the queue
                    audio_data = audio_queue.get()
                    
                    # Process the audio data
                    text = self._convert_audio_to_text(audio_data)
                    
                    if text:
                        logger.info(f"Recognized text: {text}")
                        
                        # Save transcript
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        transcript_path = os.path.join(self.output_dir, f'transcript_{timestamp}.txt')
                        with open(transcript_path, 'w') as f:
                            f.write(text)
                        
                        # Process commands in the recognized text
                        command = self._identify_command(text)
                        if command:
                            self.last_command = self._execute_command(command, text)
                else:
                    time.sleep(0.01)
            except Exception as e:
                logger.error(f"Error processing audio data: {e}")
                time.sleep(0.1)
    
    def _convert_audio_to_text(self, audio_data):
        """
        Convert audio data to text using speech recognition.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            str: Recognized text or None if recognition failed
        """
        try:
            # Assuming audio data is raw PCM
            # The number of bytes per sample depends on the format (e.g., 2 for paInt16)
            bytes_per_sample = 2 # Assuming pyaudio.paInt16
            audio = sr.AudioData(audio_data, self.sample_rate, bytes_per_sample * self.channels)
            
            # Perform speech recognition
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except sr.UnknownValueError:
            logger.warning("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.error(f"Could not request results from Speech Recognition service: {e}")
        except Exception as e:
            logger.error(f"Error converting audio to text: {e}")
        
        return None
    
    def _identify_command(self, text):
        """
        Identify commands in the recognized text.
        
        Args:
            text: Recognized text
            
        Returns:
            dict: Command information or None if no command was identified
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        for command in self.commands:
            for keyword in command["keywords"]:
                if keyword.lower() in text_lower:
                    logger.info(f"Identified command: {command['action']}")
                    return command
        
        logger.info("No command identified in text")
        return None
    
    def _execute_command(self, command, text):
        """
        Execute the identified command.
        
        Args:
            command: Command information
            text: Original recognized text
            
        Returns:
            dict: Information about the executed command (or None)
        """
        action = command["action"]
        executed_command_info = {"action": action, "text": text, "timestamp": time.time()}
        
        try:
            if action == "navigate":
                # Extract destination from text
                destination = self._extract_destination(text)
                if destination:
                    logger.info(f"Executing navigation command to: {destination}")
                    executed_command_info["destination"] = destination
                    # In a real implementation, you would call the navigation system
                    # nav_system.set_destination(destination)
                    # nav_system.start_navigation()
                else:
                    logger.warning("Could not extract destination for navigation command")
                    return None
                
            elif action == "stop":
                logger.info("Executing stop navigation command")
                # nav_system.stop_navigation()
                
            elif action == "restart":
                logger.info("Executing restart navigation command")
                # nav_system.start_navigation() # Or a specific resume function
                
            elif action == "get_location":
                logger.info("Executing get location command")
                # location = nav_system.get_current_position()
                # logger.info(f"Current location: {location}")
                # executed_command_info["location"] = location
                
            elif action == "help":
                logger.info("Executing help command")
                help_text = "Available commands: " + ", ".join([c["action"] for c in self.commands])
                logger.info(help_text)
                executed_command_info["help_text"] = help_text
                
            else:
                logger.warning(f"Unknown action: {action}")
                return None
                
            return executed_command_info
        
        except Exception as e:
            logger.error(f"Error executing command {action}: {e}")
            return None
    
    def _extract_destination(self, text):
        """
        Extract destination from the recognized text.
        
        Args:
            text: Recognized text
            
        Returns:
            str: Extracted destination or None if no destination was found
        """
        # This is a simplified implementation
        # In a real implementation, you would use NLP techniques to extract the destination
        
        text_lower = text.lower()
        
        # Look for common patterns like "navigate to X" or "go to X"
        for pattern in ["navigate to ", "go to ", "take me to "]:
            if pattern in text_lower:
                destination = text[text_lower.index(pattern) + len(pattern):].strip()
                # Remove potential trailing punctuation
                if destination.endswith((".", "?", "!")):
                    destination = destination[:-1]
                return destination
        
        # If no pattern found, return None or maybe the whole text after the keyword?
        # For now, returning None if specific pattern not found.
        return None

# Main function to start the audio processor (for standalone testing)
def main():
    # Initialize the audio to text converter
    audio_processor = AudioToTextConverter()
    
    # Start processing audio data
    if audio_processor.start_processing():
        logger.info("Audio processor started successfully")
        
        # Simulate adding some audio data (replace with real data source)
        def simulate_audio_input():
            time.sleep(5) # Wait a bit
            logger.info("Simulating audio input...")
            # Create some dummy audio data (e.g., silence or simple tone)
            # For simplicity, using placeholder bytes
            dummy_audio = b"\x00" * 16000 * 2 * 1 # 1 second of silence at 16kHz, 16-bit mono
            audio_queue.put(dummy_audio)
            time.sleep(5)
            # Simulate a command
            # This requires a real audio sample or a mock recognizer
            # audio_queue.put(real_command_audio_data)

        # simulation_thread = threading.Thread(target=simulate_audio_input)
        # simulation_thread.daemon = True
        # simulation_thread.start()
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            audio_processor.stop_processing()
    else:
        logger.error("Failed to start audio processor")

if __name__ == "__main__":
    main()

