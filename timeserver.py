from flask import Flask, jsonify, request
from datetime import datetime
import socket

app = Flask(__name__)

STYLE = """<style>
    body { font-family: sans-serif; background: #f0f2f5; padding: 40px; text-align: center; }
    .card { background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .btn { background: #6c5ce7; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
    .btn-api { background: #00b894; }
    pre { background: #2d3436; color: #81ecec; text-align: left; padding: 15px; border-radius: 5px; overflow-x: auto; }
</style>"""

@app.route("/", methods=["GET"])
def home():
    return f"""
    {STYLE}
    <div class="card">
        <h1>Web API Demo</h1>
        <p>Choose your "Interface" (Slide 27/28):</p>
        <a href="/time?format=html" class="btn">👤 Human Interface (HTML)</a>
        <a href="/time?format=json" class="btn btn-api">🤖 Robot Interface (JSON)</a>
    </div>
    """

@app.route("/time", methods=["GET"])
def get_time():
    fmt = request.args.get("format", "html")
    now = datetime.now()
    data = {
        "timestamp": now.isoformat(),
        "server_id": socket.gethostname(),
        "status": "active"
    }

    # Case 1: The "Robot" Interface (JSON)
    if fmt == "json":
        return jsonify(data)

    # Case 2: The "Human" Interface (HTML)
    return f"""
    {STYLE}
    <div class="card">
        <h1>Time: {now.strftime('%H:%M:%S')}</h1>
        <p>You requested the <strong>HTML</strong> representation.</p>
        <a href="/" class="btn">Back</a>
    </div>
    """

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)