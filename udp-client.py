import socket
from flask import Flask, render_template_string, request
from datetime import datetime
import os
import time

app = Flask(__name__)

SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
UDP_SERVER_ADDRESS = (SERVER_IP, 5678)
BUFFER_SIZE = 1024
TIMEOUT_SECONDS = 2 

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Distributed System Fault Tolerance</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({startOnLoad:true});</script>

    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7f6; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #2c3e50; }
        
        .status-box { padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-weight: bold; }
        .status-idle { background: #eee; color: #777; }
        .status-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        
        .diagram-container { text-align: center; margin: 30px 0; background: #fafafa; padding: 20px; border-radius: 8px; border: 1px solid #eee; }
        
        .btn-main { background: #e67e22; color: white; border: none; padding: 15px 30px; font-size: 1.1em; border-radius: 50px; cursor: pointer; display: block; margin: 0 auto; width: 100%; }
        .btn-main:hover { background: #d35400; }

        .admin-panel { margin-top: 40px; padding-top: 20px; border-top: 2px dashed #ccc; text-align: center; }
        .admin-controls { display: flex; justify-content: center; gap: 20px; margin-top: 10px; }
        .btn-crash { background: #c0392b; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-repair { background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ Distributed Failure Handling</h1>
        
        <div class="status-box {{ status_class }}">
            {{ status_message }}
        </div>

        <div class="diagram-container">
            <div class="mermaid">
                graph LR
                Client(Client App<br>Flask)
                Backend(Backend Svr<br>UDP :5678)
                
                style Client fill:#3498db,stroke:#2980b9,color:white
                
                {% if status_class == 'status-error' %}
                    %% CRASH STATE
                    Client -.-x|TIMEOUT| Backend
                    style Backend fill:#e74c3c,stroke:#c0392b,color:white,stroke-dasharray: 5 5
                {% else %}
                    %% NORMAL STATE
                    Client -- UDP Request --> Backend
                    style Backend fill:#27ae60,stroke:#2ecc71,color:white
                {% endif %}
            </div>
        </div>

        <form action="/" method="POST">
            <input type="hidden" name="action" value="sync">
            <button type="submit" class="btn-main">Sync Time</button>
        </form>

        {% if rtt %}
        <p style="text-align: center; color: #666;">Latency: <strong>{{ rtt }} ms</strong></p>
        {% endif %}

        <div class="admin-panel">
            <h3>⚠️ Instructor Controls (Chaos Engineering)</h3>
            <div class="admin-controls">
                <form action="/" method="POST">
                    <input type="hidden" name="action" value="crash">
                    <button type="submit" class="btn-crash">💥 Simulate Crash</button>
                </form>
                <form action="/" method="POST">
                    <input type="hidden" name="action" value="repair">
                    <button type="submit" class="btn-repair">🔧 Repair Server</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
"""

def send_udp_command(command):
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
        s.sendto(command.encode(), UDP_SERVER_ADDRESS)

@app.route("/", methods=["GET", "POST"])
def home():
    status_message = "System Ready."
    status_class = "status-idle"
    rtt = None
    
    if request.method == "POST":
        action = request.form.get("action")

        if action == "crash":
            send_udp_command("ADMIN_CRASH")
            status_message = "💀 Server CRASHED. Try Syncing now."
            status_class = "status-idle" # Diagram stays green until they TRY to sync

        elif action == "repair":
            send_udp_command("ADMIN_REPAIR")
            status_message = "🟢 Server REPAIRED."
            status_class = "status-idle"

        elif action == "sync":
            start = time.time()
            with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
                s.settimeout(TIMEOUT_SECONDS)
                try:
                    s.sendto("REQUEST_TIME".encode(), UDP_SERVER_ADDRESS)
                    msg, _ = s.recvfrom(BUFFER_SIZE)
                    
                    rtt = round((time.time() - start) * 1000, 2)
                    server_time = datetime.strptime(msg.decode(), '%Y-%m-%d %H:%M:%S.%f')
                    status_message = f"✅ Success! Server Time: {server_time.strftime('%H:%M:%S')}"
                    status_class = "status-success"
                    
                except socket.timeout:
                    status_message = f"⚠️ CRITICAL ERROR: Connection Timed Out ({TIMEOUT_SECONDS}s)"
                    status_class = "status-error"
                except Exception as e:
                    status_message = f"Error: {e}"
                    status_class = "status-error"

    return render_template_string(HTML_TEMPLATE, status_message=status_message, status_class=status_class, target_server=SERVER_IP, rtt=rtt)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)