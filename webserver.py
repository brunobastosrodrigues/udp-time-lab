import os
from flask import Flask, render_template_string, request, abort

app = Flask(__name__)

# Base directory for navigation
BASE_DIR = os.getcwd()

# Configuration for the Dashboard
# We list the ports we defined in docker-compose.yml
LAB_SERVICES = [
    {"name": "File Browser (This Page)", "port": 5000, "desc": "Explore the code files"},
    {"name": "UDP Web Client", "port": 5001, "desc": "The User Interface for the Time App"},
    {"name": "Simple Time Server", "port": 5002, "desc": "Standard HTTP Time Server"},
    {"name": "UDP Backend Server", "port": 5678, "desc": "Internal UDP Time Source (No Web UI)"}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Distributed Systems Lab</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .dashboard { background-color: #f0f4f8; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #d9e2ec; }
        .service-item { margin-bottom: 10px; }
        .service-link { font-weight: bold; text-decoration: none; color: #007bff; }
        .service-link:hover { text-decoration: underline; }
        .note { font-size: 0.9em; color: #666; margin-left: 10px; }
        h1, h2 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 5px 0; }
        a { text-decoration: none; color: #0066cc; }
        a:hover { text-decoration: underline; }
    </style>
    <script>
        // specific function to generate links relative to the current host IP
        function writeLink(port, text) {
            var host = window.location.hostname;
            var url = "http://" + host + ":" + port;
            document.write('<a href="' + url + '" class="service-link" target="_blank">' + text + '</a>');
        }
    </script>
</head>
<body>
    <h1>Distributed Systems Example</h1>
    
    <div class="dashboard">
        <h2>Active Services</h2>
        <p>Use the links below to access the different components of the lab:</p>
        {% for service in services %}
        <div class="service-item">
            <strong>{{ service.name }}:</strong>
            {% if service.name == "UDP Backend Server" %}
                <span>Port {{ service.port }} (UDP - Internal Only)</span>
            {% else %}
                <script>writeLink({{ service.port }}, "Open on Port {{ service.port }}");</script>
            {% endif %}
            <span class="note">- {{ service.desc }}</span>
        </div>
        {% endfor %}
    </div>

    <hr>

    <h2>Project Files</h2>
    <p>Current Directory: {{ current_path }}</p>
    
    <h3>Folders</h3>
    <ul>
        {% for folder in folders %}
        <li>📂 <a href="/navigate?path={{ folder }}">{{ folder }}</a></li>
        {% endfor %}
    </ul>
    
    <h3>Files</h3>
    <ul>
        {% for file in files %}
        <li>📄 <a href="/view?path={{ file }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
    
    {% if current_path != base_dir %}
    <br>
    <a href="/">⬅ Back to Base Directory</a>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    """Entry point: List contents and show dashboard"""
    contents = list_directory(BASE_DIR)
    return render_template_string(HTML_TEMPLATE, 
                                  current_path=BASE_DIR, 
                                  base_dir=BASE_DIR,
                                  services=LAB_SERVICES,
                                  **contents)

def list_directory(path):
    """Helper function to list contents of a directory"""
    try:
        contents = os.listdir(path)
        contents.sort()
        return {
            "folders": [item for item in contents if os.path.isdir(os.path.join(path, item))],
            "files": [item for item in contents if os.path.isfile(os.path.join(path, item))]
        }
    except Exception as e:
        return {"folders": [], "files": [], "error": str(e)}

@app.route("/navigate", methods=["GET"])
def navigate():
    folder_name = request.args.get("path")
    if not folder_name: abort(400)
    new_path = os.path.join(BASE_DIR, folder_name)
    if os.path.isdir(new_path):
        contents = list_directory(new_path)
        return render_template_string(HTML_TEMPLATE, 
                                      current_path=new_path, 
                                      base_dir=BASE_DIR,
                                      services=LAB_SERVICES,
                                      **contents)
    else: abort(404)

@app.route("/view", methods=["GET"])
def view_file():
    file_name = request.args.get("path")
    if not file_name: abort(400)
    file_path = os.path.join(BASE_DIR, file_name)
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r") as file: content = file.read()
            return f"<h1>Contents of {file_name}</h1><pre>{content}</pre><a href='/'>Go Back</a>"
        except Exception as e: abort(500, description=str(e))
    else: abort(404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)