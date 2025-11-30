import os
import socket
from flask import Flask, render_template_string, request, abort

app = Flask(__name__)

# Base directory for navigation
BASE_DIR = os.getcwd()

# Extended Configuration for the Dashboard
# Added 'role', 'protocol', and 'slide' to help students connect dots
LAB_SERVICES = [
    {
        "name": "File Browser (This Page)",
        "port": 5000,
        "role": "Tool",
        "protocol": "HTTP",
        "desc": "Navigates the code files inside the container.",
        "slide": "Slide 30"
    },
    {
        "name": "Simple Time Server",
        "port": 5002,
        "role": "Server",
        "protocol": "HTTP (REST)",
        "desc": "A basic API returning time directly to the browser.",
        "slide": "Slide 31"
    },
    {
        "name": "UDP Web Client",
        "port": 5001,
        "role": "Client / Frontend",
        "protocol": "HTTP + UDP",
        "desc": "The User Interface that talks to the Backend.",
        "slide": "Slide 34"
    },
    {
        "name": "UDP Backend Server",
        "port": 5678,
        "role": "Backend Server",
        "protocol": "UDP",
        "desc": "Internal time source. Does not have a web page.",
        "slide": "Slide 33"
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Distributed Systems Lab Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({startOnLoad:true});</script>
    
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 950px; margin: 0 auto; }
        
        /* Header */
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #2c3e50; margin: 0; }
        .header p { color: #7f8c8d; }

        /* Card Style */
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 25px; }
        h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; margin-top: 0; }

        /* Service Grid */
        .service-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .service-card { border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; transition: transform 0.2s; background: #fff; }
        .service-card:hover { transform: translateY(-3px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-color: #3498db; }
        .service-title { font-weight: bold; font-size: 1.1em; color: #2980b9; margin-bottom: 5px; display: block; text-decoration: none; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: bold; margin-right: 5px; }
        .badge-http { background: #d4edda; color: #155724; }
        .badge-udp { background: #fff3cd; color: #856404; }
        .badge-tool { background: #e2e3e5; color: #383d41; }
        
        /* Diagram container */
        .diagram-container { text-align: center; overflow-x: auto; }

        /* File Browser */
        ul { list-style: none; padding: 0; }
        li { padding: 8px 0; border-bottom: 1px solid #eee; }
        li a { text-decoration: none; color: #333; font-family: monospace; font-size: 1.1em; }
        li a:hover { color: #2980b9; text-decoration: underline; }
        
        /* Instructions */
        .steps { counter-reset: step; list-style: none; padding: 0; }
        .steps li { position: relative; padding-left: 40px; margin-bottom: 15px; }
        .steps li:before { content: counter(step); counter-increment: step; position: absolute; left: 0; top: 0; width: 30px; height: 30px; background: #2980b9; color: white; text-align: center; line-height: 30px; border-radius: 50%; font-weight: bold; }
    </style>
    
    <script>
        // JS hack to inject current Host IP into links
        function writeLink(port, text, role, protocol, desc, slide) {
            var host = window.location.hostname;
            var url = "http://" + host + ":" + port;
            
            var badgeClass = protocol.includes("UDP") ? "badge-udp" : "badge-http";
            if(role === "Tool") badgeClass = "badge-tool";

            var html = `
            <div class="service-card">
                <a href="${url}" target="_blank" class="service-title">${text} ↗</a>
                <div style="margin-bottom: 8px;">
                    <span class="badge ${badgeClass}">${protocol}</span>
                    <span class="badge badge-tool">${slide}</span>
                </div>
                <p style="font-size: 0.9em; color: #666; margin: 0;">${desc}</p>
            </div>
            `;
            document.write(html);
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Distributed Systems Lab</h1>
            <p>Container Orchestration & Network Protocols</p>
        </div>

        <div class="card">
            <h2>🏗️ System Architecture</h2>
            <p>This diagram represents the 4 Docker containers currently running on this machine.</p>
            <div class="diagram-container">
                <div class="mermaid">
                    graph LR
                        User((Web User)) 
                        style User fill:#f9f,stroke:#333,stroke-width:2px

                        subgraph Docker_Network [Virtual Docker Network]
                            direction LR
                            FB[File Browser<br>Port 5000]:::tool
                            STS[Simple Time Svr<br>Port 5002]:::http
                            WC[UDP Client<br>Port 5001]:::http
                            BE[UDP Backend<br>Port 5678]:::udp
                        end

                        User -- HTTP --> FB
                        User -- HTTP --> STS
                        User -- HTTP --> WC
                        WC -- UDP Request --> BE
                        BE -. UDP Reply .-> WC

                        classDef tool fill:#e2e3e5,stroke:#333;
                        classDef http fill:#d4edda,stroke:#155724;
                        classDef udp fill:#fff3cd,stroke:#856404;
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🚀 Active Services</h2>
            <div class="service-grid">
                {% for service in services %}
                    {% if service.name == "UDP Backend Server" %}
                    <div class="service-card" style="background: #fafafa; border-style: dashed;">
                        <span class="service-title" style="color: #7f8c8d; cursor: default;">{{ service.name }}</span>
                        <div style="margin-bottom: 8px;">
                            <span class="badge badge-udp">UDP</span>
                            <span class="badge badge-tool">{{ service.slide }}</span>
                        </div>
                        <p style="font-size: 0.9em; color: #666; margin: 0;">Internal Only. Accessed via Client.</p>
                    </div>
                    {% else %}
                        <script>writeLink({{ service.port }}, "{{ service.name }}", "{{ service.role }}", "{{ service.protocol }}", "{{ service.desc }}", "{{ service.slide }}");</script>
                    {% endif %}
                {% endfor %}
            </div>
        </div>

        <div class="card">
            <h2>🎓 Lab Instructions</h2>
            <ul class="steps">
                <li><strong>Explore the Code:</strong> Use the file browser below to look at <code>udp-client.py</code> vs <code>udp-backend.py</code>. Note the difference between <code>socket.sendto</code> (Client) and <code>socket.bind</code> (Server).</li>
                <li><strong>Test HTTP (Slide 31):</strong> Open the <b>Simple Time Server</b>. Note that your browser talks directly to the server.</li>
                <li><strong>Test UDP (Slide 34):</strong> Open the <b>UDP Web Client</b>. Click "Sync". Note that your browser talks to the Client, which then talks to the Backend.</li>
                <li><strong>Simulate Failure (Slide 19):</strong> In the UDP Web Client, try the "Chaos Engineering" buttons to crash the backend and observe the timeouts.</li>
            </ul>
        </div>

        <div class="card">
            <h2>📂 Source Code Explorer</h2>
            <p><strong>Current Directory:</strong> {{ current_path }}</p>
            
            {% if current_path != base_dir %}
            <p><a href="/" style="font-weight: bold; text-decoration: none;">⬅ Back to Root</a></p>
            {% endif %}

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
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    contents = list_directory(BASE_DIR)
    return render_template_string(HTML_TEMPLATE, current_path=BASE_DIR, base_dir=BASE_DIR, services=LAB_SERVICES, **contents)

def list_directory(path):
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
        return render_template_string(HTML_TEMPLATE, current_path=new_path, base_dir=BASE_DIR, services=LAB_SERVICES, **contents)
    else: abort(404)

@app.route("/view", methods=["GET"])
def view_file():
    file_name = request.args.get("path")
    if not file_name: abort(400)
    file_path = os.path.join(BASE_DIR, file_name)
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r") as file: content = file.read()
            # Added basic styling for the file viewer
            return f"""
            <html>
            <body style="font-family: monospace; background: #f4f7f6; padding: 20px;">
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h2 style="margin-top:0; color: #2c3e50;">📄 {file_name}</h2>
                    <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 5px; overflow-x: auto;">{content}</pre>
                    <a href="/" style="display: inline-block; margin-top: 15px; text-decoration: none; background: #2980b9; color: white; padding: 8px 15px; border-radius: 4px;">⬅ Back to Dashboard</a>
                </div>
            </body>
            </html>
            """
        except Exception as e: abort(500, description=str(e))
    else: abort(404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)