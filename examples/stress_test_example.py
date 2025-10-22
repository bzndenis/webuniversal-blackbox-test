#!/usr/bin/env python3
"""
Contoh penggunaan stress test untuk menguji performa web application.
File ini menunjukkan cara menggunakan stress test service secara langsung.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from app.services.stress_test import create_stress_test_config, run_stress_test

async def basic_stress_test():
    """Contoh stress test dasar."""
    print("🚀 Menjalankan Basic Stress Test...")
    
    # Konfigurasi stress test
    config = create_stress_test_config(
        url="https://httpbin.org/delay/1",  # URL yang akan di-test
        concurrent_users=5,                 # 5 user bersamaan
        duration_seconds=30,               # Test selama 30 detik
        ramp_up_seconds=5,                # Ramp up 5 detik
        think_time_seconds=0.5,           # Think time 0.5 detik
        timeout_seconds=10,              # Timeout 10 detik
        headless=True                     # Mode headless
    )
    
    # Jalankan stress test
    results = await run_stress_test(config)
    
    # Tampilkan hasil
    print(f"\n📊 Hasil Stress Test:")
    print(f"Total Requests: {results.total_requests}")
    print(f"Success Rate: {results.success_rate:.1f}%")
    print(f"Average Response Time: {results.avg_response_time:.2f}s")
    print(f"Requests per Second: {results.requests_per_second:.1f}")
    
    if results.errors:
        print(f"\n❌ Errors:")
        for error_type, count in results.errors.items():
            print(f"  {error_type}: {count}")

async def advanced_stress_test():
    """Contoh stress test dengan aksi tambahan."""
    print("\n🚀 Menjalankan Advanced Stress Test...")
    
    # Aksi tambahan yang akan dilakukan
    actions = [
        {"type": "wait", "seconds": 1},
        {"type": "click", "selector": "button"},
        {"type": "fill", "selector": "input", "value": "test"},
        {"type": "wait", "seconds": 0.5}
    ]
    
    config = create_stress_test_config(
        url="https://httpbin.org/forms/post",
        concurrent_users=3,
        duration_seconds=20,
        ramp_up_seconds=3,
        think_time_seconds=1.0,
        timeout_seconds=15,
        headless=True,
        actions=actions
    )
    
    results = await run_stress_test(config)
    
    print(f"\n📊 Hasil Advanced Stress Test:")
    print(f"Total Requests: {results.total_requests}")
    print(f"Success Rate: {results.success_rate:.1f}%")
    print(f"Average Response Time: {results.avg_response_time:.2f}s")
    print(f"95th Percentile: {results.p95_response_time:.2f}s")
    print(f"99th Percentile: {results.p99_response_time:.2f}s")

async def high_load_stress_test():
    """Contoh stress test dengan beban tinggi."""
    print("\n🚀 Menjalankan High Load Stress Test...")
    
    config = create_stress_test_config(
        url="https://httpbin.org/status/200",
        concurrent_users=20,              # 20 user bersamaan
        duration_seconds=60,             # Test selama 1 menit
        ramp_up_seconds=10,             # Ramp up 10 detik
        think_time_seconds=0.1,          # Think time sangat cepat
        timeout_seconds=5,               # Timeout pendek
        headless=True
    )
    
    results = await run_stress_test(config)
    
    print(f"\n📊 Hasil High Load Stress Test:")
    print(f"Total Requests: {results.total_requests}")
    print(f"Success Rate: {results.success_rate:.1f}%")
    print(f"Average Response Time: {results.avg_response_time:.2f}s")
    print(f"Max Response Time: {results.max_response_time:.2f}s")
    print(f"Requests per Second: {results.requests_per_second:.1f}")
    
    if results.errors:
        print(f"\n❌ Error Analysis:")
        for error_type, count in results.errors.items():
            percentage = (count / results.total_requests * 100)
            print(f"  {error_type}: {count} ({percentage:.1f}%)")

async def main():
    """Fungsi utama untuk menjalankan semua contoh."""
    print("🔍 Black-Box Testing Tool - Stress Test Examples")
    print("=" * 50)
    
    try:
        # Jalankan contoh-contoh stress test
        await basic_stress_test()
        await advanced_stress_test()
        await high_load_stress_test()
        
        print("\n✅ Semua contoh stress test selesai!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Jalankan stress test examples
    asyncio.run(main())
