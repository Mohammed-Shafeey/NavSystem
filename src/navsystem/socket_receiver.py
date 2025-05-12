import socket
import struct
import io
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
PORT = 8000

def receive_exact(sock, length):
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", PORT))
    sock.listen(1)
    logging.info(f"Listening on port {PORT}...")

    conn, addr = sock.accept()
    logging.info(f"Connection from {addr}")

    try:
        while True:
            size_data = receive_exact(conn, 4)
            if not size_data:
                break
            size = struct.unpack(">I", size_data)[0]
            image_data = receive_exact(conn, size)
            if not image_data:
                break

            image = Image.open(io.BytesIO(image_data))
            image.show()  # opens image with system default viewer
    finally:
        conn.close()
        sock.close()
        logging.info("Receiver stopped.")

if __name__ == "__main__":
    main()
