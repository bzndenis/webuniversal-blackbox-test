# Examples - Component Testing

Contoh-contoh penggunaan Black-Box Testing Tool secara programmatic (tanpa UI).

## 📁 Files

- **`test_google_components.py`** - Test komponen di Google.com
- **`output/`** - Folder untuk hasil test (auto-generated)

## 🚀 Quick Run

### Test Google.com Components

```bash
# Dari root project
python examples/test_google_components.py
```

**Output:**
```
============================================================
🔍 Deep Component Testing - Google.com
============================================================

📍 Testing: https://google.com
📁 Output: examples/output

⏳ Running tests...

============================================================
📊 RESULTS
============================================================

✅ Status: PASS
⏱️  Load Time: 1250ms
🌐 HTTP Status: 200

🔍 DEEP COMPONENT ANALYSIS
------------------------------------------------------------

🖱️  BUTTONS:
   Total: 2
   Working: 2

   Details:
   ✅ Google Search - clickable
   ✅ I'm Feeling Lucky - clickable

🖼️  IMAGES:
   Total: 1
   Loaded: 1
   Broken: 0

   Details:
   ✅ Google logo (272x92) - loaded

🔗 LINKS:
   Total: 15
   Valid: 15
   External: 3
   Internal: 12
   Empty: 0

📋 FORMS:
   Total: 1
   Complete: 1

   Details:
   ✅ Form 1:
      Action: /search
      Method: GET
      Inputs: 1
         - q (text)

============================================================
💾 FILES GENERATED
============================================================
📸 Screenshot: examples/output/screenshot.png
📄 Component Details: examples/output/component_test.json
🔍 Full Result: examples/output/result.json
📝 Summary saved to: examples/output/summary.txt

✅ Test completed successfully!
```

## 📊 Generated Files

Setelah run, check folder `examples/output/`:

1. **`screenshot.png`** - Screenshot halaman
2. **`component_test.json`** - Detail semua komponen
3. **`result.json`** - Overall test result
4. **`summary.txt`** - Human-readable summary
5. **`page.html`** - Saved HTML

## 🎯 Customize for Your Website

Edit `test_google_components.py`:

```python
# Change URL
url = "https://yourwebsite.com"

# Change output directory
output_dir = "my_tests/output"

# Adjust timeout (ms)
timeout = 30000  # 30 seconds for slow pages

# Disable headless to see browser
headless = False
```

## 🔧 Create Your Own Test Script

```python
from app.runners.playwright_runner import run_page_smoke

# Run test
result = run_page_smoke(
    url="https://example.com",
    out_dir="output",
    timeout=15000,
    headless=True,
    deep_component_test=True  # Enable deep testing
)

# Access results
if 'component_tests' in result:
    comp = result['component_tests']
    
    # Get button info
    buttons = comp['buttons']
    print(f"Buttons: {buttons['clickable_buttons']}/{buttons['total_buttons']}")
    
    # Get image info
    images = comp['images']
    print(f"Images: {images['loaded_images']}/{images['total_images']}")
    
    # Get broken images
    broken = images['broken_images']
    if broken > 0:
        print(f"⚠️ Found {broken} broken images!")
```

## 📚 More Examples

### Test Multiple Pages

```python
urls = [
    "https://example.com",
    "https://example.com/about",
    "https://example.com/contact"
]

for url in urls:
    print(f"Testing: {url}")
    result = run_page_smoke(url, f"output/{url.split('/')[-1]}", deep_component_test=True)
    # Process result...
```

### Focus on Specific Components

```python
result = run_page_smoke("https://example.com", "output", deep_component_test=True)

comp = result['component_tests']

# Check only buttons
buttons = comp['buttons']['buttons_tested']
for btn in buttons:
    if btn['status'] != 'clickable':
        print(f"⚠️ Button issue: {btn['text']} - {btn['status']}")

# Check only broken images
images = comp['images']['images_tested']
for img in images:
    if img['status'] == 'broken':
        print(f"❌ Broken image: {img['src']}")
```

## 💡 Integration Ideas

### 1. CI/CD Integration

```yaml
# .github/workflows/component-test.yml
- name: Run Component Tests
  run: python examples/test_google_components.py

- name: Check for broken images
  run: |
    if grep -q "broken" examples/output/summary.txt; then
      echo "❌ Broken images found!"
      exit 1
    fi
```

### 2. Scheduled Testing

```python
# schedule_test.py
import schedule
import time

def run_test():
    os.system("python examples/test_google_components.py")

schedule.every().day.at("00:00").do(run_test)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 3. Slack Notifications

```python
import requests

result = run_page_smoke(url, output_dir, deep_component_test=True)

summary = result['component_tests']['summary']
broken_images = summary['broken_images']

if broken_images > 0:
    # Send Slack notification
    requests.post(SLACK_WEBHOOK, json={
        "text": f"⚠️ {broken_images} broken images found on {url}"
    })
```

## 🎓 Learn More

- Full documentation: [README.md](../README.md)
- Component testing guide: [COMPONENT_TESTING_GUIDE.md](../COMPONENT_TESTING_GUIDE.md)
- Use Streamlit UI: `python run.py`

---

**Happy Testing! 🚀**

