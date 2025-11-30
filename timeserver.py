from flask import Flask, jsonify, request
from datetime import datetime
import socket

app = Flask(__name__)

# --- STYLING & TEMPLATES ---
STYLE = """
<style>
    :root { --primary: #6c5ce7; --secondary: #a29bfe; --dark: #2d3436; --light: #dfe6e9; --success: #00b894; --code-bg: #282c34; }
    body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f7f6; color: var(--dark); margin: 0; padding: 20px; display: flex; justify-content: center; min-height: 100vh; }
    .container { width: 100%; max-width: 600px; margin-top: 40px; }
    
    /* Cards */
    .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; overflow: hidden; position: relative; }
    .card-header { margin-bottom: 25px; }
    h1 { margin: 0; color: var(--primary); font-size: 2.2rem; }
    p { color: #636e72; line-height: 1.6; }

    /* URL Simulation Bar */
    .url-bar { background: var(--light); padding: 10px 15px; border-radius: 6px; font-family: monospace; color: #555; margin-bottom: 20px; display: flex; align-items: center; border: 1px solid #b2bec3; }
    .method { font-weight: bold; color: var(--primary); margin-right: 10px; }
    .path { color: #2d3436; flex-grow: 1; text-align: left; }

    /* Buttons */
    .btn-group { display: flex; gap: 15px; justify-content: center; margin-top: 20px; }
    .btn { display: flex; align-items: center; justify-content: center; padding: 15px 25px; border-radius: 8px; text-decoration: none; color: white; font-weight: bold; transition: transform 0.2s, box-shadow 0.2s; border: none; cursor: pointer; width: 100%; }
    .btn:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .btn-human { background: linear-gradient(135deg, #6c5ce7, #a29bfe); }
    .btn-robot { background: linear-gradient(135deg, #00b894, #55efc4); }
    .btn-back { background: #b2bec3; color: white; width: auto; display: inline-block; margin-top: 20px; padding: 10px 20px; }

    /* Visual Clock (Human) */
    .clock-display { font-size: 3.5rem; font-weight: 700; color: var(--dark); margin: 20px 0; letter-spacing: 2px; }
    .date-display { color: var(--primary); font-size: 1.2rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

    /* Code Block (Robot) */
    .code-block { background: var(--code-bg); color: #abb2bf; text-align: left; padding: 20px; border-radius: 8px; font-family: 'Consolas', 'Monaco', monospace; overflow-x: auto; position: relative; }
    .key { color: #e06c75; }
    .string { color: #98c379; }
    .number { color: #d19a66; }
    .meta-tag { position: absolute; top: 0; right: 0; background: #abb2bf; color: var(--code-bg); padding: 4px 8px; font-size: 0.7rem; border-bottom-left-radius: 8px; font-weight: bold; }

    /* Metadata Footer */
    .footer-info { margin-top: 30px; padding-top: 15px; border-top: 1px dashed #dfe6e9; font-size: 0.85rem; color: #b2bec3; text-align: left; }
    .footer-item { display: flex; justify-content: space-between; margin-bottom: 5px; }
</style>
"""

@app.route("/", methods=["GET"])
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Web API Demo</title>{STYLE}</head>
    <body>
        <div class="container">
            <div class="card">
                <div class="card-header">
                    <h1>Web API Playground</h1>
                    <p>Select how you want to consume the data. This demonstrates <strong>Content Representation</strong>.</p>
                </div>

                <div class="url-bar">
                    <span class="method">GET</span>
                    <span class="path">http://api.local/time</span>
                </div>

                <div class="btn-group">
                    <a href="/time?format=html" class="btn btn-human">
                        <span style="font-size: 1.5em; margin-right: 10px;">👤</span> 
                        Human Interface<br><small style="font-weight:normal; opacity:0.8;">(HTML Page)</small>
                    </a>
                    <a href="/time?format=json" class="btn btn-robot">
                        <span style="font-size: 1.5em; margin-right: 10px;">🤖</span> 
                        Robot Interface<br><small style="font-weight:normal; opacity:0.8;">(JSON Data)</small>
                    </a>
                </div>
                
                <div class="footer-info">
                    <div class="footer-item"><span>Server Software:</span> <span>Flask (Python)</span></div>
                    <div class="footer-item"><span>Protocol:</span> <span>HTTP/1.1</span></div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/time", methods=["GET"])
def get_time():
    fmt = request.args.get("format", "html")
    now = datetime.now()
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)

    # ---------------- ROBOT INTERFACE (JSON) ----------------
    if fmt == "json":
        # We manually construct the response to ensure the browser displays it comfortably 
        # normally we would just return jsonify(data)
        
        json_str = f'''{{
    <span class="key">"timestamp"</span>: <span class="string">"{now.isoformat()}"</span>,
    <span class="key">"unix_epoch"</span>: <span class="number">{now.timestamp()}</span>,
    <span class="key">"server_info"</span>: {{
        <span class="key">"container_id"</span>: <span class="string">"{hostname}"</span>,
        <span class="key">"ip_address"</span>: <span class="string">"{ip_addr}"</span>
    }},
    <span class="key">"status"</span>: <span class="string">"active"</span>
}}'''
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>JSON Response</title>{STYLE}</head>
        <body>
            <div class="container">
                <div class="card">
                    <div class="url-bar">
                        <span class="method">GET</span>
                        <span class="path">/time?format=json</span>
                    </div>
                    
                    <div class="code-block">
                        <div class="meta-tag">application/json</div>
                        <pre>{json_str}</pre>
                    </div>

                    <div class="footer-info">
                        <p><strong>Educational Note:</strong> This raw text is lightweight and easy for other programs to parse. It is not meant for humans to read directly.</p>
                    </div>

                    <a href="/" class="btn btn-back">⬅ Back to Playground</a>
                </div>
            </div>
        </body>
        </html>
        """

    # ---------------- HUMAN INTERFACE (HTML) ----------------
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Current Time</title>{STYLE}</head>
    <body>
        <div class="container">
            <div class="card">
                <div class="url-bar">
                    <span class="method">GET</span>
                    <span class="path">/time?format=html</span>
                </div>

                <div class="date-display">{now.strftime('%A, %B %d, %Y')}</div>
                <div class="clock-display">{now.strftime('%H:%M:%S')}</div>
                
                <div style="background: #eef2f5; padding: 10px; border-radius: 8px; display: inline-block;">
                    <span style="color: #636e72; font-size: 0.9em;">Served by Container: <strong>{hostname}</strong></span>
                </div>

                <div class="footer-info">
                    <p><strong>Educational Note:</strong> This page includes layout, fonts, and colors (CSS). It is heavy to transmit and hard for machines to read, but great for humans.</p>
                </div>

                <a href="/" class="btn btn-back">⬅ Back to Playground</a>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)