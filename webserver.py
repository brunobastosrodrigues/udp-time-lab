import os
from flask import Flask, render_template_string, request, abort

app = Flask(__name__)

# Base directory for navigation
BASE_DIR = os.getcwd()

# HTML Template for rendering
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Folder Navigation API</title>
</head>
<body>
    <h1>Folder Navigation API</h1>
    <p>Current Directory: {{ current_path }}</p>
    <h2>Folders</h2>
    <ul>
        {% for folder in folders %}
        <li><a href="/navigate?path={{ folder }}">{{ folder }}</a></li>
        {% endfor %}
    </ul>
    <h2>Files</h2>
    <ul>
        {% for file in files %}
        <li><a href="/view?path={{ file }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
    <a href="/">Go to Base Directory</a>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    """Entry point: List contents of the base directory"""
    contents = list_directory(BASE_DIR)
    return render_template_string(HTML_TEMPLATE, current_path=BASE_DIR, **contents)

def list_directory(path):
    """Helper function to list contents of a directory"""
    try:
        contents = os.listdir(path)
        return {
            "folders": [item for item in contents if os.path.isdir(os.path.join(path, item))],
            "files": [item for item in contents if os.path.isfile(os.path.join(path, item))]
        }
    except Exception as e:
        return {"error": str(e)}

@app.route("/navigate", methods=["GET"])
def navigate():
    """Navigate to a folder and list its contents"""
    folder_name = request.args.get("path")
    if not folder_name:
        abort(400, description="Path parameter is required")

    new_path = os.path.join(BASE_DIR, folder_name)
    if os.path.isdir(new_path):
        contents = list_directory(new_path)
        return render_template_string(HTML_TEMPLATE, current_path=new_path, **contents)
    else:
        abort(404, description="Folder not found")

@app.route("/view", methods=["GET"])
def view_file():
    """View the contents of a file"""
    file_name = request.args.get("path")
    if not file_name:
        abort(400, description="Path parameter is required")

    file_path = os.path.join(BASE_DIR, file_name)
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r") as file:
                content = file.read()
            return f"<h1>Contents of {file_name}</h1><pre>{content}</pre><a href='/'>Go Back</a>"
        except Exception as e:
            abort(500, description=f"Error reading file: {str(e)}")
    else:
        abort(404, description="File not found")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)