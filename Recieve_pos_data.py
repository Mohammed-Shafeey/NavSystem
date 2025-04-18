import socket

def get_latest_position():
    # Set up UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 5000))  

    print("Waiting for SLAM position data...")

    data, _ = sock.recvfrom(1024)  # Receive data
    print("Received Position and Angle (X, Y, Z, W):", data.decode())  # Print it
    
    return data.decode()


