"""
Debug script untuk check event loop policy di Windows
"""
import sys
import asyncio
import platform

print("=" * 60)
print("🔍 EVENT LOOP POLICY DIAGNOSTICS")
print("=" * 60)

print(f"\n📍 Platform: {platform.system()} {platform.release()}")
print(f"🐍 Python: {sys.version}")
print(f"🔧 Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# Check current event loop policy
current_policy = asyncio.get_event_loop_policy()
print(f"\n📋 Current Event Loop Policy:")
print(f"   Type: {type(current_policy).__name__}")
print(f"   Module: {type(current_policy).__module__}")

# Check if Windows
if sys.platform == 'win32':
    print(f"\n✅ Running on Windows - Fix SHOULD be applied")
    
    # Try to get current event loop
    try:
        loop = asyncio.get_event_loop()
        print(f"\n⚙️ Current Event Loop:")
        print(f"   Type: {type(loop).__name__}")
        print(f"   Module: {type(loop).__module__}")
        print(f"   Running: {loop.is_running()}")
        print(f"   Closed: {loop.is_closed()}")
    except Exception as e:
        print(f"\n❌ Error getting event loop: {e}")
    
    # Check available policies
    print(f"\n📦 Available Event Loop Policies:")
    print(f"   - WindowsSelectorEventLoopPolicy: {hasattr(asyncio, 'WindowsSelectorEventLoopPolicy')}")
    print(f"   - WindowsProactorEventLoopPolicy: {hasattr(asyncio, 'WindowsProactorEventLoopPolicy')}")
    
    # Try setting the policy
    print(f"\n🔧 Attempting to set WindowsSelectorEventLoopPolicy...")
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        new_policy = asyncio.get_event_loop_policy()
        print(f"   ✅ SUCCESS!")
        print(f"   New policy: {type(new_policy).__name__}")
        
        # Create new event loop
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        print(f"   ✅ New event loop created: {type(new_loop).__name__}")
        
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
else:
    print(f"\n⚠️ Not running on Windows - no fix needed")

print("\n" + "=" * 60)
print("🎯 RECOMMENDATION:")
print("=" * 60)

if sys.platform == 'win32':
    if isinstance(current_policy, asyncio.WindowsSelectorEventLoopPolicy):
        print("✅ Event loop policy is CORRECT (WindowsSelectorEventLoopPolicy)")
        print("✅ Playwright SHOULD work without NotImplementedError")
    else:
        print("❌ Event loop policy is WRONG!")
        print(f"   Current: {type(current_policy).__name__}")
        print(f"   Expected: WindowsSelectorEventLoopPolicy")
        print("\n🔧 FIX: Event loop policy needs to be set BEFORE any async operations")
        print("   Add this at the VERY TOP of your script:")
        print("   ```python")
        print("   import asyncio")
        print("   if sys.platform == 'win32':")
        print("       asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())")
        print("   ```")

print("\n" + "=" * 60)

