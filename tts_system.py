import pyttsx3
import threading
import queue
import time

class TTSSystem:
    def __init__(self, rate=150, volume=1.0):
        """
        Initialize the Text-to-Speech system.
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        # Initialize the TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
        # Get available voices and set to default
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        
        # Create a queue for speech instructions
        self.speech_queue = queue.Queue()
        
        # Flag to control the speech thread
        self.running = False
        self.speech_thread = None
        
        # Priority levels for different types of instructions
        self.PRIORITY_HIGH = 3    # Immediate turns, safety instructions
        self.PRIORITY_MEDIUM = 2  # Upcoming turns, distance updates
        self.PRIORITY_LOW = 1     # General information
    
    def start(self):
        """Start the TTS system and speech processing thread."""
        if not self.running:
            self.running = True
            self.speech_thread = threading.Thread(target=self._process_speech_queue)
            self.speech_thread.daemon = True
            self.speech_thread.start()
            print("TTS system started")
    
    def stop(self):
        """Stop the TTS system and speech processing thread."""
        if self.running:
            self.running = False
            # Add a None item to unblock the queue
            self.speech_queue.put((None, 0))
            if self.speech_thread:
                self.speech_thread.join(timeout=1.0)
            print("TTS system stopped")
    
    def _process_speech_queue(self):
        """Process speech instructions from the queue."""
        while self.running:
            try:
                # Get the next instruction from the queue
                text, priority = self.speech_queue.get(timeout=0.5)
                
                # Check for stop signal
                if text is None:
                    self.speech_queue.task_done()
                    break
                
                # Speak the text
                self.engine.say(text)
                self.engine.runAndWait()
                
                # Mark the task as done
                self.speech_queue.task_done()
                
                # Small delay between instructions
                time.sleep(0.3)
                
            except queue.Empty:
                # Queue is empty, continue waiting
                continue
            except Exception as e:
                print(f"Error in speech processing: {e}")
    
    def speak(self, text, priority=2):
        """
        Add a speech instruction to the queue.
        
        Args:
            text: Text to speak
            priority: Priority level (1-3, higher is more important)
        """
        if not self.running:
            print("Warning: TTS system not started")
            return
        
        # Add the instruction to the queue
        self.speech_queue.put((text, priority))
    
    def clear_queue(self):
        """Clear all pending speech instructions."""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
    
    def generate_turn_instruction(self, direction, turn_type, distance=None):
        """
        Generate a turn instruction.
        
        Args:
            direction: Turn direction (left, right)
            turn_type: Type of turn (slight, normal, sharp, u-turn)
            distance: Distance to the turn (optional)
            
        Returns:
            str: Turn instruction text
        """
        instruction = ""
        
        # Add distance information if provided
        if distance is not None:
            instruction += f"In {distance}, "
        
        # Add turn information
        if turn_type == "u-turn":
            instruction += f"make a U-turn"
        else:
            instruction += f"{turn_type} {direction}"
        
        return instruction
    
    def generate_distance_update(self, distance, destination_name=None):
        """
        Generate a distance update instruction.
        
        Args:
            distance: Distance in appropriate units
            destination_name: Name of the destination (optional)
            
        Returns:
            str: Distance update text
        """
        if destination_name:
            return f"{destination_name} is {distance} away"
        else:
            return f"Continue for {distance}"
    
    def announce_arrival(self, destination_name=None):
        """
        Generate an arrival announcement.
        
        Args:
            destination_name: Name of the destination (optional)
            
        Returns:
            str: Arrival announcement text
        """
        if destination_name:
            return f"You have arrived at {destination_name}"
        else:
            return f"You have reached your destination"
