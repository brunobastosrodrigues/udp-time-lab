import socket
from flask import Flask, render_template_string, request
from datetime import datetime
import os

app = Flask(__name__)

# Web Client Configuration
# We get the server IP from the Environment Variable (set in docker-compose)
# If it's not set, it defaults to localhost (useful for testing without Docker)
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
UDP_SERVER_ADDRESS = (SERVER_IP, 5678) 
BUFFER_SIZE = 1024

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Distributed Time Synchronization</title>
</head>
<body>
    <h1>Client Web Interface</h1>
    <p><strong>Target Server:</strong> {{ target_server }}</p>
    <p>Local time: {{ local_time }}</p>
    <p>Synchronized server time: {{ server_time }}</p>
    <p>Adjusted local time: {{ adjusted_time }}</p>
    <form action="/" method="POST">
        <button type="submit">Sync Time</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    """Web interface for time synchronization"""
    local_time = datetime.now()
    server_time = None
    adjusted_time = None

    if request.method == "POST":
        # Create a UDP socket to communicate with the server
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as udp_client_socket:
            try:
                # Set a timeout so the webpage doesn't hang if server is down
                udp_client_socket.settimeout(2)
                
                # Send a time request to the UDP server
                udp_client_socket.sendto("REQUEST_TIME".encode(), UDP_SERVER_ADDRESS)
                response, _ = udp_client_socket.recvfrom(BUFFER_SIZE)

                # Decode and parse the server's response
                server_time = datetime.strptime(response.decode(), '%Y-%m-%d %H:%M:%S.%f')
                adjusted_time = server_time 

            except Exception as e:
                server_time = f"Error: {e}"

    return render_template_string(
        HTML_TEMPLATE,
        target_server=SERVER_IP,
        local_time=local_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        server_time=server_time.strftime('%Y-%m-%d %H:%M:%S.%f') if isinstance(server_time, datetime) else server_time,
        adjusted_time=adjusted_time.strftime('%Y-%m-%d %H:%M:%S.%f') if adjusted_time else "Unavailable"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
