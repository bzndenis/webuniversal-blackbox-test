#!/usr/bin/env python
"""
Command Line Interface for Black-Box Testing Tool.
"""

import argparse
import asyncio
import sys
import os
import json
import logging
from typing import List, Optional

# Ensure app directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CLI")

# Import runners and services
from app.runners.crawl import crawl_site, crawl_site_with_auth
from app.runners.playwright_runner import run_page_smoke, run_yaml_scenario
from app.services.stress_test import create_stress_test_config, run_stress_test
from app.services.load_generator import create_load_generator_config, run_load_test

def setup_windows_event_loop():
    """Set up the correct event loop policy for Windows."""
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def cmd_crawl(args):
    """Handle crawl command."""
    print(f"🕷️ Starting crawl of {args.url}")
    
    if args.auth_user and args.auth_pass:
        auth_config = {
            "enabled": True,
            "url": args.login_url or args.url,
            "credentials": {
                "username": args.auth_user,
                "password": args.auth_pass
            },
            "success_indicator": args.auth_success
        }
        urls = crawl_site_with_auth(
            base_url=args.url,
            max_depth=args.depth,
            max_pages=args.max_pages,
            same_origin_only=not args.cross_origin,
            timeout=args.timeout,
            auth=auth_config,
            headless=not args.headed
        )
    else:
        urls = crawl_site(
            base_url=args.url,
            max_depth=args.depth,
            max_pages=args.max_pages,
            same_origin_only=not args.cross_origin,
            timeout=args.timeout
        )
    
    print(f"✅ Found {len(urls)} URLs:")
    for url in urls:
        print(f"  - {url}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(urls, f, indent=2)
        print(f"💾 Results saved to {args.output}")

def cmd_smoke(args):
    """Handle smoke test command."""
    print(f"🔥 Starting smoke test for {args.url}")
    
    auth_config = None
    if args.auth_user and args.auth_pass:
        auth_config = {
            "enabled": True,
            "url": args.login_url or args.url,
            "credentials": {
                "username": args.auth_user,
                "password": args.auth_pass
            },
            "success_indicator": args.auth_success
        }
    
    result = run_page_smoke(
        url=args.url,
        out_dir=args.out_dir,
        timeout=args.timeout * 1000,
        headless=not args.headed,
        deep_component_test=args.deep,
        test_forms=args.forms,
        auth=auth_config,
        enable_xss_test=args.xss,
        enable_sql_test=args.sql
    )
    
    print(f"🏁 Test finished with status: {result.get('status')}")
    print(f"📄 Report saved to {args.out_dir}")

async def run_stress_async(args):
    """Async handler for stress test."""
    config = create_stress_test_config(
        url=args.url,
        concurrent_users=args.users,
        duration_seconds=args.duration,
        ramp_up_seconds=args.ramp_up,
        think_time_seconds=args.think_time,
        timeout_seconds=args.timeout,
        headless=not args.headed
    )
    
    print(f"⚡ Starting stress test on {args.url}")
    print(f"👥 Users: {args.users}, ⏱️ Duration: {args.duration}s")
    
    summary = await run_stress_test(config)
    
    print("\n📊 Stress Test Results:")
    print(f"  Total Requests: {summary.total_requests}")
    print(f"  Success Rate: {summary.success_rate:.2f}%")
    print(f"  Avg Response Time: {summary.avg_response_time:.4f}s")
    print(f"  RPS: {summary.requests_per_second:.2f}")
    
    if args.output:
        # Convert dataclass to dict for JSON serialization
        import dataclasses
        with open(args.output, 'w') as f:
            json.dump(dataclasses.asdict(summary), f, indent=2)
        print(f"💾 Results saved to {args.output}")

def cmd_stress(args):
    """Handle stress test command."""
    setup_windows_event_loop()
    asyncio.run(run_stress_async(args))

async def run_load_async(args):
    """Async handler for load test."""
    config = create_load_generator_config(
        target_url=args.url,
        virtual_users=args.users,
        duration_seconds=args.duration,
        ramp_up_seconds=args.ramp_up,
        ramp_down_seconds=args.ramp_down,
        think_time_seconds=args.think_time,
        timeout_seconds=args.timeout,
        headless=not args.headed
    )
    
    print(f"🚀 Starting load test on {args.url}")
    print(f"👥 Virtual Users: {args.users}, ⏱️ Duration: {args.duration}s")
    
    result = await run_load_test(config)
    
    print("\n📈 Load Test Results:")
    print(f"  Total Requests: {result.total_requests}")
    print(f"  Success Rate: {result.success_rate:.2f}%")
    print(f"  Avg Response Time: {result.avg_response_time:.4f}s")
    print(f"  Avg RPS: {result.average_rps:.2f}")
    print(f"  Peak RPS: {result.peak_rps:.2f}")
    
    if args.output:
        import dataclasses
        with open(args.output, 'w') as f:
            # Helper to handle Enum serialization
            class EnhancedJSONEncoder(json.JSONEncoder):
                def default(self, o):
                    if dataclasses.is_dataclass(o):
                        return dataclasses.asdict(o)
                    if hasattr(o, 'value'):  # For Enum
                        return o.value
                    return super().default(o)
            
            json.dump(result, f, indent=2, cls=EnhancedJSONEncoder)
        print(f"💾 Results saved to {args.output}")

def cmd_load(args):
    """Handle load test command."""
    setup_windows_event_loop()
    asyncio.run(run_load_async(args))

def main():
    parser = argparse.ArgumentParser(description="Black-Box Testing Tool CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Crawl Command
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a website")
    crawl_parser.add_argument("url", help="Base URL to crawl")
    crawl_parser.add_argument("--depth", type=int, default=2, help="Max depth")
    crawl_parser.add_argument("--max-pages", type=int, default=50, help="Max pages")
    crawl_parser.add_argument("--cross-origin", action="store_true", help="Allow cross-origin")
    crawl_parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds")
    crawl_parser.add_argument("--output", help="Output JSON file")
    crawl_parser.add_argument("--headed", action="store_true", help="Run in headed mode")
    # Auth args
    crawl_parser.add_argument("--auth-user", help="Username for auth")
    crawl_parser.add_argument("--auth-pass", help="Password for auth")
    crawl_parser.add_argument("--login-url", help="Login URL (default: base URL)")
    crawl_parser.add_argument("--auth-success", help="Success indicator selector")

    # Smoke Test Command
    smoke_parser = subparsers.add_parser("smoke", help="Run smoke test on a page")
    smoke_parser.add_argument("url", help="URL to test")
    smoke_parser.add_argument("--out-dir", default="test_results", help="Output directory")
    smoke_parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds")
    smoke_parser.add_argument("--headed", action="store_true", help="Run in headed mode")
    smoke_parser.add_argument("--deep", action="store_true", help="Deep component test")
    smoke_parser.add_argument("--forms", action="store_true", help="Test forms")
    smoke_parser.add_argument("--xss", action="store_true", help="Enable XSS test")
    smoke_parser.add_argument("--sql", action="store_true", help="Enable SQL injection test")
    # Auth args
    smoke_parser.add_argument("--auth-user", help="Username for auth")
    smoke_parser.add_argument("--auth-pass", help="Password for auth")
    smoke_parser.add_argument("--login-url", help="Login URL")
    smoke_parser.add_argument("--auth-success", help="Success indicator selector")

    # Stress Test Command
    stress_parser = subparsers.add_parser("stress", help="Run stress test")
    stress_parser.add_argument("url", help="Target URL")
    stress_parser.add_argument("--users", type=int, default=10, help="Concurrent users")
    stress_parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    stress_parser.add_argument("--ramp-up", type=int, default=10, help="Ramp up seconds")
    stress_parser.add_argument("--think-time", type=float, default=1.0, help="Think time seconds")
    stress_parser.add_argument("--timeout", type=int, default=30, help="Request timeout")
    stress_parser.add_argument("--headed", action="store_true", help="Run in headed mode")
    stress_parser.add_argument("--output", help="Output JSON file")

    # Load Test Command
    load_parser = subparsers.add_parser("load", help="Run load test (Enterprise)")
    load_parser.add_argument("url", help="Target URL")
    load_parser.add_argument("--users", type=int, default=10, help="Virtual users")
    load_parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    load_parser.add_argument("--ramp-up", type=int, default=10, help="Ramp up seconds")
    load_parser.add_argument("--ramp-down", type=int, default=10, help="Ramp down seconds")
    load_parser.add_argument("--think-time", type=float, default=1.0, help="Think time seconds")
    load_parser.add_argument("--timeout", type=int, default=30, help="Request timeout")
    load_parser.add_argument("--headed", action="store_true", help="Run in headed mode")
    load_parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()
    
    if args.command == "crawl":
        cmd_crawl(args)
    elif args.command == "smoke":
        cmd_smoke(args)
    elif args.command == "stress":
        cmd_stress(args)
    elif args.command == "load":
        cmd_load(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
