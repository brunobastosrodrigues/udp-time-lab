import socket
from datetime import datetime
import os

# Configuration
IPaddress = "0.0.0.0"
portNumber = 5678
bufferSize = 1024

# STATE VARIABLE: Controls if the server is "Simulating a Crash"
is_server_healthy = True

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((IPaddress, portNumber))

print(f"UDP Time Server running on {IPaddress}:{portNumber}")
print("Waiting for requests...")

while True:
    message, clientAddress = UDPServerSocket.recvfrom(bufferSize)
    decoded_message = message.decode()

    # --- ADMIN COMMANDS (To simulate failures) ---
    if decoded_message == "ADMIN_CRASH":
        is_server_healthy = False
        print(f"[ADMIN] Simulation Mode: CRASHED (Ignoring requests from {clientAddress})")
        # We don't reply, just acknowledge in logs
        
    elif decoded_message == "ADMIN_REPAIR":
        is_server_healthy = True
        print(f"[ADMIN] Simulation Mode: REPAIRED (Resuming normal service)")

    # --- STANDARD CLIENT REQUESTS ---
    elif decoded_message == "REQUEST_TIME":
        if is_server_healthy:
            # Normal behavior: Send time
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            print(f"Request from {clientAddress} -> Responded: {current_time}")
            UDPServerSocket.sendto(current_time.encode(), clientAddress)
        else:
            # Crashed behavior: DO NOTHING (Simulates a dropped packet or dead server)
            print(f"Request from {clientAddress} -> IGNORED (Simulated Crash)")
    
    else:
        UDPServerSocket.sendto("INVALID_REQUEST".encode(), clientAddress)