import socket

# Set up UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 5000))  

print("Waiting for SLAM position data...")

while True:
    data, _ = sock.recvfrom(1024)  # Receive data
    print("Received Position (X, Y, Z):", data.decode())  # Print it
