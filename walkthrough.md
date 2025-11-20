# Walkthrough: CLI Support and Web UI Configuration

## Overview
We have added a new Command Line Interface (CLI) to the Black-Box Testing Tool and enhanced the Web UI launcher to support custom host and port configurations.

## 1. CLI Usage (`cli.py`)
You can now run various testing tasks directly from the terminal without launching the web interface.

### Basic Usage
```bash
python cli.py [command] [options]
```

### Available Commands

#### Crawl a Website
Crawl a website to discover URLs.
```bash
python cli.py crawl https://example.com --depth 2 --max-pages 20
```
**Options:**
- `--depth`: Maximum crawl depth (default: 2)
- `--max-pages`: Maximum pages to find (default: 50)
- `--output`: Save results to a JSON file (e.g., `--output urls.json`)
- `--headed`: Run browser in visible mode (default: headless)

#### Smoke Test
Run a quick smoke test on a single page.
```bash
python cli.py smoke https://example.com/page
```
**Options:**
- `--deep`: Enable deep component testing
- `--forms`: Enable form testing
- `--xss`: Enable XSS vulnerability test
- `--sql`: Enable SQL injection test
- `--out-dir`: Directory to save reports (default: `test_results`)

#### Stress Test
Run a stress test with concurrent users.
```bash
python cli.py stress https://example.com --users 5 --duration 30
```

#### Load Test (Enterprise)
Run a load test with advanced configuration.
```bash
python cli.py load https://example.com --users 50 --duration 60
```

## 2. Web UI Configuration (`run.py`)
The web application launcher now supports command-line arguments to configure the server address and port. This allows you to make the UI accessible from other machines on your network.

### Usage
```bash
python run.py --host 0.0.0.0 --port 8501
```

**Arguments:**
- `--host`: The address to bind the server to. Use `0.0.0.0` to make it accessible from other devices on the network. Default is `localhost`.
- `--port`: The port to run the server on. Default is `8501`.

### Example: Expose to Network
To allow other computers to access the UI, run:
```bash
python run.py --host 0.0.0.0
```
Then access it via your machine's IP address, e.g., `http://192.168.1.x:8501`.
