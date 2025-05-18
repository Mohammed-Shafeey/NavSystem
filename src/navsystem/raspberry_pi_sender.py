import socket
import struct
import time
from PIL import Image
from picamera2 import Picamera2
import io
import logging

SERVER_IP = "192.168.230.1"  # Replace with receiver IP
PORT = 8000
JPEG_QUALITY = 5  # Lower = more compression, faster send
RESOLUTION = (620, 480)
FRAME_DELAY = 0.03  # ~30 FPS target

# Logging
logging.basicConfig(level=logging.INFO)

def main():
    # Setup camera in video mode
    cam = Picamera2()
    config = cam.create_video_configuration(main={"size": RESOLUTION})
    cam.configure(config)
    cam.start()
    cam.set_controls({"Brightness": 0.3})
    time.sleep(1)  # Warm up camera

    # Connect to receiver
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, PORT))
    logging.info(f"Connected to {SERVER_IP}:{PORT}")

    try:
        while True:
            # Capture frame from video stream
            frame = cam.capture_array("main")

            # Encode to JPEG (compressed)
            buffer = io.BytesIO()
            image = Image.fromarray(frame)
            image.save(buffer, format="JPEG", quality=JPEG_QUALITY)
            jpeg_data = buffer.getvalue()

            # Send length + data
            sock.sendall(struct.pack(">I", len(jpeg_data)) + jpeg_data)

            time.sleep(FRAME_DELAY)  # Prevent CPU overload
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        cam.stop()
        sock.close()
        logging.info("Sender stopped.")

if __name__ == "__main__":
    main()