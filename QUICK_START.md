# ⚡ Quick Start Guide

Panduan singkat untuk langsung menggunakan Black-Box Testing Tool.

## 🚀 Installation (5 menit)

### 1. Install Python 3.10+

Download dari [python.org](https://www.python.org/downloads/)

Verify:
```bash
python --version  # Should show 3.10 or higher
```

### 2. Clone & Setup

```bash
# Clone repository
git clone <repo-url>
cd webuniversal-blackbox-test

# Create virtual environment
python -m venv .venv

# Activate (pilih sesuai OS)
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install --with-deps chromium
```

### 3. Run Application

```bash
# Simple way
python run.py

# Or directly
streamlit run app/main.py
```

Buka browser ke: **http://localhost:8501**

## 📝 First Test (1 menit)

### Test Single Page (dengan Deep Component Testing)

1. Di sidebar, pilih **"Single Page"**
2. Isi URL: `https://google.com`
3. Pastikan **"🔍 Deep Component Test"** = ✅ (default ON)
4. Klik **🚀 Run Test**
5. Tunggu ~10-15 detik
6. Lihat hasil detail komponen:
   - Klik **expander** untuk detail
   - Check tab **Buttons**, **Images**, **Links**, **Forms**
7. Download report

### Test Multiple Pages (Crawler)

1. Di sidebar, pilih **"Crawler Mode"**
2. Isi Base URL: `https://example.com`
3. Set Max Pages: `5`
4. Klik **🚀 Run Test**
5. Tunggu ~30-60 detik
6. Download HTML report

## 🎯 What You'll Get

Setelah test selesai:

✅ **Summary Metrics**
- Total pages tested
- Pass rate (%)
- Average load time
- Console errors count
- Network failures count

✅ **Deep Component Analysis** (NEW! 🔍)
- **Buttons**: 12/15 working, 2 disabled, 1 hidden
- **Images**: 8/8 loaded, 0 broken
- **Links**: 45 valid, 2 empty
- **Forms**: 2/2 complete with submit buttons
- **Interactive**: Checkboxes, radios, selects

✅ **Detailed Results Table**
- Per-page status
- Load time
- Errors
- Assertions

✅ **Component Details per Element**
- Every button (text, clickable, status)
- Every image (src, alt, size, loaded/broken)
- Every link (href, text, type)
- Every form (action, method, inputs)

✅ **Reports (3 formats)**
- 📊 HTML (visual, interactive)
- 📈 CSV (untuk Excel)
- 🔧 JSON (untuk automation)
- 🔍 Component Test JSON (detailed)

✅ **Screenshots**
- Full page screenshots
- Saved in `artifacts/` folder

## 🧪 Test YAML Scenario

### 1. Create YAML file

`my_test.yaml`:
```yaml
base_url: "https://example.com"
scenarios:
  - name: "Homepage Check"
    steps:
      - action: "goto"
        url: "/"
      - action: "expect_title"
        contains: "Example"
      - action: "screenshot"
        path: "test.png"
```

### 2. Upload & Run

1. Pilih **"YAML Scenario"**
2. Upload `my_test.yaml`
3. Klik **Run Test**

## 🎨 Customization

### Change Timeout

Di sidebar → **Timeout slider** → 5-60 seconds

### Headless vs Visual

Di sidebar → **Headless Mode checkbox**
- ✅ Headless = Faster, no GUI
- ❌ Not Headless = See browser (debugging)

### Filter URLs (Crawler Mode)

**Include only blog posts:**
```
Include Pattern: /blog/.*
```

**Exclude admin pages:**
```
Exclude Pattern: /admin/.*
```

## ❓ Troubleshooting

### "Executable doesn't exist"
```bash
playwright install --with-deps chromium
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### Timeout errors
- Increase timeout to 30s
- Check internet connection
- Try different URL

## 📚 Next Steps

1. ✅ Read full [README.md](README.md)
2. ✅ Check [sample YAML files](tests/sample_specs/)
3. ✅ Run unit tests: `pytest`
4. ✅ Explore `artifacts/` folder
5. ✅ Try testing your own website!

## 🎉 Success!

Sekarang Anda sudah bisa:
- ✅ Test single page dengan deep component analysis
- ✅ Check semua button apakah working
- ✅ Detect broken images
- ✅ Validate all links
- ✅ Analyze all forms
- ✅ Crawl & test multiple pages
- ✅ Run YAML scenarios
- ✅ Generate reports
- ✅ Export data

## 🔥 Try This!

### Test Your Website

```
1. Single Page mode
2. URL: https://yourwebsite.com
3. Deep Component Test: ✅ ON
4. Run Test
5. Check results:
   - Any broken images? ❌
   - Any disabled buttons? ⚠️
   - Any empty links? ⚠️
   - All forms complete? ✅
```

### Example: Test Google

```
URL: https://google.com

Results:
✅ 2/2 buttons working
✅ 1/1 images loaded
✅ 15/15 links valid
✅ 1/1 forms complete
```

### Programmatic Testing

Tanpa UI, langsung via Python script:

```bash
python examples/test_google_components.py
```

**Happy Testing! 🚀**

---

📚 **More Resources:**
- Full guide: [README.md](README.md)
- Component testing: [COMPONENT_TESTING_GUIDE.md](COMPONENT_TESTING_GUIDE.md)
- Examples: [examples/](examples/)
- Issues: GitHub Issues

