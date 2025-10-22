"""Deep component testing for web pages."""

from playwright.sync_api import Page, Locator
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def test_all_buttons(page: Page) -> Dict[str, Any]:
    """
    Test semua button di halaman.
    
    Args:
        page: Playwright page object
        
    Returns:
        Dictionary dengan hasil test buttons
    """
    result = {
        "total_buttons": 0,
        "clickable_buttons": 0,
        "disabled_buttons": 0,
        "hidden_buttons": 0,
        "buttons_tested": [],
        "errors": []
    }
    
    try:
        # Find all button elements
        button_selectors = [
            'button',
            'input[type="button"]',
            'input[type="submit"]',
            'a[role="button"]',
            '[role="button"]'
        ]
        
        for selector in button_selectors:
            buttons = page.locator(selector)
            count = buttons.count()
            
            for i in range(count):
                button = buttons.nth(i)
                result["total_buttons"] += 1
                
                try:
                    # Check if visible
                    is_visible = button.is_visible()
                    if not is_visible:
                        result["hidden_buttons"] += 1
                        continue
                    
                    # Check if disabled
                    is_disabled = button.is_disabled()
                    if is_disabled:
                        result["disabled_buttons"] += 1
                        button_info = {
                            "selector": selector,
                            "index": i,
                            "text": button.text_content() or button.get_attribute('value') or 'N/A',
                            "status": "disabled",
                            "visible": is_visible
                        }
                        result["buttons_tested"].append(button_info)
                        continue
                    
                    # Check if clickable
                    is_enabled = button.is_enabled()
                    
                    # Get button info
                    button_text = button.text_content() or button.get_attribute('value') or button.get_attribute('aria-label') or 'N/A'
                    
                    button_info = {
                        "selector": selector,
                        "index": i,
                        "text": button_text.strip()[:50] if button_text else 'N/A',
                        "enabled": is_enabled,
                        "visible": is_visible,
                        "status": "clickable" if is_enabled else "not_clickable"
                    }
                    
                    if is_enabled:
                        result["clickable_buttons"] += 1
                    
                    result["buttons_tested"].append(button_info)
                    
                except Exception as e:
                    result["errors"].append({
                        "selector": selector,
                        "index": i,
                        "error": str(e)
                    })
                    logger.error(f"Error testing button {selector}[{i}]: {e}")
    
    except Exception as e:
        result["errors"].append({"error": f"General error: {str(e)}"})
        logger.error(f"Error in test_all_buttons: {e}")
    
    return result


def test_all_images(page: Page) -> Dict[str, Any]:
    """
    Test semua image di halaman.
    
    Args:
        page: Playwright page object
        
    Returns:
        Dictionary dengan hasil test images
    """
    result = {
        "total_images": 0,
        "loaded_images": 0,
        "broken_images": 0,
        "images_without_alt": 0,
        "images_tested": [],
        "errors": []
    }
    
    try:
        images = page.locator('img')
        result["total_images"] = images.count()
        
        for i in range(images.count()):
            img = images.nth(i)
            
            try:
                src = img.get_attribute('src') or ''
                alt = img.get_attribute('alt') or ''
                
                # Check if image loaded
                natural_width = img.evaluate('img => img.naturalWidth')
                natural_height = img.evaluate('img => img.naturalHeight')
                
                is_loaded = natural_width > 0 and natural_height > 0
                
                image_info = {
                    "index": i,
                    "src": src[:100] if src else 'N/A',
                    "alt": alt[:50] if alt else 'N/A',
                    "has_alt": bool(alt),
                    "width": natural_width,
                    "height": natural_height,
                    "status": "loaded" if is_loaded else "broken"
                }
                
                if is_loaded:
                    result["loaded_images"] += 1
                else:
                    result["broken_images"] += 1
                
                if not alt:
                    result["images_without_alt"] += 1
                
                result["images_tested"].append(image_info)
                
            except Exception as e:
                result["errors"].append({
                    "index": i,
                    "error": str(e)
                })
                logger.error(f"Error testing image {i}: {e}")
    
    except Exception as e:
        result["errors"].append({"error": f"General error: {str(e)}"})
        logger.error(f"Error in test_all_images: {e}")
    
    return result


def test_all_links(page: Page) -> Dict[str, Any]:
    """
    Test semua link di halaman.
    
    Args:
        page: Playwright page object
        
    Returns:
        Dictionary dengan hasil test links
    """
    result = {
        "total_links": 0,
        "valid_links": 0,
        "empty_links": 0,
        "external_links": 0,
        "internal_links": 0,
        "links_tested": [],
        "errors": []
    }
    
    try:
        links = page.locator('a')
        result["total_links"] = links.count()
        
        current_domain = page.url
        
        for i in range(min(links.count(), 50)):  # Limit to first 50 links
            link = links.nth(i)
            
            try:
                href = link.get_attribute('href') or ''
                text = link.text_content() or ''
                
                is_visible = link.is_visible()
                
                # Categorize link
                is_external = href.startswith('http') and current_domain not in href
                is_empty = not href or href == '#'
                
                link_info = {
                    "index": i,
                    "href": href[:100] if href else 'N/A',
                    "text": text.strip()[:50] if text else 'N/A',
                    "visible": is_visible,
                    "type": "external" if is_external else "internal",
                    "status": "empty" if is_empty else "valid"
                }
                
                if is_empty:
                    result["empty_links"] += 1
                else:
                    result["valid_links"] += 1
                
                if is_external:
                    result["external_links"] += 1
                else:
                    result["internal_links"] += 1
                
                result["links_tested"].append(link_info)
                
            except Exception as e:
                result["errors"].append({
                    "index": i,
                    "error": str(e)
                })
                logger.error(f"Error testing link {i}: {e}")
    
    except Exception as e:
        result["errors"].append({"error": f"General error: {str(e)}"})
        logger.error(f"Error in test_all_links: {e}")
    
    return result


def test_all_forms(page: Page, test_submission: bool = False) -> Dict[str, Any]:
    """
    Test semua form di halaman.
    
    Args:
        page: Playwright page object
        test_submission: Apakah mencoba submit form (default: False)
        
    Returns:
        Dictionary dengan hasil test forms
    """
    result = {
        "total_forms": 0,
        "forms_with_action": 0,
        "forms_with_submit": 0,
        "forms_tested": [],
        "errors": []
    }
    
    try:
        forms = page.locator('form')
        result["total_forms"] = forms.count()
        
        for i in range(forms.count()):
            form = forms.nth(i)
            
            try:
                action = form.get_attribute('action') or ''
                method = form.get_attribute('method') or 'GET'
                
                # Count inputs
                inputs = form.locator('input, textarea, select')
                input_count = inputs.count()
                
                # Check for submit button
                submit_buttons = form.locator('button[type="submit"], input[type="submit"]')
                has_submit = submit_buttons.count() > 0
                
                # Get input types
                input_types = []
                for j in range(min(input_count, 20)):  # Limit to 20 inputs
                    input_elem = inputs.nth(j)
                    input_type = input_elem.get_attribute('type') or 'text'
                    input_name = input_elem.get_attribute('name') or f'input_{j}'
                    
                    if input_type not in ['submit', 'button', 'hidden']:
                        input_types.append({
                            "name": input_name,
                            "type": input_type
                        })
                
                form_info = {
                    "index": i,
                    "action": action[:100] if action else 'N/A',
                    "method": method.upper(),
                    "has_action": bool(action),
                    "has_submit_button": has_submit,
                    "input_count": input_count,
                    "inputs": input_types,
                    "status": "complete" if (action and has_submit) else "incomplete"
                }
                
                if action:
                    result["forms_with_action"] += 1
                
                if has_submit:
                    result["forms_with_submit"] += 1
                
                # Optional: Test submission
                if test_submission and has_submit and input_count > 0:
                    try:
                        # Fill form with dummy data
                        for j in range(min(input_count, 10)):
                            input_elem = inputs.nth(j)
                            input_type = input_elem.get_attribute('type') or 'text'
                            
                            if input_type == 'text':
                                input_elem.fill('Test Input')
                            elif input_type == 'email':
                                input_elem.fill('test@example.com')
                            elif input_type == 'password':
                                input_elem.fill('TestPassword123')
                            elif input_type == 'number':
                                input_elem.fill('42')
                        
                        form_info["test_filled"] = True
                        # Note: We don't actually submit to avoid side effects
                        
                    except Exception as e:
                        form_info["test_error"] = str(e)
                
                result["forms_tested"].append(form_info)
                
            except Exception as e:
                result["errors"].append({
                    "index": i,
                    "error": str(e)
                })
                logger.error(f"Error testing form {i}: {e}")
    
    except Exception as e:
        result["errors"].append({"error": f"General error: {str(e)}"})
        logger.error(f"Error in test_all_forms: {e}")
    
    return result


def test_interactive_elements(page: Page) -> Dict[str, Any]:
    """
    Test interactive elements seperti dropdown, checkbox, radio.
    
    Args:
        page: Playwright page object
        
    Returns:
        Dictionary dengan hasil test
    """
    result = {
        "checkboxes": {"total": 0, "checked": 0, "unchecked": 0},
        "radios": {"total": 0, "checked": 0, "unchecked": 0},
        "selects": {"total": 0, "with_options": 0},
        "textareas": {"total": 0, "with_placeholder": 0},
        "errors": []
    }
    
    try:
        # Test checkboxes
        checkboxes = page.locator('input[type="checkbox"]')
        result["checkboxes"]["total"] = checkboxes.count()
        for i in range(checkboxes.count()):
            if checkboxes.nth(i).is_checked():
                result["checkboxes"]["checked"] += 1
            else:
                result["checkboxes"]["unchecked"] += 1
        
        # Test radios
        radios = page.locator('input[type="radio"]')
        result["radios"]["total"] = radios.count()
        for i in range(radios.count()):
            if radios.nth(i).is_checked():
                result["radios"]["checked"] += 1
            else:
                result["radios"]["unchecked"] += 1
        
        # Test selects
        selects = page.locator('select')
        result["selects"]["total"] = selects.count()
        for i in range(selects.count()):
            options = selects.nth(i).locator('option')
            if options.count() > 0:
                result["selects"]["with_options"] += 1
        
        # Test textareas
        textareas = page.locator('textarea')
        result["textareas"]["total"] = textareas.count()
        for i in range(textareas.count()):
            placeholder = textareas.nth(i).get_attribute('placeholder')
            if placeholder:
                result["textareas"]["with_placeholder"] += 1
    
    except Exception as e:
        result["errors"].append({"error": str(e)})
        logger.error(f"Error in test_interactive_elements: {e}")
    
    return result


def run_comprehensive_component_test(
    page: Page,
    test_forms_submission: bool = False
) -> Dict[str, Any]:
    """
    Jalankan comprehensive test untuk semua komponen di halaman.
    
    Args:
        page: Playwright page object
        test_forms_submission: Test form submission atau tidak
        
    Returns:
        Dictionary dengan semua hasil test komponen
    """
    logger.info("Starting comprehensive component test...")
    
    results = {
        "buttons": test_all_buttons(page),
        "images": test_all_images(page),
        "links": test_all_links(page),
        "forms": test_all_forms(page, test_submission=test_forms_submission),
        "interactive": test_interactive_elements(page)
    }
    
    # Summary
    results["summary"] = {
        "total_buttons": results["buttons"]["total_buttons"],
        "working_buttons": results["buttons"]["clickable_buttons"],
        "total_images": results["images"]["total_images"],
        "loaded_images": results["images"]["loaded_images"],
        "broken_images": results["images"]["broken_images"],
        "total_links": results["links"]["total_links"],
        "valid_links": results["links"]["valid_links"],
        "total_forms": results["forms"]["total_forms"],
        "complete_forms": results["forms"]["forms_with_submit"],
        "total_errors": (
            len(results["buttons"]["errors"]) +
            len(results["images"]["errors"]) +
            len(results["links"]["errors"]) +
            len(results["forms"]["errors"]) +
            len(results["interactive"]["errors"])
        )
    }
    
    logger.info("Comprehensive component test completed")
    return results

