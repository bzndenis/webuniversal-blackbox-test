"""Playwright-based test runner for automated page testing."""

import sys
import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Set event loop policy for Windows BEFORE importing Playwright
# This is handled in main.py, no need to re-apply here
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from .component_tester import run_comprehensive_component_test
from app.services.heuristics import perform_login

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10000


def clean_for_json(data):
    """
    Clean data untuk JSON serialization dengan menghapus bytes dan objek yang tidak bisa di-serialize.
    
    Args:
        data: Dictionary atau data yang akan dibersihkan
        
    Returns:
        Data yang sudah dibersihkan untuk JSON serialization
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, bytes):
                # Skip bytes data
                continue
            elif isinstance(value, (dict, list)):
                cleaned[key] = clean_for_json(value)
            else:
                cleaned[key] = value
        return cleaned
    elif isinstance(data, list):
        return [clean_for_json(item) for item in data if not isinstance(item, bytes)]
    else:
        return data


def run_page_smoke(
    url: str,
    out_dir: str,
    timeout: int = DEFAULT_TIMEOUT,
    headless: bool = True,
    deep_component_test: bool = False,
    test_forms: bool = False,
    auth: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Jalankan smoke test pada satu halaman.
    
    Args:
        url: URL halaman yang akan ditest
        out_dir: Direktori untuk menyimpan artifacts
        timeout: Timeout dalam ms (default: 10000)
        headless: Run browser in headless mode (default: True)
        deep_component_test: Run comprehensive component testing (default: False)
        test_forms: Test form submission (default: False)
        auth: Authentication configuration (optional)
        
    Returns:
        Dictionary berisi hasil test lengkap
    """
    os.makedirs(out_dir, exist_ok=True)
    
    result = {
        "url": url,
        "status": "UNKNOWN",
        "load_ms": None,
        "console_errors": [],
        "console_warnings": [],
        "network_failures": [],
        "assertions": [],
        "forms_found": 0,
        "forms_tested": 0,
        "screenshot": None,
        "timestamp": datetime.now().isoformat(),
        "error": None
    }
    
    try:
        with sync_playwright() as p:
            browser: Browser = p.chromium.launch(headless=headless)
            context: BrowserContext = browser.new_context(
                ignore_https_errors=True,
                user_agent=os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; BlackBoxTester/1.0)")
            )
            page: Page = context.new_page()
            page.set_default_timeout(timeout)

            # Collect console messages
            def handle_console(msg):
                # Playwright API berubah antar versi (method vs properti)
                # Ambil nilai dengan aman baik jika callable maupun atribut biasa
                msg_type_attr = getattr(msg, "type", None)
                msg_text_attr = getattr(msg, "text", None)
                msg_location_attr = getattr(msg, "location", None)

                message_type = msg_type_attr() if callable(msg_type_attr) else msg_type_attr
                message_text = msg_text_attr() if callable(msg_text_attr) else msg_text_attr
                message_location = (
                    msg_location_attr() if callable(msg_location_attr) else msg_location_attr
                )

                if message_type == "error":
                    result["console_errors"].append({
                        "text": message_text,
                        "type": message_type,
                        "location": message_location
                    })
                elif message_type == "warning":
                    result["console_warnings"].append(message_text)
            
            page.on("console", handle_console)
            
            # Collect failed requests
            def handle_request_failed(req):
                # Normalisasi akses properti vs metode antar versi Playwright
                def val(obj, name):
                    attr = getattr(obj, name, None)
                    return attr() if callable(attr) else attr

                result["network_failures"].append({
                    "url": val(req, "url"),
                    "method": val(req, "method"),
                    "resource_type": val(req, "resource_type"),
                    "failure": val(req, "failure"),
                })
            
            page.on("requestfailed", handle_request_failed)

            # Optional: Authentication step before testing page
            if auth and auth.get("enabled"):
                try:
                    login_url = auth.get("url") or url
                    creds = auth.get("credentials", {}) or {}
                    username = creds.get("username") or creds.get("email") or ""
                    password = creds.get("password") or ""
                    success_indicator = auth.get("success_indicator")
                    logger.info("Performing login before page test")
                    auth_result = perform_login(
                        page=page,
                        login_url=login_url,
                        username=username,
                        password=password,
                        success_indicator=success_indicator,
                        timeout_ms=timeout,
                    )
                    result["auth"] = auth_result
                except Exception as auth_e:
                    result["auth"] = {"success": False, "error": str(auth_e)}

            # Navigate and measure load time for target page
            logger.info(f"Testing page: {url}")
            t0 = time.time()
            resp = page.goto(url, wait_until="load", timeout=timeout)
            load_ms = int((time.time() - t0) * 1000)
            result["load_ms"] = load_ms

            # Check HTTP status
            code = resp.status if resp else None
            result["http_status"] = code
            
            if code and 200 <= code < 400:
                result["status"] = "PASS"
            else:
                result["status"] = f"HTTP_{code}"

            # Wait a bit for dynamic content
            page.wait_for_timeout(1000)

            # Basic assertions
            try:
                title = page.title()
            except TypeError:
                # Beberapa versi wrapper dapat mengekspos title sebagai properti/string
                try:
                    title_attr = getattr(page, "title", "")
                    title = title_attr if isinstance(title_attr, str) else ""
                except Exception:
                    # Fallback terakhir via DOM
                    try:
                        title = page.evaluate("() => document.title")
                    except Exception:
                        title = ""
            result["assertions"].append({
                "assert": "title_not_empty",
                "pass": bool(title and title.strip()),
                "actual": title,
                "expected": "non-empty string"
            })
            
            # Check for h1
            h1 = page.locator("h1")
            has_h1 = h1.count() > 0
            result["assertions"].append({
                "assert": "has_h1",
                "pass": has_h1,
                "count": h1.count(),
                "expected": "at least 1"
            })
            
            # Check meta charset
            meta_charset = page.locator('meta[charset]').count() > 0
            meta_content_type = page.locator('meta[http-equiv="Content-Type"]').count() > 0
            has_charset = meta_charset or meta_content_type
            result["assertions"].append({
                "assert": "has_meta_charset",
                "pass": has_charset,
                "actual": "found" if has_charset else "not found"
            })
            
            # Check for lang attribute
            html_lang = page.locator('html[lang]').count() > 0
            result["assertions"].append({
                "assert": "has_html_lang",
                "pass": html_lang,
                "actual": "found" if html_lang else "not found"
            })

            # Check for broken images (robust terhadap DOM dinamis)
            images = page.locator('img')
            broken_images = 0
            checked_images = 0
            try:
                # Snapshot semua naturalWidth sekaligus untuk menghindari race ketika DOM berubah
                widths = images.evaluate_all("imgs => imgs.map(img => img.naturalWidth)")
                for w in widths[:10]:
                    checked_images += 1
                    try:
                        if int(w) == 0:
                            broken_images += 1
                    except Exception:
                        # Jika nilai tidak dapat di-cast, anggap bermasalah
                        broken_images += 1
            except Exception as eval_all_error:
                # Fallback per-elemen dengan timeout singkat dan scroll jika perlu
                total = min(images.count(), 10)
                for i in range(total):
                    img = images.nth(i)
                    try:
                        # Coba evaluasi cepat
                        natural_width = img.evaluate('el => el.naturalWidth', timeout=2000)
                    except PlaywrightTimeoutError:
                        # Scroll agar terlihat lalu coba lagi dengan timeout singkat
                        try:
                            img.scroll_into_view_if_needed(timeout=1000)
                            natural_width = img.evaluate('el => el.naturalWidth', timeout=1000)
                        except Exception:
                            natural_width = 0
                    except Exception as eval_error:
                        logger.warning(f"Could not evaluate image {i}: {eval_error}")
                        natural_width = 0
                    checked_images += 1
                    if not natural_width or int(natural_width) == 0:
                        broken_images += 1

            result["assertions"].append({
                "assert": "no_broken_images",
                "pass": broken_images == 0,
                "actual": f"{broken_images} broken",
                "checked": checked_images
            })

            # Find and count forms
            forms = page.locator("form")
            result["forms_found"] = forms.count()

            # Check for clickable buttons
            buttons = page.locator('button, input[type="button"], input[type="submit"]')
            result["buttons_found"] = buttons.count()

            # Deep Component Testing (jika diaktifkan)
            if deep_component_test:
                logger.info(f"Running deep component test for: {url}")
                component_results = run_comprehensive_component_test(page, test_forms_submission=False)
                result["component_tests"] = component_results
                
                # Save detailed component report
                component_report_path = os.path.join(out_dir, "component_test.json")
                with open(component_report_path, 'w', encoding='utf-8') as f:
                    json.dump(component_results, f, indent=2, ensure_ascii=False)
            
            # Form Testing (jika diaktifkan dan ada form)
            if test_forms and result.get('forms_found', 0) > 0:
                try:
                    from app.services.heuristics import test_form_submission
                    logger.info(f"Testing form submission for: {url}")
                    form_result = test_form_submission(page, 0, timeout_ms=timeout, out_dir=out_dir)
                    
                    # Form testing screenshots are handled in test_form_submission function
                    # and saved to files, not stored as bytes in result
                    
                    result['form_test'] = form_result
                    result['forms_tested'] = 1 if form_result['success'] else 0
                        
                except Exception as e:
                    logger.error(f"Form test error: {e}")
                    result['form_test_error'] = str(e)

            # Screenshot
            screenshot_path = os.path.join(out_dir, "screenshot.png")
            page.screenshot(path=screenshot_path, full_page=True)
            result["screenshot"] = screenshot_path
            
            # Save page HTML
            html_path = os.path.join(out_dir, "page.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                try:
                    f.write(page.content())
                except TypeError:
                    # Antisipasi jika content terekspos sebagai properti/string
                    content_attr = getattr(page, "content", None)
                    if isinstance(content_attr, str):
                        f.write(content_attr)
                    else:
                        try:
                            html = page.evaluate("() => document.documentElement.outerHTML")
                            f.write(html or "")
                        except Exception:
                            f.write("")
            
            logger.info(f"✓ Test complete: {url} - {result['status']}")

            context.close()
            browser.close()
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        result["status"] = "ERROR"
        result["error"] = f"{type(e).__name__}: {str(e)}"
        logger.error(f"✗ Error testing {url}: {type(e).__name__}")
        logger.error(f"Full traceback:\n{error_detail}")
    
    # Save result as JSON (clean data first)
    result_path = os.path.join(out_dir, "result.json")
    cleaned_result = clean_for_json(result)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_result, f, indent=2, ensure_ascii=False)
    
    return result


def run_yaml_scenario(
    scenario: Dict[str, Any],
    base_url: str,
    out_dir: str,
    timeout: int = DEFAULT_TIMEOUT,
    headless: bool = True,
    auth: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Jalankan skenario test dari YAML spec.
    
    Args:
        scenario: Dictionary berisi steps dari YAML
        base_url: Base URL untuk relative URLs
        out_dir: Direktori untuk artifacts
        timeout: Timeout dalam ms
        headless: Run in headless mode
        
    Returns:
        Dictionary hasil eksekusi
    """
    os.makedirs(out_dir, exist_ok=True)
    
    result = {
        "name": scenario.get("name", "Unnamed Scenario"),
        "steps_executed": 0,
        "steps_passed": 0,
        "steps_failed": 0,
        "errors": [],
        "screenshots": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            page.set_default_timeout(timeout)
            
            last_response = None

            # Optional authentication before running steps
            if auth and auth.get("enabled"):
                try:
                    login_url = auth.get("url") or base_url
                    creds = auth.get("credentials", {}) or {}
                    username = creds.get("username") or creds.get("email") or ""
                    password = creds.get("password") or ""
                    success_indicator = auth.get("success_indicator")
                    logger.info("Performing login before executing YAML scenario")
                    auth_result = perform_login(
                        page=page,
                        login_url=login_url,
                        username=username,
                        password=password,
                        success_indicator=success_indicator,
                        timeout_ms=timeout,
                    )
                    result["auth"] = auth_result
                except Exception as auth_e:
                    result["auth"] = {"success": False, "error": str(auth_e)}
            
            for idx, step in enumerate(scenario.get("steps", [])):
                action = step.get("action")
                result["steps_executed"] += 1
                
                logger.info(f"Step {idx + 1}: {action}")
                
                try:
                    if action == "goto":
                        target_url = step["url"]
                        # Handle relative URLs
                        if not target_url.startswith('http'):
                            target_url = base_url.rstrip('/') + '/' + target_url.lstrip('/')
                        last_response = page.goto(target_url, wait_until="load")
                        
                    elif action == "click":
                        selector = step["selector"]
                        page.locator(selector).first.click()
                        page.wait_for_timeout(500)  # Wait for any transitions
                        
                    elif action == "fill":
                        selector = step["selector"]
                        value = step["value"]
                        page.locator(selector).fill(value)
                        
                    elif action == "press":
                        key = step["key"]
                        page.keyboard.press(key)
                        
                    elif action == "screenshot":
                        screenshot_name = step.get("path", f"step_{idx}.png")
                        screenshot_path = os.path.join(out_dir, screenshot_name)
                        page.screenshot(path=screenshot_path, full_page=True)
                        result["screenshots"].append(screenshot_path)
                        
                    elif action == "expect_title":
                        actual = page.title()
                        expected = step.get("equals")
                        contains = step.get("contains")
                        
                        if expected and actual != expected:
                            raise AssertionError(f"Title mismatch: '{actual}' != '{expected}'")
                        if contains and contains not in actual:
                            raise AssertionError(f"Title doesn't contain: '{contains}' in '{actual}'")
                    
                    elif action == "expect_text":
                        selector = step["selector"]
                        element = page.locator(selector).first
                        text = element.text_content() or ""
                        
                        equals = step.get("equals")
                        contains = step.get("contains")
                        
                        if equals and text.strip() != equals:
                            raise AssertionError(f"Text mismatch: '{text}' != '{equals}'")
                        if contains and contains not in text:
                            raise AssertionError(f"Text doesn't contain: '{contains}' in '{text}'")
                    
                    elif action == "expect_status":
                        if last_response:
                            actual_status = last_response.status
                            expected_in = step.get("in", [])
                            expected_equals = step.get("equals")
                            
                            if expected_equals and actual_status != expected_equals:
                                raise AssertionError(f"Status mismatch: {actual_status} != {expected_equals}")
                            if expected_in and actual_status not in expected_in:
                                raise AssertionError(f"Status {actual_status} not in {expected_in}")
                    
                    elif action == "wait":
                        wait_ms = step.get("ms", 1000)
                        page.wait_for_timeout(wait_ms)
                    
                    else:
                        logger.warning(f"Unknown action: {action}")
                    
                    result["steps_passed"] += 1
                    
                except Exception as e:
                    result["steps_failed"] += 1
                    result["errors"].append({
                        "step": idx + 1,
                        "action": action,
                        "error": str(e)
                    })
                    logger.error(f"Step {idx + 1} failed: {e}")
                    
                    # Take error screenshot
                    error_screenshot = os.path.join(out_dir, f"error_step_{idx}.png")
                    try:
                        page.screenshot(path=error_screenshot)
                        result["screenshots"].append(error_screenshot)
                    except:
                        pass
            
            context.close()
            browser.close()
    
    except Exception as e:
        result["errors"].append({
            "step": "setup/teardown",
            "error": str(e)
        })
        logger.error(f"Scenario error: {e}")
    
    # Save result
    result_path = os.path.join(out_dir, "scenario_result.json")
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result

