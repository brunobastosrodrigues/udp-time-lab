import socket
from flask import Flask, render_template_string, request
from datetime import datetime
import os
import time

app = Flask(__name__)

# Configuration
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
UDP_SERVER_ADDRESS = (SERVER_IP, 5678)
BUFFER_SIZE = 1024
TIMEOUT_SECONDS = 2  # Define a strict timeout (Slide 19: Detecting failures)

HISTORY = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Distributed System Fault Tolerance</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7f6; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #2c3e50; }
        
        .status-box { padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-weight: bold; }
        .status-idle { background: #eee; color: #777; }
        .status-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        
        .diagram { display: flex; justify-content: space-between; align-items: center; margin: 30px 0; }
        .node { width: 120px; padding: 15px; text-align: center; color: white; border-radius: 6px; position: relative; }
        .client { background: #3498db; }
        .server { background: #27ae60; }
        .server-down { background: #e74c3c; opacity: 0.5; } 
        .arrow { font-size: 20px; color: #999; font-weight: bold; }
        
        button { background: #e67e22; color: white; border: none; padding: 15px 30px; font-size: 1.1em; border-radius: 50px; cursor: pointer; display: block; margin: 0 auto; }
        button:hover { background: #d35400; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ Distributed Failure Handling</h1>
        
        <div class="status-box {{ status_class }}">
            {{ status_message }}
        </div>

        <div class="diagram">
            <div class="node client">
                <strong>Client</strong><br><small>Flask App</small>
            </div>
            <div class="arrow">
                {% if status_class == 'status-error' %} ❌ Timeout ❌ {% else %} ⇄ UDP Request ⇄ {% endif %}
            </div>
            <div class="node {{ 'server-down' if status_class == 'status-error' else 'server' }}">
                <strong>Backend</strong><br><small>{{ target_server }}</small>
            </div>
        </div>

        <form action="/" method="POST">
            <button type="submit">Try to Sync Time</button>
        </form>

        {% if rtt %}
        <p style="text-align: center; color: #666;">Last Round Trip Time: <strong>{{ rtt }} ms</strong></p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    status_message = "System Ready. Click to Sync."
    status_class = "status-idle"
    rtt = None
    
    if request.method == "POST":
        start = time.time()
        
        # Slide 36: Socket Communication
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
            s.settimeout(TIMEOUT_SECONDS) # Critical for distributed systems!
            try:
                # 1. Send Request
                s.sendto("REQUEST_TIME".encode(), UDP_SERVER_ADDRESS)
                
                # 2. Receive Response
                msg, _ = s.recvfrom(BUFFER_SIZE)
                
                # 3. Success Logic
                rtt = round((time.time() - start) * 1000, 2)
                server_time = datetime.strptime(msg.decode(), '%Y-%m-%d %H:%M:%S.%f')
                status_message = f"✅ Success! Server Time: {server_time.strftime('%H:%M:%S')}"
                status_class = "status-success"
                
            except socket.timeout:
                # Slide 19: Handling Partial Failures (Timeout)
                status_message = f"⚠️ CRITICAL ERROR: Server Request Timed Out ({TIMEOUT_SECONDS}s). The backend might be down."
                status_class = "status-error"
            except Exception as e:
                status_message = f"Error: {e}"
                status_class = "status-error"

    return render_template_string(HTML_TEMPLATE, status_message=status_message, status_class=status_class, target_server=SERVER_IP, rtt=rtt)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)