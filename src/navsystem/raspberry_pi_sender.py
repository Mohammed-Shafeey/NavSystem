import socket
import struct
import time
from PIL import Image
from picamera2 import Picamera2
import io
import logging

logging.basicConfig(level=logging.INFO)
SERVER_IP = "192.168.230.1"  # Replace with receiver IP
PORT = 8000

def main():
    cam = Picamera2()
    cam.configure(cam.create_still_configuration())
    cam.start()
    time.sleep(2)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, PORT))
    logging.info("Connected to receiver.")

    try:
        while True:
            frame = cam.capture_array()
            image = Image.fromarray(frame)
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=40)
            jpeg_data = buffer.getvalue()

            # Send length + JPEG data
            sock.sendall(struct.pack(">I", len(jpeg_data)) + jpeg_data)
            time.sleep(0.1)  # ~10 FPS
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        sock.close()
        cam.close()
        logging.info("Sender stopped.")

if __name__ == "__main__":
    main()
