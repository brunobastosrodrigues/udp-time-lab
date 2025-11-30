import socket
from datetime import datetime
import os

# UDP Server Configuration
# In Docker, we MUST listen on 0.0.0.0 to receive traffic from outside the container
IPaddress = "0.0.0.0" 
portNumber = 5678
bufferSize = 1024

# Create a UDP socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((IPaddress, portNumber))

print(f"UDP Time Server is running on {IPaddress}:{portNumber}")

while True:
    # Listen for incoming messages
    message, clientAddress = UDPServerSocket.recvfrom(bufferSize)
    decoded_message = message.decode()

    if decoded_message == "REQUEST_TIME":
        # Get the current server timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f"Received request from {clientAddress}, responding with time: {current_time}")
        
        # Send the timestamp back to the client
        UDPServerSocket.sendto(current_time.encode(), clientAddress)
    else:
        # Respond with an error message for invalid requests
        UDPServerSocket.sendto("INVALID_REQUEST".encode(), clientAddress)
