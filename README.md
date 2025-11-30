# Distributed Systems Example

This project is a live demonstration for the **Distributed Systems** lecture. It provides a hands-on environment to explore key concepts such as Client-Server architecture, Web APIs (HTTP), UDP communication, and Fault Tolerance using Docker containers.

## 📋 Prerequisites

To run this lab, you need **Docker** installed on your machine.
* [Get Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac/Windows)
* [Get Docker Engine](https://docs.docker.com/engine/install/ubuntu/) (Linux)

---

## 🚀 Quick Start

**1. Clone the repository**
Open your terminal or command prompt and run:

```bash
git clone [https://github.com/brunobastosrodrigues/udp-time-lab.git](https://github.com/brunobastosrodrigues/udp-time-lab.git)
cd udp-time-lab
````

**2. Start the Environment**
Run the following command to build and start the simulated network:

```bash
docker compose up --build
```

*(Wait a few moments until you see the logs stop scrolling and services are listed as "Started")*

**3. Access the Dashboard**
Open your web browser and go to:

> **http://localhost:5000**

*(Note: If you are running this on a cloud VM, replace `localhost` with your VM's Public IP address).*

-----

## 🗺️ System Architecture

The project orchestrates 4 isolated containers to simulate a distributed network. You can view the live architecture diagram in the **Dashboard**.

| Service | Port | Role | Description |
| :--- | :--- | :--- | :--- |
| **Dashboard** | `5000` | **Map / Tool** | The starting point. Contains the file browser, system diagram, and navigation links. |
| **UDP Web Client** | `5001` | **Client (Frontend)** | The user interface that communicates with the backend via UDP. Includes **Chaos Engineering** controls. |
| **Simple Time API** | `5002` | **Server (HTTP)** | A standard synchronous HTTP server. Demonstrates direct Client-Server communication. |
| **UDP Backend** | `5678` | **Server (Backend)** | The internal time source. It has no web interface and listens only for UDP packets. |

-----

## 🎓 Demo Walkthrough

Follow these steps to reproduce the lecture demonstrations.

### Part 1: Architecture & Transparency 

1.  Open the **Dashboard (Port 5000)**.
2.  Review the **System Architecture Diagram**. Notice how the containers are isolated in a "Virtual Docker Network".
3.  Observe that as a Web User, you interact with the Frontend services (Green nodes), while the Backend (Yellow node) remains hidden from the public internet.

### Part 2: Web APIs - Human vs. Machine 

1.  Open the **Simple Time Server (Port 5002)**.
2.  Click **"👤 Human Interface"**.
      * *Observation:* You see a styled HTML page designed for people.
3.  Go back and click **"🤖 Robot Interface"**.
      * *Observation:* You see raw JSON data. This demonstrates how programs talk to each other using APIs vs how they talk to humans.

### Part 3: Distributed Communication 

1.  Open the **UDP Web Client (Port 5001)**.
2.  Click **"Sync Time"**.
      * *Observation:* Your browser sends an HTTP request to the Client Container. The Client Container then sends a UDP packet to the Backend Container, gets the time, and displays it.
      * Check the **Latency (RTT)** metric to see how long the round-trip took.

### Part 4: Fault Tolerance & Chaos Engineering 

*Simulate a "Partial Failure" where one component dies but the system survives.*

1.  Stay on the **UDP Web Client (Port 5001)**.
2.  Scroll down to **"Instructor Controls"**.
3.  Click the red **"💥 Simulate Crash"** button.
      * *Context:* This sends a command to the backend to ignore all incoming requests (simulating a network cable cut or server crash).
4.  Click **"Sync Time"** again.
      * *Observation:* The page waits for 2 seconds (Timeout).
      * *Result:* A **CRITICAL ERROR** appears. The Client detected the failure and handled it gracefully instead of crashing.
5.  Click **"🔧 Repair Server"** to restore normal operations.

-----

## 📂 File Structure

  * **`docker-compose.yml`**: The blueprint defining the 4 services and the virtual network.
  * **`webserver.py`**: The code for the Dashboard (Port 5000).
  * **`udp-client.py`**: The Frontend application logic (Port 5001).
  * **`udp-backend.py`**: The Backend logic (Port 5678), including the crash simulation code.
  * **`timeserver.py`**: The Simple HTTP API logic (Port 5002).

## 🛑 Stopping the Demo

To stop the containers and free up ports, press `Ctrl+C` in your terminal, or run:

```bash
docker compose down
```

```
```
