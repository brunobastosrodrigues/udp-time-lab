import socket
from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime
import os
import time

app = Flask(__name__)

SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
UDP_SERVER_ADDRESS = (SERVER_IP, 5678)
BUFFER_SIZE = 1024
TIMEOUT_SECONDS = 2 

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
        
        .btn-main { background: #e67e22; color: white; border: none; padding: 15px 30px; font-size: 1.1em; border-radius: 50px; cursor: pointer; display: block; margin: 0 auto; width: 100%; }
        .btn-main:hover { background: #d35400; }

        /* Admin Panel Styles */
        .admin-panel { margin-top: 40px; padding-top: 20px; border-top: 2px dashed #ccc; text-align: center; }
        .admin-controls { display: flex; justify-content: center; gap: 20px; margin-top: 10px; }
        .btn-crash { background: #c0392b; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-repair { background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-crash:hover { background: #a93226; }
        .btn-repair:hover { background: #1e8449; }
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
            <input type="hidden" name="action" value="sync">
            <button type="submit" class="btn-main">Sync Time</button>
        </form>

        {% if rtt %}
        <p style="text-align: center; color: #666;">Latency: <strong>{{ rtt }} ms</strong></p>
        {% endif %}

        <div class="admin-panel">
            <h3>⚠️ Instructor Controls (Chaos Engineering)</h3>
            <p><small>Simulate a server failure without stopping Docker.</small></p>
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
    """Helper to send a command to the backend"""
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
        s.sendto(command.encode(), UDP_SERVER_ADDRESS)

@app.route("/", methods=["GET", "POST"])
def home():
    status_message = "System Ready."
    status_class = "status-idle"
    rtt = None
    
    if request.method == "POST":
        action = request.form.get("action")

        # CASE 1: Instructor clicks "Simulate Crash"
        if action == "crash":
            send_udp_command("ADMIN_CRASH")
            status_message = "💀 Command Sent: Server is now in CRASH state."
            status_class = "status-idle"

        # CASE 2: Instructor clicks "Repair Server"
        elif action == "repair":
            send_udp_command("ADMIN_REPAIR")
            status_message = "🟢 Command Sent: Server has been REPAIRED."
            status_class = "status-idle"

        # CASE 3: Student clicks "Sync Time"
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
                    status_message = f"⚠️ CRITICAL ERROR: Server Request Timed Out ({TIMEOUT_SECONDS}s)"
                    status_class = "status-error"
                except Exception as e:
                    status_message = f"Error: {e}"
                    status_class = "status-error"

    return render_template_string(HTML_TEMPLATE, status_message=status_message, status_class=status_class, target_server=SERVER_IP, rtt=rtt)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)