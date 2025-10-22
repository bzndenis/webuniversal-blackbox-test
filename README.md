# 🔍 Black-Box Functional Testing Tool

Automated web testing tool untuk melakukan black-box functional testing pada website. Aplikasi ini dapat melakukan crawling otomatis, menjalankan smoke tests, mendeteksi error, dan menghasilkan laporan komprehensif.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Fitur Utama

- 🔍 **Deep Component Testing**: Test semua button, form, image, dan link di halaman secara otomatis
- 🕷️ **Automatic Crawling**: Discover pages secara otomatis dengan kontrol depth dan pattern
- 🧪 **Smoke Testing**: Load time, HTTP status, console errors, network failures
- ✅ **Automated Assertions**: Title, heading, meta tags, broken images detection
- 📋 **Form Analysis**: Deteksi dan analisis semua form beserta input fields
- 🖱️ **Button Testing**: Check apakah semua button clickable dan berfungsi
- 🖼️ **Image Validation**: Verifikasi semua image load dengan baik, detect broken images
- 🔗 **Link Checking**: Test semua link (internal & external), detect empty links
- 📝 **YAML Scenarios**: Custom test workflows dengan actions dan assertions
- 📊 **Rich Reports**: Export ke HTML, CSV, dan JSON
- 💾 **Test History**: Track semua test runs dalam SQLite database
- 📸 **Screenshots**: Capture full-page screenshots sebagai evidence

## 🚀 Quick Start

### Prerequisites

- Python 3.10 atau lebih tinggi
- pip (Python package manager)
- Git

### Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd webuniversal-blackbox-test
```

2. **Create virtual environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers**
```bash
playwright install --with-deps chromium
```

### Running the Application

```bash
streamlit run app/main.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

## 📖 Usage Guide

### 1. Crawler Mode

Mode ini secara otomatis menemukan dan mentest halaman-halaman dari sebuah website.

**Langkah:**
1. Pilih **"Crawler Mode"** di sidebar
2. Masukkan **Base URL** (contoh: `https://example.com`)
3. Atur **Max Depth** (kedalaman crawling, default: 2)
4. Atur **Max Pages** (jumlah halaman maksimal, default: 10)
5. Opsional: Tambahkan **Include/Exclude Pattern** (regex)
6. Klik **Run Test**

**Advanced Options:**
- **Same Origin Only**: Hanya crawl URL dari domain yang sama
- **Include Pattern**: Regex untuk include URL tertentu (contoh: `/blog/.*`)
- **Exclude Pattern**: Regex untuk exclude URL tertentu (contoh: `/admin/.*`)

### 2. YAML Scenario Mode

Mode ini menjalankan custom test scenarios dari file YAML.

**Langkah:**
1. Pilih **"YAML Scenario"** di sidebar
2. Upload file YAML spec
3. Klik **Run Test**

**Sample YAML:**
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
        path: "homepage.png"
```

**Supported Actions:**
- `goto`: Navigate to URL
- `click`: Click element by selector
- `fill`: Fill input field
- `press`: Press keyboard key
- `screenshot`: Take screenshot
- `wait`: Wait for specified milliseconds

**Supported Assertions:**
- `expect_title`: Check page title
- `expect_text`: Check element text
- `expect_status`: Check HTTP status

### 3. Single Page Mode (Recommended untuk Component Testing)

Mode ini mentest satu halaman spesifik dengan analisis komponen mendalam.

**Langkah:**
1. Pilih **"Single Page"** di sidebar
2. Masukkan **Page URL** (contoh: `https://google.com`)
3. Aktifkan **"🔍 Deep Component Test"** (sudah default ON)
4. Klik **Run Test**

**Deep Component Test akan mengecek:**
- ✅ **Semua Button**: Apakah clickable, disabled, atau hidden
- ✅ **Semua Image**: Apakah load dengan baik atau broken
- ✅ **Semua Link**: Valid, empty, internal, atau external
- ✅ **Semua Form**: Complete dengan action & submit button
- ✅ **Interactive Elements**: Checkbox, radio, select, textarea

## 📊 Test Reports

Setelah test selesai, aplikasi menghasilkan 3 format laporan:

### 1. HTML Report
- Interactive report dengan visualisasi
- Color-coded status (Pass/Fail)
- Summary metrics
- Detail per halaman
- Embedded screenshots

### 2. CSV Report
- Tabular data untuk analisis
- Import ke Excel/Google Sheets
- Columns: URL, Status, Load Time, Errors, dll

### 3. JSON Report
- Machine-readable format
- Complete structured data
- Untuk integrasi dengan tools lain

**Download:** Klik tombol download yang tersedia setelah test selesai.

**Location:** Reports disimpan di folder `artifacts/<run_id>/`

## 🧪 What Gets Tested?

### 🔍 Deep Component Test (Fitur Utama!)

Ketika Anda test halaman seperti **google.com**, aplikasi akan otomatis mengecek:

#### 1. **Button Testing**
- Total button di halaman
- Button yang clickable vs disabled
- Button yang visible vs hidden
- Detail setiap button (text, status, visibility)

**Output:**
```
Total Buttons: 15
Clickable: 12
Disabled: 2
Hidden: 1
```

#### 2. **Image Validation**
- Total image di halaman
- Image yang berhasil load
- Image yang broken (gagal load)
- Image tanpa alt text
- Ukuran setiap image (width x height)

**Output:**
```
Total Images: 8
Loaded: 7
Broken: 1 ❌
Without Alt: 2
```

#### 3. **Link Checking**
- Total link di halaman
- Link valid vs empty (#)
- Link internal vs external
- Detail href dan text

**Output:**
```
Total Links: 25
Valid: 23
Empty: 2
External: 5
Internal: 20
```

#### 4. **Form Analysis**
- Total form di halaman
- Form dengan action URL
- Form dengan submit button
- Detail input fields (name, type)

**Output:**
```
Total Forms: 2
With Action: 2
With Submit: 2
Inputs per form: 5, 3
```

#### 5. **Interactive Elements**
- Checkbox count (checked/unchecked)
- Radio button count
- Select dropdown count
- Textarea count

### Automatic Checks (Basic Smoke Test)

Setiap halaman juga di-check untuk:

✅ **HTTP Status**
- Status code 200-399 = PASS
- Status code 4xx/5xx = FAIL

✅ **Load Performance**
- Measure load time in milliseconds
- Flag slow pages (>5000ms)

✅ **Console Errors**
- Capture JavaScript errors
- Count error messages

✅ **Network Failures**
- Track failed requests
- Identify broken resources

✅ **Basic Assertions**
- Title not empty
- Has `<h1>` tag
- Has meta charset
- Has html lang attribute

### Form Testing (Optional)

Jika diaktifkan:
- Auto-detect forms
- Fill dengan dummy data
- Submit dan verify response
- Check for success/error messages

## 🛠️ Configuration

### Environment Variables

Create `.env` file:
```env
HEADLESS=true
TIMEOUT=10000
USER_AGENT="Mozilla/5.0 (compatible; BlackBoxTester/1.0)"
DATABASE_URL=sqlite:///./test_runs.db
LOG_LEVEL=INFO
```

### Test Options

Di sidebar, atur:
- **Headless Mode**: Run browser tanpa GUI (faster)
- **Timeout**: Maximum wait time per action (5-60 seconds)
- **Test Forms**: Enable/disable form testing

## 📁 Project Structure

```
webuniversal-blackbox-test/
├── app/
│   ├── main.py                 # Streamlit entry point
│   ├── runners/
│   │   ├── crawl.py           # Web crawler
│   │   └── playwright_runner.py
│   ├── models/
│   │   ├── db.py              # Database models
│   │   └── schemas.py         # Pydantic schemas
│   ├── services/
│   │   ├── reporter.py        # Report generators
│   │   ├── yaml_loader.py     # YAML parser
│   │   └── heuristics.py      # Form testing logic
│   └── templates/             # (Reserved for Jinja2)
├── tests/
│   ├── sample_specs/          # Example YAML files
│   ├── test_crawler.py
│   ├── test_playwright_runner.py
│   └── test_reporter.py
├── artifacts/                 # Generated reports (gitignored)
├── requirements.txt
├── pytest.ini
└── README.md
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_crawler.py

# Run with verbose output
pytest -v

# Run integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## 🎯 YAML Specification Reference

### Complete Example

```yaml
base_url: "https://example.com"

scenarios:
  - name: "User Login Flow"
    steps:
      # Navigate
      - action: "goto"
        url: "/login"
      
      # Fill form
      - action: "fill"
        selector: "input[name='username']"
        value: "testuser"
      
      - action: "fill"
        selector: "input[name='password']"
        value: "password123"
      
      # Screenshot before submit
      - action: "screenshot"
        path: "before_login.png"
      
      # Submit
      - action: "click"
        selector: "button[type='submit']"
      
      # Wait for redirect
      - action: "wait"
        ms: 2000
      
      # Verify
      - action: "expect_text"
        selector: ".welcome-message"
        contains: "Welcome"
      
      # Final screenshot
      - action: "screenshot"
        path: "after_login.png"
```

### Action Reference

| Action | Parameters | Description |
|--------|-----------|-------------|
| `goto` | `url` | Navigate to URL (absolute or relative) |
| `click` | `selector` | Click element matching selector |
| `fill` | `selector`, `value` | Fill input/textarea with value |
| `press` | `key` | Press keyboard key (Enter, Tab, etc) |
| `screenshot` | `path` | Take screenshot, save to path |
| `wait` | `ms` | Wait for milliseconds |
| `expect_title` | `equals` or `contains` | Assert page title |
| `expect_text` | `selector`, `equals` or `contains` | Assert element text |
| `expect_status` | `equals` or `in` | Assert HTTP status |

## ⚠️ Limitations

### Cannot Handle

- ❌ **CAPTCHA**: Tidak dapat bypass CAPTCHA
- ❌ **Authentication**: Tidak auto-login (gunakan YAML untuk manual flow)
- ❌ **Dynamic SPAs**: Limited support untuk heavy JavaScript apps
- ❌ **File Uploads**: Belum support upload files
- ❌ **Complex Interactions**: Drag-drop, hover menus, etc.

### Best Practices

✅ **DO:**
- Test public pages tanpa auth
- Use reasonable timeouts (10-30s)
- Limit crawl depth (1-3)
- Start dengan headless mode
- Review reports setelah test

❌ **DON'T:**
- Test production tanpa permission
- Set timeout terlalu rendah (<5s)
- Crawl terlalu dalam (>5 depth)
- Ignore robots.txt
- Test dengan data real user

## 🐛 Troubleshooting

### Browser Tidak Terinstall

**Error:** `Executable doesn't exist`

**Solution:**
```bash
playwright install --with-deps chromium
```

### Timeout Errors

**Error:** `Timeout exceeded`

**Solution:**
- Increase timeout di sidebar (20-30 seconds)
- Check internet connection
- Verify target URL accessible

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Permission Errors (Windows)

**Error:** `PermissionError` saat install

**Solution:**
- Run terminal sebagai Administrator
- Atau gunakan `--user` flag: `pip install --user -r requirements.txt`

### Windows + Playwright Compatibility (SUDAH DIPERBAIKI ✅)

**Error:** `NotImplementedError` saat run test

**Root Cause:** Windows menggunakan `ProactorEventLoop` by default, Playwright butuh `SelectorEventLoop`

**Status:** ✅ **SUDAH OTOMATIS DIPERBAIKI!**

Aplikasi ini sudah include fix otomatis untuk Windows. Event loop policy di-set ke `WindowsSelectorEventLoopPolicy` saat startup.

**Tidak perlu action apapun dari user!**

**Detail teknis:**
- [`TROUBLESHOOTING_WINDOWS.md`](TROUBLESHOOTING_WINDOWS.md) - Penjelasan umum masalah Windows
- [`FIX_NOTIMPLEMENTEDERROR.md`](FIX_NOTIMPLEMENTEDERROR.md) - Panduan lengkap perbaikan NotImplementedError

**Jika masih muncul error:**
1. Restart aplikasi (pastikan event loop policy diterapkan dari awal)
2. Disable "Deep Component Test" jika masalah persisten
3. Lihat [`FIX_NOTIMPLEMENTEDERROR.md`](FIX_NOTIMPLEMENTEDERROR.md) untuk troubleshooting lengkap

## 🚢 Deployment

### Local Production

```bash
# Activate environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Run with production settings
streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0
```

### Docker (Future)

```bash
# Build image
docker build -t blackbox-tester .

# Run container
docker run -p 8501:8501 -v $(pwd)/artifacts:/app/artifacts blackbox-tester
```

## 📚 Documentation

- [Playwright Documentation](https://playwright.dev/python/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

## 🤝 Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Playwright Team**: Untuk awesome browser automation library
- **Streamlit Team**: Untuk rapid web app framework
- **Community**: Untuk feedback dan contributions

## 📞 Support

Jika menemukan bug atau punya feature request:
- Open issue di GitHub
- Sertakan error message lengkap
- Jelaskan steps to reproduce

---

**Happy Testing! 🚀**

Made with ❤️ using Playwright and Streamlit

