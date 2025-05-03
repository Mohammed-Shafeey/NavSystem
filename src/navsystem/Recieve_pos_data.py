import socket

def get_latest_position():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 5000))
    sock.settimeout(3.0)  # Wait at most 3 seconds
    print("Waiting for SLAM position data...")

    try:
        data, _ = sock.recvfrom(1024)
        print("Received Position and Angle (X, Y, Z, W):", data.decode())
        return data.decode()
    except socket.timeout:
        print("Timeout: No SLAM data received.")
        return None

