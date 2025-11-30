from flask import Flask, render_template_string, request
from datetime import datetime
import socket

app = Flask(__name__)

# CSS Styles for a clean, educational look
STYLE = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; color: #333; display: flex; justify-content: center; padding-top: 50px; }
    .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 600px; text-align: center; }
    h1 { color: #6c5ce7; margin-bottom: 10px; }
    p { color: #666; margin-bottom: 30px; }
    
    /* Diagram Box */
    .diagram { background: #eef2f5; padding: 20px; border-radius: 8px; margin: 20px 0; display: flex; align-items: center; justify-content: space-between; }
    .node { background: #6c5ce7; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold; }
    .browser-node { background: #0984e3; }
    .arrow { color: #888; font-weight: bold; font-size: 1.2em; }
    
    /* Button */
    .btn { display: inline-block; background: #0984e3; color: white; padding: 12px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; transition: 0.3s; }
    .btn:hover { background: #076cab; transform: translateY(-2px); }
    .btn-back { background: #b2bec3; margin-top: 20px; font-size: 0.9em; }

    /* Time Display */
    .time-box { font-size: 2.5em; font-weight: bold; color: #2d3436; margin: 20px 0; font-family: monospace; }
    .server-info { font-size: 0.9em; color: #999; margin-top: 10px; border-top: 1px solid #eee; padding-top: 10px; }
</style>
"""

@app.route("/", methods=["GET"])
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Simple Time Server</title>{STYLE}</head>
    <body>
        <div class="card">
            <h1>🌐 Simple HTTP Time Server</h1>
            <p>This server listens for standard Web (HTTP) requests.</p>
            
            <div class="diagram">
                <div class="node browser-node">Your Browser</div>
                <div class="arrow"> ⎯ HTTP GET ➝ </div>
                <div class="node">This Server</div>
            </div>

            <p>Click the button below to send a <code>GET /time</code> request.</p>
            <a href="/time" class="btn">📅 Get Current Time</a>
        </div>
    </body>
    </html>
    """

@app.route("/time", methods=["GET"])
def get_time():
    now = datetime.now()
    server_ip = socket.gethostbyname(socket.gethostname())
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Current Time</title>{STYLE}</head>
    <body>
        <div class="card">
            <h1>✅ Request Received</h1>
            <p>The server processed your request and returned the time:</p>
            
            <div class="time-box">{now.strftime('%H:%M:%S.%f')[:-3]}</div>
            <div style="color: #6c5ce7; font-weight: bold;">{now.strftime('%A, %B %d, %Y')}</div>

            <div class="server-info">
                Served by Container ID: <strong>{socket.gethostname()}</strong><br>
                Internal IP: {server_ip}
            </div>

            <a href="/" class="btn btn-back">⬅ Go Back</a>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)