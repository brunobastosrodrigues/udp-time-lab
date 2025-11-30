from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return """
    <h1>Welcome to the System Time Server</h1>
    <p>Click below to see the current system time:</p>
    <a href="/time">Get Current Time</a>
    """

@app.route("/time", methods=["GET"])
def get_time():
    today = datetime.now()
    return f"<h1>Current System Time</h1><p>{str(today)}</p><a href='/'>Go Back</a>"

if __name__ == "__main__":
    # Matches the simple server concept in the slides
    app.run(debug=True, host="0.0.0.0", port=5000)