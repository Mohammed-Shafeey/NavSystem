import socket
import struct
import io
import sys
import argparse
from PIL import Image

from PIL import ImageTk
import tkinter as tk


PORT = 8000

def receive_exact(sock, length):
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def start_video_gui(conn):
    def update_frame():
        nonlocal conn, label

        try:
            size_data = receive_exact(conn, 4)
            if not size_data:
                root.after(10, update_frame)
                return
            size = struct.unpack(">I", size_data)[0]

            image_data = receive_exact(conn, size)
            if not image_data:
                root.after(10, update_frame)
                return

            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            frame = ImageTk.PhotoImage(image)
            label.config(image=frame)
            label.image = frame
        except Exception as e:
            print(f"Error: {e}")

        root.after(1, update_frame)

    root = tk.Tk()
    root.title("Video Stream")
    label = tk.Label(root)
    label.pack()
    update_frame()
    root.mainloop()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--show', action='store_true', help="Display video stream in a window")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", PORT))
    sock.listen(1)
    print(f"Listening on port {PORT}...")
    conn, addr = sock.accept()
    print(f"Connected from {addr}")

    if args.show:
        try:
            start_video_gui(conn)
        except Exception as e:
            print(f"GUI error: {e}")
    else:
        # Headless mode: just receive frames
        while True:
            size_data = receive_exact(conn, 4)
            if not size_data:
                break
            size = struct.unpack(">I", size_data)[0]
            image_data = receive_exact(conn, size)
            if not image_data:
                break

            # Optional: do something with image_data
            print(f"Received frame ({size} bytes)")

    conn.close()
    sock.close()

if __name__ == "__main__":
    main()
