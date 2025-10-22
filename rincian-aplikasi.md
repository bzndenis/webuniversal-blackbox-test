# Rincian Aplikasi Black-Box Functional Testing

## Tujuan
Bangun aplikasi web Python untuk black-box functional testing per halaman situs apa pun. Aplikasi melakukan crawl terbatas, otomatis menjalankan skenario umum (load, klik, submit form, validasi teks/HTTP), mendeteksi error (HTTP 4xx/5xx, JS console error, network fail), dan menghasilkan laporan per halaman + ringkasan pass/fail. Dukungan test spesifik via berkas YAML.

---

## Persyaratan Teknis

### Opsi A: Cepat & Simpel (Direkomendasikan Awal)

- **UI**: Streamlit
- **Automation**: Playwright (Python) untuk E2E headless Chromium/Firefox/WebKit
- **Storage**: SQLite (runs, pages, results)
- **Scheduler**: Jalankan sinkron dulu; siapkan hook untuk job async nanti
- **Export laporan**: HTML/CSV/JSON

### Opsi B: Lebih Kokoh (Siap CI/CD)

- **Backend API**: FastAPI
- **Worker**: Celery + Redis (queue run)
- **Automation**: Playwright (Python)
- **Frontend**: Flask/HTMX + Bootstrap 5 (atau React minimal), layout responsive
- **DB**: SQLite (opsi upgrade ke Postgres)
- **Auth**: Dasar (API key env var)
- **Container**: Dockerfile + docker-compose

**Catatan**: Gunakan Playwright alih-alih Selenium untuk stabilitas locator, cross-browser, dan integrasi CI yang mudah.

---

## Fitur Wajib

### 1. Input Target

Field yang diperlukan:
- Base URL
- Batas domain/same-origin
- Max depth (default 1–2)
- Max pages
- Include/exclude patterns (regex)
- Opsi "manual pages list"

### 2. Crawler Ringan

- Ambil daftar halaman (same-origin)
- Hormati robots.txt (opsional)
- Hindari infinite loop
- Dedup URL

### 3. Test Otomatis Per Halaman

#### Basic Load Checks
- Status 200
- Waktu load
- Ukuran DOM
- Tidak ada 4xx/5xx dari subresource

#### Console & Network
- Catat `console.error`
- Request gagal
- Redirect berlebihan

#### Link & Elemen Penting
- Pastikan link terlihat & bisa diklik (tanpa benar-benar pindah kecuali diminta)
- Tombol utama tidak disabled tanpa alasan

#### Form Heuristics
- Deteksi form sederhana
- Isi dummy (email, text, number)
- Submit di sandbox mode
- Verifikasi tidak 500/4xx
- Ada tanda sukses/validasi

#### Assertions Generik
- Judul halaman tidak kosong
- `<h1>` ada
- Meta charset/lang ada

### 4. Test Kustom via YAML

Skema YAML mendukung:
- Daftar action & assertion
- Actions: `goto`, `click`, `fill`, `press`, `screenshot`
- Assertions: `expect_text`, `expect_status`, `expect_n_requests ≤ N`

### 5. Reporting

#### Tabel Ringkasan
- Page URL
- Status
- Load(ms)
- JS Errors
- Network Fails
- Forms Tested
- Assertions Passed/Failed

#### Detail Per Halaman
- Langkah
- Log
- Screenshot bukti (before/after submit)
- Harvester data minimal

#### Export
- HTML (rapi, warna pass/fail)
- CSV
- JSON
- Folder artifacts: `artifacts/<run_id>/`

### 6. Konfigurasi

File `.env` untuk:
- `TIMEOUT`
- `HEADLESS`
- `MAX_CONCURRENCY` (jalankan serial dulu, siapkan flag concurrency)
- `USER_AGENT`

### 7. Quality

- Type hints & docstring
- Modular (services/, models/, runners/)
- Error handling jelas
- Progress bar
- Cancel run

---

## Struktur Proyek

```
webuniversal-blackbox-test/
├── app/
│   ├── main.py                # Streamlit app (Opsi A) atau FastAPI entry (Opsi B)
│   ├── runners/
│   │   ├── __init__.py
│   │   ├── playwright_runner.py
│   │   └── crawl.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db.py              # SQLite, SQLAlchemy
│   │   └── schemas.py         # Pydantic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── yaml_loader.py
│   │   ├── reporter.py        # HTML/CSV/JSON
│   │   └── heuristics.py      # form fill rules
│   ├── static/                # CSS Bootstrap (jika Opsi B)
│   └── templates/             # report HTML (Jinja2)
├── tests/
│   ├── __init__.py
│   ├── sample_specs/
│   │   └── example.yaml
│   └── test_runner.py
├── artifacts/                 # Generated reports & screenshots
├── .env.example
├── .gitignore
├── Dockerfile                 # (Opsi B)
├── docker-compose.yml         # (Opsi B)
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Skema YAML (Contoh)

```yaml
# tests/sample_specs/example.yaml
base_url: "https://example.com"
scenarios:
  - name: "Homepage basic"
    steps:
      - action: "goto"
        url: "/"
      - action: "expect_title"
        equals: "Example Domain"
      - action: "expect_text"
        selector: "h1"
        contains: "Example"
      - action: "screenshot"
        path: "homepage.png"

  - name: "Try a link"
    steps:
      - action: "goto"
        url: "/"
      - action: "click"
        selector: "a"
      - action: "expect_status"
        in: [200, 301, 302]

  - name: "Form submission"
    steps:
      - action: "goto"
        url: "/contact"
      - action: "fill"
        selector: "input[name='email']"
        value: "test@example.com"
      - action: "fill"
        selector: "textarea[name='message']"
        value: "Test message"
      - action: "screenshot"
        path: "before_submit.png"
      - action: "click"
        selector: "button[type='submit']"
      - action: "expect_text"
        selector: ".success-message"
        contains: "Thank you"
      - action: "screenshot"
        path: "after_submit.png"
```

---

## Contoh Kode Inti

### Playwright Runner

```python
# app/runners/playwright_runner.py
from playwright.sync_api import sync_playwright, Page
from typing import Dict, Any, List, Optional
import time
import json
import os

DEFAULT_TIMEOUT = 10000

def run_page_smoke(url: str, out_dir: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Jalankan smoke test pada satu halaman.
    
    Args:
        url: URL halaman yang akan ditest
        out_dir: Direktori untuk menyimpan artifacts
        timeout: Timeout dalam ms
        
    Returns:
        Dictionary berisi hasil test
    """
    os.makedirs(out_dir, exist_ok=True)
    result = {
        "url": url,
        "status": "UNKNOWN",
        "load_ms": None,
        "console_errors": [],
        "network_failures": [],
        "assertions": [],
        "forms_found": 0,
        "forms_tested": 0
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent=os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; BlackBoxTester/1.0)")
        )
        page = context.new_page()
        page.set_default_timeout(timeout)

        # Collect console errors
        def handle_console(msg):
            if msg.type() == "error":
                result["console_errors"].append({
                    "text": msg.text(),
                    "location": msg.location
                })
        
        page.on("console", handle_console)
        
        # Collect failed requests
        def handle_request_failed(req):
            result["network_failures"].append({
                "url": req.url,
                "method": req.method,
                "failure": req.failure
            })
        
        page.on("requestfailed", handle_request_failed)

        try:
            # Navigate and measure load time
            t0 = time.time()
            resp = page.goto(url, wait_until="load", timeout=timeout)
            load_ms = int((time.time() - t0) * 1000)
            result["load_ms"] = load_ms

            # Check HTTP status
            code = resp.status if resp else None
            if code and 200 <= code < 400:
                result["status"] = "PASS"
            else:
                result["status"] = f"HTTP_{code}"

            # Basic assertions
            title = page.title()
            result["assertions"].append({
                "assert": "title_not_empty",
                "pass": bool(title),
                "actual": title
            })
            
            h1 = page.locator("h1")
            has_h1 = h1.count() > 0
            result["assertions"].append({
                "assert": "has_h1",
                "pass": has_h1,
                "count": h1.count()
            })
            
            # Check meta charset
            meta_charset = page.locator('meta[charset]').count() > 0
            result["assertions"].append({
                "assert": "has_meta_charset",
                "pass": meta_charset
            })

            # Find and analyze forms
            forms = page.locator("form")
            result["forms_found"] = forms.count()

            # Screenshot
            screenshot_path = os.path.join(out_dir, "screenshot.png")
            page.screenshot(path=screenshot_path, full_page=True)
            result["screenshot"] = screenshot_path

        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        finally:
            context.close()
            browser.close()
    
    return result


def run_yaml_scenario(scenario: Dict[str, Any], out_dir: str) -> Dict[str, Any]:
    """
    Jalankan skenario test dari YAML spec.
    
    Args:
        scenario: Dictionary berisi steps dari YAML
        out_dir: Direktori untuk artifacts
        
    Returns:
        Dictionary hasil eksekusi
    """
    os.makedirs(out_dir, exist_ok=True)
    result = {
        "name": scenario.get("name", "Unnamed"),
        "steps_executed": 0,
        "steps_passed": 0,
        "steps_failed": 0,
        "errors": []
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        try:
            for idx, step in enumerate(scenario.get("steps", [])):
                action = step.get("action")
                result["steps_executed"] += 1
                
                try:
                    if action == "goto":
                        page.goto(step["url"], wait_until="load")
                    elif action == "click":
                        page.locator(step["selector"]).first.click()
                    elif action == "fill":
                        page.locator(step["selector"]).fill(step["value"])
                    elif action == "press":
                        page.keyboard.press(step["key"])
                    elif action == "screenshot":
                        page.screenshot(path=os.path.join(out_dir, step["path"]))
                    elif action == "expect_title":
                        actual = page.title()
                        expected = step.get("equals")
                        if actual != expected:
                            raise AssertionError(f"Title mismatch: {actual} != {expected}")
                    elif action == "expect_text":
                        text = page.locator(step["selector"]).text_content()
                        contains = step.get("contains")
                        if contains and contains not in text:
                            raise AssertionError(f"Text not found: {contains} in {text}")
                    elif action == "expect_status":
                        # This would need the last response object
                        pass
                    
                    result["steps_passed"] += 1
                    
                except Exception as e:
                    result["steps_failed"] += 1
                    result["errors"].append({
                        "step": idx,
                        "action": action,
                        "error": str(e)
                    })
                    
        finally:
            context.close()
            browser.close()
    
    return result
```

### Crawler

```python
# app/runners/crawl.py
from urllib.parse import urljoin, urlparse
from typing import Set, List
import requests
from bs4 import BeautifulSoup
import re

def crawl_site(
    base_url: str,
    max_depth: int = 2,
    max_pages: int = 50,
    same_origin_only: bool = True,
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None
) -> List[str]:
    """
    Crawl website dan kumpulkan daftar URL.
    
    Args:
        base_url: URL awal
        max_depth: Kedalaman maksimal crawling
        max_pages: Jumlah halaman maksimal
        same_origin_only: Hanya crawl same-origin URLs
        include_patterns: Regex patterns untuk include
        exclude_patterns: Regex patterns untuk exclude
        
    Returns:
        List of URLs yang ditemukan
    """
    visited: Set[str] = set()
    to_visit: List[tuple] = [(base_url, 0)]  # (url, depth)
    found_urls: List[str] = []
    
    base_domain = urlparse(base_url).netloc
    
    while to_visit and len(found_urls) < max_pages:
        current_url, depth = to_visit.pop(0)
        
        if current_url in visited or depth > max_depth:
            continue
            
        # Check include/exclude patterns
        if include_patterns:
            if not any(re.search(pattern, current_url) for pattern in include_patterns):
                continue
                
        if exclude_patterns:
            if any(re.search(pattern, current_url) for pattern in exclude_patterns):
                continue
        
        visited.add(current_url)
        found_urls.append(current_url)
        
        try:
            # Fetch page
            resp = requests.get(current_url, timeout=10, allow_redirects=True)
            if resp.status_code != 200:
                continue
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(current_url, href)
                parsed = urlparse(absolute_url)
                
                # Remove fragments
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_url += f"?{parsed.query}"
                
                # Same origin check
                if same_origin_only and parsed.netloc != base_domain:
                    continue
                
                if clean_url not in visited:
                    to_visit.append((clean_url, depth + 1))
                    
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
            continue
    
    return found_urls
```

---

## UI (Opsi A – Streamlit)

### Layout
- **Sidebar**: Input untuk Base URL, Max Depth/Pages, Include/Exclude regex, tombol Run
- **Main Area**: 
  - Progress bar & log area
  - Tabel hasil dengan st.metric untuk angka ringkas
  - Link ke detail halaman (log + screenshot)
  - Tombol Export

### Komponen Utama
```python
# app/main.py
import streamlit as st
from runners.crawl import crawl_site
from runners.playwright_runner import run_page_smoke
from services.reporter import generate_html_report
import os
from datetime import datetime

st.set_page_config(page_title="Black-Box Testing Tool", layout="wide")

st.title("🔍 Black-Box Functional Testing")

# Sidebar inputs
with st.sidebar:
    st.header("Configuration")
    base_url = st.text_input("Base URL", "https://example.com")
    max_depth = st.number_input("Max Depth", 1, 5, 2)
    max_pages = st.number_input("Max Pages", 1, 100, 10)
    include_pattern = st.text_input("Include Pattern (regex)", "")
    exclude_pattern = st.text_input("Exclude Pattern (regex)", "")
    
    run_button = st.button("🚀 Run Test", type="primary")

# Main area
if run_button:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifacts_dir = f"artifacts/{run_id}"
    os.makedirs(artifacts_dir, exist_ok=True)
    
    with st.spinner("Crawling site..."):
        urls = crawl_site(
            base_url,
            max_depth=max_depth,
            max_pages=max_pages,
            include_patterns=[include_pattern] if include_pattern else None,
            exclude_patterns=[exclude_pattern] if exclude_pattern else None
        )
    
    st.success(f"Found {len(urls)} pages")
    
    # Test each page
    results = []
    progress_bar = st.progress(0)
    
    for idx, url in enumerate(urls):
        st.write(f"Testing: {url}")
        page_dir = os.path.join(artifacts_dir, f"page_{idx}")
        result = run_page_smoke(url, page_dir)
        results.append(result)
        progress_bar.progress((idx + 1) / len(urls))
    
    # Display results
    st.header("Results")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    total_pass = sum(1 for r in results if r["status"] == "PASS")
    total_errors = sum(len(r["console_errors"]) for r in results)
    total_network_fails = sum(len(r["network_failures"]) for r in results)
    avg_load = sum(r["load_ms"] for r in results if r["load_ms"]) / len(results)
    
    col1.metric("Total Pages", len(results))
    col2.metric("Passed", total_pass)
    col3.metric("Console Errors", total_errors)
    col4.metric("Avg Load Time", f"{avg_load:.0f}ms")
    
    # Results table
    st.dataframe(results)
    
    # Generate report
    report_path = os.path.join(artifacts_dir, "report.html")
    generate_html_report(results, report_path, run_id)
    
    st.success(f"Report generated: {report_path}")
```

---

## Pelaporan

### HTML Report Generator

```python
# app/services/reporter.py
from jinja2 import Template
from typing import List, Dict, Any
import json
from datetime import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Black-Box Test Report - {{ run_id }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
        .metric { background: #f9f9f9; padding: 15px; border-radius: 5px; text-align: center; }
        .metric-value { font-size: 32px; font-weight: bold; color: #4CAF50; }
        .metric-label { color: #666; font-size: 14px; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #4CAF50; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:hover { background: #f5f5f5; }
        .pass { color: #4CAF50; font-weight: bold; }
        .fail { color: #f44336; font-weight: bold; }
        .error { color: #ff9800; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Black-Box Test Report</h1>
        <p><strong>Run ID:</strong> {{ run_id }}</p>
        <p><strong>Generated:</strong> {{ timestamp }}</p>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value">{{ total_pages }}</div>
                <div class="metric-label">Total Pages</div>
            </div>
            <div class="metric">
                <div class="metric-value {{ 'pass' if pass_rate >= 80 else 'fail' }}">{{ pass_rate }}%</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value {{ 'error' if total_console_errors > 0 else '' }}">{{ total_console_errors }}</div>
                <div class="metric-label">Console Errors</div>
            </div>
            <div class="metric">
                <div class="metric-value {{ 'error' if total_network_fails > 0 else '' }}">{{ total_network_fails }}</div>
                <div class="metric-label">Network Failures</div>
            </div>
        </div>
        
        <h2>Test Results</h2>
        <table>
            <thead>
                <tr>
                    <th>URL</th>
                    <th>Status</th>
                    <th>Load Time (ms)</th>
                    <th>Console Errors</th>
                    <th>Network Fails</th>
                    <th>Assertions</th>
                </tr>
            </thead>
            <tbody>
                {% for result in results %}
                <tr>
                    <td>{{ result.url }}</td>
                    <td class="{{ 'pass' if result.status == 'PASS' else 'fail' }}">{{ result.status }}</td>
                    <td>{{ result.load_ms or 'N/A' }}</td>
                    <td class="{{ 'error' if result.console_errors|length > 0 else '' }}">{{ result.console_errors|length }}</td>
                    <td class="{{ 'error' if result.network_failures|length > 0 else '' }}">{{ result.network_failures|length }}</td>
                    <td>
                        {% set passed = result.assertions|selectattr('pass')|list|length %}
                        {% set total = result.assertions|length %}
                        {{ passed }}/{{ total }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

def generate_html_report(results: List[Dict[str, Any]], output_path: str, run_id: str):
    """Generate HTML report from test results."""
    total_pages = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    pass_rate = int((passed / total_pages * 100) if total_pages > 0 else 0)
    total_console_errors = sum(len(r.get("console_errors", [])) for r in results)
    total_network_fails = sum(len(r.get("network_failures", [])) for r in results)
    
    template = Template(HTML_TEMPLATE)
    html = template.render(
        run_id=run_id,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_pages=total_pages,
        pass_rate=pass_rate,
        total_console_errors=total_console_errors,
        total_network_fails=total_network_fails,
        results=results
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def generate_csv_report(results: List[Dict[str, Any]], output_path: str):
    """Generate CSV report from test results."""
    import csv
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'URL', 'Status', 'Load Time (ms)', 
            'Console Errors', 'Network Failures', 
            'Assertions Passed', 'Assertions Total'
        ])
        
        for result in results:
            passed = sum(1 for a in result.get("assertions", []) if a.get("pass"))
            total = len(result.get("assertions", []))
            
            writer.writerow([
                result.get("url"),
                result.get("status"),
                result.get("load_ms", ""),
                len(result.get("console_errors", [])),
                len(result.get("network_failures", [])),
                passed,
                total
            ])


def generate_json_report(results: List[Dict[str, Any]], output_path: str):
    """Generate JSON report from test results."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
```

---

## Testing & CI

### pytest Configuration

```python
# tests/test_runner.py
import pytest
from app.runners.playwright_runner import run_page_smoke
from app.runners.crawl import crawl_site
import tempfile
import os

def test_smoke_runner_basic():
    """Test basic smoke runner functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_page_smoke("https://example.com", tmpdir)
        
        assert result["status"] == "PASS"
        assert result["load_ms"] is not None
        assert result["load_ms"] > 0
        assert len(result["assertions"]) > 0
        assert os.path.exists(os.path.join(tmpdir, "screenshot.png"))


def test_crawler_basic():
    """Test basic crawler functionality."""
    urls = crawl_site("https://example.com", max_depth=1, max_pages=5)
    
    assert len(urls) > 0
    assert "https://example.com" in urls
```

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Black-Box Testing CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        playwright install --with-deps chromium
    
    - name: Run tests
      run: |
        pytest tests/ -v
    
    - name: Run sample black-box test
      run: |
        python -c "
        from app.runners.playwright_runner import run_page_smoke
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_page_smoke('https://example.com', tmpdir)
            print(f'Test result: {result[\"status\"]}')
            assert result['status'] == 'PASS'
        "
    
    - name: Upload artifacts
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-reports
        path: artifacts/
```

---

## Instalasi

### Lokal (Opsi A - Streamlit)

```bash
# Clone repository
git clone <repo-url>
cd webuniversal-blackbox-test

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install streamlit playwright jinja2 pydantic sqlmodel requests beautifulsoup4
playwright install --with-deps

# Run application
streamlit run app/main.py
```

### Docker (Opsi B)

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy application
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./artifacts:/app/artifacts
    environment:
      - HEADLESS=true
      - TIMEOUT=10000
```

---

## Batasan & Considerations

### Batasan Black-Box Testing
- **Tidak melewati authentication**: Aplikasi tidak dapat test halaman yang memerlukan login kecuali kredensial disediakan
- **CAPTCHA**: Tidak dapat bypass CAPTCHA
- **Dynamic content**: Content yang di-load via infinite scroll atau lazy loading mungkin tidak terdeteksi
- **SPA (Single Page Applications)**: Perlu wait strategy khusus

### Mode Login Opsional

Untuk halaman yang memerlukan auth, tambahkan ke YAML:

```yaml
auth:
  enabled: true
  url: "/login"
  credentials:
    username_selector: "input[name='username']"
    username_value: "testuser"
    password_selector: "input[name='password']"
    password_value: "testpass"
    submit_selector: "button[type='submit']"
  success_indicator: ".dashboard"
```

---

## Rekomendasi Stack (Ringkas)

### Opsi Tercepat
**Streamlit + Playwright (Python)**
- ✅ Fokus ke logic testing
- ✅ UI instan, 1 file bisa jalan
- ✅ Ideal untuk prototype & internal tools

### Opsi Scalable
**FastAPI + Celery + Playwright + Bootstrap 5**
- ✅ Multi-user support
- ✅ Job queue untuk concurrent testing
- ✅ API-first design
- ✅ Mudah integrasi CI/CD
- ✅ Production-ready

### Kenapa Playwright?
1. **Locator stabil**: Auto-waiting, smart selectors
2. **Cross-browser**: Chromium, Firefox, WebKit
3. **Headless ready**: Perfect untuk CI/CD
4. **Rich API**: Screenshot, video, network interception
5. **Modern**: Aktif dikembangkan, dokumentasi lengkap
6. **Python native**: Tidak perlu Selenium WebDriver setup

---

## Roadmap & Future Enhancements

### Phase 1 (MVP)
- ✅ Basic crawling
- ✅ Smoke testing per page
- ✅ HTML report
- ✅ Streamlit UI

### Phase 2
- [ ] YAML scenario support
- [ ] Form heuristics
- [ ] CSV/JSON export
- [ ] Database persistence (SQLite)

### Phase 3
- [ ] Concurrent testing
- [ ] Authentication support
- [ ] Advanced assertions
- [ ] Screenshot comparison

### Phase 4
- [ ] FastAPI backend
- [ ] Celery worker
- [ ] REST API
- [ ] Multi-project support
- [ ] Scheduled runs

---

## Dependencies

```txt
# requirements.txt
streamlit==1.28.0
playwright==1.40.0
beautifulsoup4==4.12.2
requests==2.31.0
jinja2==3.1.2
pydantic==2.5.0
sqlmodel==0.0.14
python-dotenv==1.0.0
pytest==7.4.3
```

---

## Environment Variables

```bash
# .env.example
# Application Settings
HEADLESS=true
TIMEOUT=10000
MAX_CONCURRENCY=1
USER_AGENT="Mozilla/5.0 (compatible; BlackBoxTester/1.0)"

# Database
DATABASE_URL=sqlite:///./test_runs.db

# Optional: Opsi B
REDIS_URL=redis://localhost:6379/0
API_KEY=your-secret-api-key-here
```

---

## Kesimpulan

Aplikasi ini dirancang untuk:
1. **Rapid testing**: Quickly test any website without writing code
2. **Automated QA**: Catch errors before they reach production
3. **CI/CD Integration**: Easy to integrate into deployment pipelines
4. **Flexibility**: Support both automated and custom YAML scenarios
5. **Comprehensive reporting**: Clear visibility of issues

Mulai dengan **Opsi A (Streamlit)** untuk development cepat, kemudian migrate ke **Opsi B (FastAPI)** saat butuh scalability dan multi-user support.

