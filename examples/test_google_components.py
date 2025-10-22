"""
Example: Test Google.com components
Contoh sederhana untuk test komponen di Google.com
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.runners.playwright_runner import run_page_smoke
import json

def main():
    """Test Google.com dengan deep component testing."""
    print("=" * 60)
    print("🔍 Deep Component Testing - Google.com")
    print("=" * 60)
    print()
    
    # Setup
    url = "https://google.com"
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📍 Testing: {url}")
    print(f"📁 Output: {output_dir}")
    print()
    
    # Run test with deep component testing
    print("⏳ Running tests...")
    result = run_page_smoke(
        url=url,
        out_dir=output_dir,
        timeout=15000,
        headless=True,
        deep_component_test=True
    )
    
    print()
    print("=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    print()
    
    # Basic info
    print(f"✅ Status: {result['status']}")
    print(f"⏱️  Load Time: {result['load_ms']}ms")
    print(f"🌐 HTTP Status: {result.get('http_status', 'N/A')}")
    print()
    
    # Component test results
    if 'component_tests' in result:
        comp = result['component_tests']
        summary = comp.get('summary', {})
        
        print("🔍 DEEP COMPONENT ANALYSIS")
        print("-" * 60)
        
        # Buttons
        print(f"\n🖱️  BUTTONS:")
        print(f"   Total: {summary.get('total_buttons', 0)}")
        print(f"   Working: {summary.get('working_buttons', 0)}")
        buttons = comp.get('buttons', {})
        if buttons.get('buttons_tested'):
            print(f"\n   Details:")
            for btn in buttons['buttons_tested'][:5]:  # Show first 5
                status_icon = "✅" if btn.get('status') == 'clickable' else "❌"
                print(f"   {status_icon} {btn.get('text', 'N/A')[:40]} - {btn.get('status', 'N/A')}")
        
        # Images
        print(f"\n🖼️  IMAGES:")
        print(f"   Total: {summary.get('total_images', 0)}")
        print(f"   Loaded: {summary.get('loaded_images', 0)}")
        print(f"   Broken: {summary.get('broken_images', 0)}")
        images = comp.get('images', {})
        if images.get('images_tested'):
            print(f"\n   Details:")
            for img in images['images_tested'][:5]:
                status_icon = "✅" if img.get('status') == 'loaded' else "❌"
                alt_text = img.get('alt', 'No alt')[:30]
                size = f"{img.get('width', 0)}x{img.get('height', 0)}"
                print(f"   {status_icon} {alt_text} ({size}) - {img.get('status', 'N/A')}")
        
        # Links
        print(f"\n🔗 LINKS:")
        print(f"   Total: {summary.get('total_links', 0)}")
        print(f"   Valid: {summary.get('valid_links', 0)}")
        links = comp.get('links', {})
        print(f"   External: {links.get('external_links', 0)}")
        print(f"   Internal: {links.get('internal_links', 0)}")
        print(f"   Empty: {links.get('empty_links', 0)}")
        
        # Forms
        print(f"\n📋 FORMS:")
        print(f"   Total: {summary.get('total_forms', 0)}")
        print(f"   Complete: {summary.get('complete_forms', 0)}")
        forms = comp.get('forms', {})
        if forms.get('forms_tested'):
            print(f"\n   Details:")
            for idx, form in enumerate(forms['forms_tested'], 1):
                status_icon = "✅" if form.get('status') == 'complete' else "⚠️"
                print(f"   {status_icon} Form {idx}:")
                print(f"      Action: {form.get('action', 'N/A')[:40]}")
                print(f"      Method: {form.get('method', 'N/A')}")
                print(f"      Inputs: {form.get('input_count', 0)}")
                if form.get('inputs'):
                    for inp in form['inputs'][:3]:
                        print(f"         - {inp.get('name', 'N/A')} ({inp.get('type', 'text')})")
    
    print()
    print("=" * 60)
    print("💾 FILES GENERATED")
    print("=" * 60)
    print(f"📸 Screenshot: {result.get('screenshot', 'N/A')}")
    print(f"📄 Component Details: {output_dir}/component_test.json")
    print(f"🔍 Full Result: {output_dir}/result.json")
    print()
    
    # Save summary
    summary_file = os.path.join(output_dir, "summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Google.com Component Test\n")
        f.write(f"=========================\n\n")
        f.write(f"Status: {result['status']}\n")
        f.write(f"Load Time: {result['load_ms']}ms\n\n")
        
        if 'component_tests' in result:
            comp = result['component_tests']
            summary = comp.get('summary', {})
            f.write(f"Components:\n")
            f.write(f"- Buttons: {summary.get('working_buttons', 0)}/{summary.get('total_buttons', 0)} working\n")
            f.write(f"- Images: {summary.get('loaded_images', 0)}/{summary.get('total_images', 0)} loaded\n")
            f.write(f"- Links: {summary.get('valid_links', 0)} valid\n")
            f.write(f"- Forms: {summary.get('complete_forms', 0)}/{summary.get('total_forms', 0)} complete\n")
    
    print(f"📝 Summary saved to: {summary_file}")
    print()
    print("✅ Test completed successfully!")
    print()

if __name__ == "__main__":
    main()

