import cv2
import threading
import queue
import time

class VideoProcessor:
    """
    Minimal video processor that captures frames from a camera
    and forwards them to a queue for SLAM or other processing.
    """
    def __init__(self, src=0):
        """
        Initialize the video processor.

        Args:
            src: Camera index or video file path.
        """
        self.src = src
        self.capture = cv2.VideoCapture(self.src)
        self.frame_queue = queue.Queue(maxsize=10)
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            print("VideoProcessor is already running.")
            return False

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return True

    def _capture_loop(self):
        while self.running:
            ret, frame = self.capture.read()
            if not ret:
                print("Failed to read frame.")
                break

            if not self.frame_queue.full():
                self.frame_queue.put(frame)

            time.sleep(0.01)  # Avoid CPU overuse

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.capture.release()

    def get_latest_frame(self):
        """
        Get the most recent frame from the queue (non-blocking).
        """
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
