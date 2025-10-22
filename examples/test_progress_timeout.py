#!/usr/bin/env python3
"""
Test script untuk progress monitoring timeout fix.
Menunjukkan bagaimana progress monitoring berhenti dengan benar.
"""

import asyncio
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.load_generator import AdvancedLoadGenerator, create_load_generator_config
from app.services.progress_monitor import create_progress_monitor

async def test_progress_timeout_fix():
    """Test progress monitoring timeout fix."""
    print("🚀 Testing Progress Monitoring Timeout Fix...")
    
    # Create simple load test config with short duration
    config = create_load_generator_config(
        target_url="https://httpbin.org/status/200",
        virtual_users=3,
        duration_seconds=5,  # Short duration for testing
        ramp_up_seconds=1,
        ramp_down_seconds=1,
        think_time_seconds=0.5
    )
    
    # Create load generator
    generator = AdvancedLoadGenerator(config)
    
    # Create progress monitor
    progress_monitor = create_progress_monitor()
    
    # Progress callback function
    async def progress_callback(data):
        print(f"📊 Progress: {data['progress_percent']:.1f}% | "
              f"Active: {data['active_users']} | "
              f"RPS: {data['current_rps']:.1f} | "
              f"Success: {data['success_rate']:.1f}% | "
              f"Completed: {data['completed_requests']}")
    
    # Start progress monitoring
    await progress_monitor.start_monitoring(generator, progress_callback)
    
    # Run load test with timeout
    print("🔄 Starting load test...")
    start_time = time.time()
    
    try:
        # Run with timeout
        result = await asyncio.wait_for(
            generator.run_load_test(),
            timeout=config.duration_seconds + 10  # 10 seconds buffer
        )
        
        # Stop progress monitoring
        await progress_monitor.stop_monitoring()
        
        end_time = time.time()
        
        # Show results
        print(f"\n✅ Load test completed in {end_time - start_time:.1f}s")
        print(f"📊 Total requests: {result.total_requests}")
        print(f"📊 Success rate: {result.success_rate:.1f}%")
        print(f"📊 Peak RPS: {result.peak_rps:.1f}")
        print(f"📊 Avg response time: {result.avg_response_time:.2f}s")
        
    except asyncio.TimeoutError:
        print("\n⏰ Load test timeout!")
        await progress_monitor.stop_monitoring()
        return False
    except Exception as e:
        print(f"\n❌ Error during load test: {e}")
        await progress_monitor.stop_monitoring()
        return False
    
    # Show progress history
    chart_data = progress_monitor.get_chart_data()
    if chart_data:
        print(f"\n📈 Progress data points: {len(chart_data)}")
        print("📈 Final data points:")
        for i, data in enumerate(chart_data[-3:]):  # Show last 3 data points
            print(f"  {i}s: RPS={data['RPS']:.1f}, Success={data['Success Rate (%)']:.1f}%, Active={data['Active Users']}")
    
    # Show summary stats
    summary_stats = progress_monitor.get_summary_stats()
    if summary_stats:
        print(f"\n📋 Summary Statistics:")
        print(f"  Max RPS: {summary_stats.get('max_rps', 0):.1f}")
        print(f"  Avg RPS: {summary_stats.get('avg_rps', 0):.1f}")
        print(f"  Min Success Rate: {summary_stats.get('min_success_rate', 0):.1f}%")
        print(f"  Max Active Users: {summary_stats.get('max_active_users', 0)}")
        print(f"  Final Progress: {summary_stats.get('final_progress', 0):.1f}%")
    
    return True

if __name__ == "__main__":
    print("🧪 Progress Monitoring Timeout Fix Test")
    print("=" * 50)
    
    try:
        success = asyncio.run(test_progress_timeout_fix())
        if success:
            print("\n✅ Progress monitoring timeout fix test completed successfully!")
        else:
            print("\n❌ Progress monitoring timeout fix test failed!")
    except Exception as e:
        print(f"\n❌ Error during timeout fix test: {e}")
        import traceback
        traceback.print_exc()
