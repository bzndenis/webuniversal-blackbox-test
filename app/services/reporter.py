"""Report generation service for HTML, CSV, and JSON formats."""

from jinja2 import Template
from typing import List, Dict, Any
import json
import csv
from datetime import datetime
import os

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Black-Box Test Report - {{ run_id }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        .container { 
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }
        h1 { 
            font-size: 32px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .meta {
            opacity: 0.9;
            font-size: 14px;
            margin-top: 10px;
        }
        .summary { 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .metric { 
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .metric:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .metric-value { 
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .metric-label { 
            color: #666;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .content {
            padding: 30px;
        }
        h2 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        table { 
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        th { 
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        td { 
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }
        tr:hover { 
            background: #f8f9fa;
        }
        tr:last-child td {
            border-bottom: none;
        }
        .pass { 
            color: #28a745;
            font-weight: bold;
        }
        .fail { 
            color: #dc3545;
            font-weight: bold;
        }
        .error { 
            color: #fd7e14;
            font-weight: bold;
        }
        .warning {
            color: #ffc107;
            font-weight: bold;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        .badge-danger {
            background: #f8d7da;
            color: #721c24;
        }
        .badge-warning {
            background: #fff3cd;
            color: #856404;
        }
        .url-cell {
            max-width: 400px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .url-cell:hover {
            white-space: normal;
            word-break: break-all;
        }
        .footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Black-Box Test Report</h1>
            <div class="meta">
                <strong>Run ID:</strong> {{ run_id }}<br>
                <strong>Generated:</strong> {{ timestamp }}
            </div>
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value">{{ total_pages }}</div>
                <div class="metric-label">Total Pages</div>
            </div>
            <div class="metric">
                <div class="metric-value {{ 'pass' if pass_rate >= 80 else 'fail' if pass_rate < 50 else 'warning' }}">
                    {{ pass_rate }}%
                </div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value {{ 'pass' if avg_load_time < 3000 else 'warning' if avg_load_time < 5000 else 'error' }}">
                    {{ avg_load_time }}ms
                </div>
                <div class="metric-label">Avg Load Time</div>
            </div>
            <div class="metric">
                <div class="metric-value {{ 'error' if total_console_errors > 0 else 'pass' }}">
                    {{ total_console_errors }}
                </div>
                <div class="metric-label">Console Errors</div>
            </div>
            <div class="metric">
                <div class="metric-value {{ 'error' if total_network_fails > 0 else 'pass' }}">
                    {{ total_network_fails }}
                </div>
                <div class="metric-label">Network Failures</div>
            </div>
            <div class="metric">
                <div class="metric-value">{{ total_forms }}</div>
                <div class="metric-label">Forms Found</div>
            </div>
        </div>
        
        <div class="content">
            <h2>📊 Test Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>URL</th>
                        <th>Status</th>
                        <th>HTTP</th>
                        <th>Load (ms)</th>
                        <th>Console</th>
                        <th>Network</th>
                        <th>Assertions</th>
                        <th>Forms</th>
                    </tr>
                </thead>
                <tbody>
                    {% for result in results %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td class="url-cell" title="{{ result.url }}">{{ result.url }}</td>
                        <td>
                            {% if result.status == 'PASS' %}
                                <span class="badge badge-success">✓ PASS</span>
                            {% elif result.status == 'ERROR' %}
                                <span class="badge badge-danger">✗ ERROR</span>
                            {% else %}
                                <span class="badge badge-warning">{{ result.status }}</span>
                            {% endif %}
                        </td>
                        <td>{{ result.http_status or 'N/A' }}</td>
                        <td>{{ result.load_ms or 'N/A' }}</td>
                        <td class="{{ 'error' if result.console_errors|length > 0 else '' }}">
                            {{ result.console_errors|length }}
                        </td>
                        <td class="{{ 'error' if result.network_failures|length > 0 else '' }}">
                            {{ result.network_failures|length }}
                        </td>
                        <td>
                            {% set passed = result.assertions|selectattr('pass')|list|length %}
                            {% set total = result.assertions|length %}
                            <span class="{{ 'pass' if passed == total else 'warning' }}">
                                {{ passed }}/{{ total }}
                            </span>
                        </td>
                        <td>{{ result.forms_found }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Generated by Black-Box Testing Tool v1.0 | Powered by Playwright
        </div>
    </div>
</body>
</html>
"""


def generate_html_report(
    results: List[Dict[str, Any]],
    output_path: str,
    run_id: str
) -> None:
    """
    Generate HTML report from test results.
    
    Args:
        results: List of test results
        output_path: Path to save HTML report
        run_id: Unique run identifier
    """
    total_pages = len(results)
    
    if total_pages == 0:
        passed = 0
        pass_rate = 0
        total_console_errors = 0
        total_network_fails = 0
        avg_load_time = 0
        total_forms = 0
    else:
        passed = sum(1 for r in results if r.get("status") == "PASS")
        pass_rate = int((passed / total_pages * 100))
        total_console_errors = sum(len(r.get("console_errors", [])) for r in results)
        total_network_fails = sum(len(r.get("network_failures", [])) for r in results)
        
        load_times = [r.get("load_ms", 0) for r in results if r.get("load_ms")]
        avg_load_time = int(sum(load_times) / len(load_times)) if load_times else 0
        
        total_forms = sum(r.get("forms_found", 0) for r in results)
    
    template = Template(HTML_TEMPLATE)
    html = template.render(
        run_id=run_id,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_pages=total_pages,
        pass_rate=pass_rate,
        avg_load_time=avg_load_time,
        total_console_errors=total_console_errors,
        total_network_fails=total_network_fails,
        total_forms=total_forms,
        results=results
    )
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def generate_csv_report(
    results: List[Dict[str, Any]],
    output_path: str
) -> None:
    """
    Generate CSV report from test results.
    
    Args:
        results: List of test results
        output_path: Path to save CSV report
    """
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'URL',
            'Status',
            'HTTP Status',
            'Load Time (ms)',
            'Console Errors',
            'Console Warnings',
            'Network Failures',
            'Assertions Passed',
            'Assertions Total',
            'Forms Found',
            'Buttons Found',
            'Timestamp'
        ])
        
        for result in results:
            passed = sum(1 for a in result.get("assertions", []) if a.get("pass"))
            total = len(result.get("assertions", []))
            
            writer.writerow([
                result.get("url"),
                result.get("status"),
                result.get("http_status", ""),
                result.get("load_ms", ""),
                len(result.get("console_errors", [])),
                len(result.get("console_warnings", [])),
                len(result.get("network_failures", [])),
                passed,
                total,
                result.get("forms_found", 0),
                result.get("buttons_found", 0),
                result.get("timestamp", "")
            ])


def generate_json_report(
    results: List[Dict[str, Any]],
    output_path: str,
    run_id: str = None
) -> None:
    """
    Generate JSON report from test results.
    
    Args:
        results: List of test results
        output_path: Path to save JSON report
        run_id: Optional run ID to include
    """
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    report = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_pages": len(results),
            "passed": sum(1 for r in results if r.get("status") == "PASS"),
            "failed": sum(1 for r in results if r.get("status") != "PASS"),
            "total_console_errors": sum(len(r.get("console_errors", [])) for r in results),
            "total_network_failures": sum(len(r.get("network_failures", [])) for r in results),
        },
        "results": results
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def generate_all_reports(
    results: List[Dict[str, Any]],
    output_dir: str,
    run_id: str
) -> Dict[str, str]:
    """
    Generate all report formats (HTML, CSV, JSON).
    
    Args:
        results: List of test results
        output_dir: Directory to save reports
        run_id: Unique run identifier
        
    Returns:
        Dictionary with paths to generated reports
    """
    os.makedirs(output_dir, exist_ok=True)
    
    html_path = os.path.join(output_dir, "report.html")
    csv_path = os.path.join(output_dir, "report.csv")
    json_path = os.path.join(output_dir, "report.json")
    
    generate_html_report(results, html_path, run_id)
    generate_csv_report(results, csv_path)
    generate_json_report(results, json_path, run_id)
    
    return {
        "html": html_path,
        "csv": csv_path,
        "json": json_path
    }

