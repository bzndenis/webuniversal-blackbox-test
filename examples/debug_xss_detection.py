"""
Script untuk debugging XSS detection
Membantu memahami mengapa payload tidak memberikan respon yang diharapkan
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.xss_pentest import XSSPentester
from playwright.sync_api import sync_playwright


def debug_xss_detection():
    """Debug XSS detection untuk memahami response"""
    print("🔍 Debugging XSS Detection...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=False untuk melihat browser
        page = browser.new_page()
        
        # Test dengan halaman yang memiliki form
        test_url = "http://127.0.0.1:8000/login"  # Ganti dengan URL yang Anda test
        
        try:
            print(f"🌐 Navigating to: {test_url}")
            page.goto(test_url)
            page.wait_for_load_state('networkidle')
            
            # Ambil form
            forms = page.locator('form').all()
            if not forms:
                print("❌ No forms found on the page")
                return
            
            print(f"✅ Found {len(forms)} form(s)")
            
            # Test dengan form pertama
            form = forms[0]
            inputs = form.locator('input[type="text"], input[type="password"], textarea').all()
            
            if not inputs:
                print("❌ No input fields found in form")
                return
            
            print(f"✅ Found {len(inputs)} input field(s)")
            
            # Test dengan input pertama
            input_elem = inputs[0]
            input_name = input_elem.get_attribute('name') or 'unnamed'
            input_type = input_elem.get_attribute('type') or 'text'
            
            print(f"🔍 Testing input: {input_name} (type: {input_type})")
            
            # Test dengan payload sederhana
            test_payload = "<script>alert('XSS')</script>"
            print(f"📝 Using payload: {test_payload}")
            
            # Clear dan fill input
            input_elem.clear()
            input_elem.fill(test_payload)
            print("✅ Payload filled in input field")
            
            # Submit form
            submit_btn = form.locator('input[type="submit"], button[type="submit"]').first
            if submit_btn.count() > 0:
                print("🔄 Submitting form...")
                submit_btn.click()
                page.wait_for_timeout(3000)  # Wait 3 seconds
                print("✅ Form submitted")
            else:
                print("⚠️ No submit button found, trying Enter key")
                input_elem.press('Enter')
                page.wait_for_timeout(3000)
            
            # Ambil response
            response_text = page.content()
            print(f"📄 Response length: {len(response_text)} characters")
            
            # Cek apakah payload muncul dalam response
            payload_found = test_payload in response_text
            print(f"🔍 Payload found in response: {payload_found}")
            
            if payload_found:
                payload_position = response_text.find(test_payload)
                print(f"📍 Payload position: {payload_position}")
                
                # Ambil context sekitar payload
                start = max(0, payload_position - 200)
                end = min(len(response_text), payload_position + len(test_payload) + 200)
                context = response_text[start:end]
                print(f"📝 Payload context:\n{context}")
            else:
                print("❌ Payload not found in response")
                
                # Cek apakah ada alert yang muncul
                try:
                    # Cek apakah ada alert dialog
                    alert_text = page.evaluate("""
                        () => {
                            // Cek apakah ada alert yang muncul
                            return document.querySelector('script') ? 'Script tags found' : 'No script tags';
                        }
                    """)
                    print(f"🔍 Script tags check: {alert_text}")
                except Exception as e:
                    print(f"⚠️ Could not check for script tags: {e}")
            
            # Test dengan XSS pentester
            print("\n🔒 Testing with XSS Pentester...")
            xss_tester = XSSPentester()
            result = xss_tester.run_xss_test(page, test_url)
            
            print(f"📊 XSS Test Results:")
            print(f"   Total Tests: {result['summary']['total_tests']}")
            print(f"   Vulnerabilities Found: {result['summary']['vulnerabilities_found']}")
            print(f"   High Vulnerabilities: {result['summary']['high_vulnerabilities']}")
            print(f"   Critical Vulnerabilities: {result['summary']['critical_vulnerabilities']}")
            
            if result['form_tests']:
                print(f"\n📋 Form Test Details:")
                for test in result['form_tests']:
                    print(f"   Input: {test['input_name']}")
                    print(f"   Payload: {test['payload']}")
                    print(f"   Vulnerable: {test['is_vulnerable']}")
                    print(f"   Risk Level: {test['risk_level']}")
                    if 'payload_found_in_response' in test:
                        print(f"   Payload Found: {test['payload_found_in_response']}")
                    if 'payload_context' in test:
                        print(f"   Context: {test['payload_context'][:100]}...")
                    print()
            
            # Cek apakah ada JavaScript error
            try:
                console_messages = page.evaluate("""
                    () => {
                        return window.console ? 'Console available' : 'No console';
                    }
                """)
                print(f"🔍 Console check: {console_messages}")
            except Exception as e:
                print(f"⚠️ Could not check console: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("\n⏸️ Press Enter to close browser...")
            input()
            browser.close()


def test_specific_payload():
    """Test payload spesifik untuk debugging"""
    print("🔍 Testing Specific Payload...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Test dengan halaman sederhana
            test_url = "http://127.0.0.1:8000/login"
            page.goto(test_url)
            page.wait_for_load_state('networkidle')
            
            # Test berbagai payload
            payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "javascript:alert('XSS')",
                "<input onfocus=alert('XSS') autofocus>",
                "<a href=javascript:alert('XSS')>Click</a>"
            ]
            
            for i, payload in enumerate(payloads, 1):
                print(f"\n🧪 Test {i}: {payload}")
                
                # Cari input field
                inputs = page.locator('input[type="text"], input[type="password"], textarea').all()
                if inputs:
                    input_elem = inputs[0]
                    input_elem.clear()
                    input_elem.fill(payload)
                    
                    # Submit form
                    forms = page.locator('form').all()
                    if forms:
                        submit_btn = forms[0].locator('input[type="submit"], button[type="submit"]').first
                        if submit_btn.count() > 0:
                            submit_btn.click()
                            page.wait_for_timeout(2000)
                    
                    # Cek response
                    response_text = page.content()
                    payload_found = payload in response_text
                    print(f"   Payload found: {payload_found}")
                    
                    if payload_found:
                        position = response_text.find(payload)
                        context = response_text[max(0, position-50):position+len(payload)+50]
                        print(f"   Context: {context}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("\n⏸️ Press Enter to close browser...")
            input()
            browser.close()


def main():
    """Main function"""
    print("🚀 XSS Detection Debug Tool")
    print("=" * 50)
    
    choice = input("""
Pilih opsi:
1. Debug XSS Detection (Full)
2. Test Specific Payloads
3. Exit

Pilihan (1-3): """)
    
    if choice == "1":
        debug_xss_detection()
    elif choice == "2":
        test_specific_payload()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()


