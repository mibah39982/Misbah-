# ROADMAN MIND (Safe Scaffold)

Welcome to **ROADMAN MIND**, a cyber-hacker–themed AI assistant framework. This project is a safe and legal scaffold, designed for educational purposes, defensive cybersecurity, and system automation. It is built with a modular plugin system, making it easily extendable.

## 📂 Project Structure

The project is organized into a core engine, a command-line interface (CLI), a web API, and a set of pluggable modules.

- `roadman_mind/`: The main application package.
  - `core/`: Core components like the plugin system, logger, and config.
  - `plugins/`: Individual plugins that extend the application's functionality.
  - `ui/`: Web-facing components, including the FastAPI server.
  - `main.py`: The CLI entry point powered by Typer.
- `tests/`: Contains tests for the application.
- `requirements.txt`: A list of Python dependencies.

## 🚀 Getting Started

### 1. Setup a Virtual Environment

It is recommended to run this project in a virtual environment.

```bash
python -m venv .venv
# On Windows
# .\.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies

Install the required packages using pip:

```bash
pip install -r requirements.txt
```

### 3. Run the CLI

The CLI is the primary way to interact with ROADMAN MIND. You can list available commands (routes) and execute them.

**List all available routes:**
```bash
python -m roadman_mind list-routes
```

**Run a specific route:**
```bash
# Example: Check CPU usage
python -m roadman_mind run sys:cpu_percent

# Example: Get information on a sample CVE
python -m roadman_mind run osint:get_cve_2025_0001
```

### 4. Run the API Server

The project includes a FastAPI server that exposes the plugin functionality via a REST API.

**Start the server:**
```bash
uvicorn roadman_mind.ui.server:app --reload --port 8000
```

Once running, you can access the following endpoints:
- **List all routes:** `http://localhost:8000/routes`
- **Interactive API docs:** `http://localhost:8000/docs`

You can execute a route by sending a POST request to `http://localhost:8000/run` with a JSON body:
```json
{
  "name": "sys:memory"
}
```

## 🛡️ Safety Notice

This scaffold includes no offensive or hacking tools. It is intended for **legal and educational use only**, focusing on cybersecurity awareness and defensive monitoring.

## 🛣️ Roadmap

- Expand the Learning Lab with more quizzes.
- Add a personal notebook for study notes.
- Implement session journaling for tracking experiments.
- Build a React frontend dashboard.
