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

# Store the last 5 requests for the history log
HISTORY = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Distributed Time Sync Lab</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
        
        /* Diagram Styles */
        .diagram { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; padding: 20px; background: #eef2f5; border-radius: 10px; }
        .box { width: 30%; padding: 20px; border-radius: 8px; text-align: center; color: white; position: relative; }
        .client-box { background-color: #3498db; }
        .server-box { background-color: #27ae60; }
        .box h3 { margin: 0 0 10px 0; font-size: 1.2em; }
        .box p { font-size: 0.9em; margin: 5px 0; opacity: 0.9; }
        .arrow { font-size: 2em; color: #7f8c8d; font-weight: bold; }
        
        /* Metrics Section */
        .metrics { display: flex; justify-content: space-around; margin-bottom: 30px; }
        .metric-card { background: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 8px; width: 45%; text-align: center; }
        .metric-value { font-size: 1.4em; font-weight: bold; color: #2c3e50; display: block; margin-top: 5px; }
        .metric-label { font-size: 0.85em; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; }

        /* Button */
        .action-area { text-align: center; margin-bottom: 40px; }
        button { background-color: #e67e22; color: white; border: none; padding: 15px 40px; font-size: 1.1em; border-radius: 50px; cursor: pointer; transition: background 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        button:hover { background-color: #d35400; transform: translateY(-2px); }

        /* History Table */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; color: #7f8c8d; font-weight: 600; }
        tr:hover { background-color: #f1f1f1; }
        .status-success { color: #27ae60; font-weight: bold; }
        .status-error { color: #c0392b; font-weight: bold; }
        
        .badge { background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕰️ Distributed Time Synchronization</h1>

        <div class="diagram">
            <div class="box client-box">
                <h3>Client Container</h3>
                <p>Flask Web App</p>
                <div class="badge">{{ client_ip }}</div>
            </div>
            <div class="arrow">⇄ UDP ⇄</div>
            <div class="box server-box">
                <h3>Backend Container</h3>
                <p>Time Source</p>
                <div class="badge">{{ target_server }}</div>
            </div>
        </div>

        {% if request_made %}
            <div class="metrics">
                <div class="metric-card">
                    <span class="metric-label">Server Timestamp</span>
                    <span class="metric-value">{{ server_time }}</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Round Trip Time (Latency)</span>
                    <span class="metric-value">{{ rtt }} ms</span>
                </div>
            </div>
        {% endif %}

        <div class="action-area">
            <form action="/" method="POST">
                <button type="submit">⚡ Sync Time via UDP</button>
            </form>
        </div>

        <h3>Request History</h3>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Local Time (Sent)</th>
                    <th>Server Time (Received)</th>
                    <th>Latency (RTT)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for item in history %}
                <tr>
                    <td>{{ loop.revindex }}</td>
                    <td>{{ item.local }}</td>
                    <td>{{ item.server }}</td>
                    <td>{{ item.rtt }}</td>
                    <td class="{{ 'status-success' if 'Success' in item.status else 'status-error' }}">{{ item.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

def get_ip_address():
    """Helper to find the container's own IP"""
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

@app.route("/", methods=["GET", "POST"])
def home():
    local_time = datetime.now()
    server_time = "Not Synced"
    rtt_ms = 0
    request_made = False
    
    if request.method == "POST":
        request_made = True
        status = "Error"
        server_time_str = "-"
        
        # Start Timer
        start_time = time.time()
        
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as udp_client_socket:
            try:
                udp_client_socket.settimeout(2)
                # Send
                udp_client_socket.sendto("REQUEST_TIME".encode(), UDP_SERVER_ADDRESS)
                # Receive
                response, _ = udp_client_socket.recvfrom(BUFFER_SIZE)
                
                # Stop Timer
                end_time = time.time()
                
                # Calculate Latency (Round Trip Time) in milliseconds
                rtt_ms = round((end_time - start_time) * 1000, 2)
                
                # Parse Response
                server_time_obj = datetime.strptime(response.decode(), '%Y-%m-%d %H:%M:%S.%f')
                server_time = server_time_obj.strftime('%H:%M:%S.%f')[:-3] # Truncate micros
                server_time_str = server_time
                status = "Success"

            except Exception as e:
                server_time = f"Error: {e}"
                status = f"Failed ({e})"
        
        # Log to history (Keep last 5)
        HISTORY.insert(0, {
            "local": local_time.strftime('%H:%M:%S'),
            "server": server_time_str,
            "rtt": f"{rtt_ms} ms" if status == "Success" else "-",
            "status": status
        })
        if len(HISTORY) > 5:
            HISTORY.pop()

    return render_template_string(
        HTML_TEMPLATE,
        client_ip=get_ip_address(),
        target_server=SERVER_IP,
        request_made=request_made,
        server_time=server_time,
        rtt=rtt_ms,
        history=HISTORY
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)