from playwright.sync_api import sync_playwright
import os
print('PLAYWRIGHT_BROWSERS_PATH=', os.environ.get('PLAYWRIGHT_BROWSERS_PATH'))
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context()
    page = ctx.new_page()
    page.goto('https://example.com', timeout=15000, wait_until='load')
    print('Title:', page.title())
    ctx.close()
    b.close()
    print('OK')
