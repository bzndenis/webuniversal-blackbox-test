# 🔍 Panduan Deep Component Testing

Panduan lengkap menggunakan fitur **Deep Component Testing** untuk mengecek semua komponen di halaman web.

## 🎯 Apa itu Deep Component Testing?

Deep Component Testing adalah fitur untuk **otomatis mengecek semua elemen interaktif** di halaman web seperti:
- Button (apakah bisa diklik?)
- Form (apakah complete dan berfungsi?)
- Image (apakah load dengan baik?)
- Link (apakah valid?)
- Dan lainnya...

## 🚀 Cara Menggunakan

### Quick Start (1 Menit)

1. **Buka aplikasi:**
```bash
python run.py
```

2. **Di sidebar:**
   - Pilih mode: **"Single Page"**
   - Masukkan URL: **`https://google.com`**
   - Pastikan **"🔍 Deep Component Test"** = ✅ (default ON)

3. **Klik "🚀 Run Test"**

4. **Lihat hasilnya dalam ~10-15 detik**

## 📊 Apa yang Akan Anda Dapatkan?

### 1. Summary Metrics

Ringkasan cepat:
```
Total Buttons: 12 working / 15 total
Total Images: 8 loaded / 8 total (0 broken)
Total Links: 45 valid
Total Forms: 2 complete / 2 total
```

### 2. Detailed Component Analysis

Klik **expander** untuk melihat detail setiap komponen:

#### Tab "Buttons"
Tabel berisi semua button dengan info:
- **Text**: Label/text di button
- **Status**: clickable, disabled, hidden
- **Visible**: true/false
- **Enabled**: true/false

**Example:**
| Text | Status | Visible | Enabled |
|------|--------|---------|---------|
| Submit | clickable | true | true |
| Disabled Button | disabled | true | false |
| Hidden Action | hidden | false | false |

#### Tab "Images"
Tabel berisi semua image dengan info:
- **Source**: URL image (50 char)
- **Alt**: Alt text untuk accessibility
- **Size**: Width x Height dalam pixel
- **Status**: loaded / broken

**Example:**
| Source | Alt | Size | Status |
|--------|-----|------|--------|
| logo.png | Company Logo | 200x50 | loaded |
| banner.jpg | N/A | 0x0 | broken ❌ |

#### Tab "Links"
Tabel berisi semua link dengan info:
- **Text**: Anchor text
- **Href**: URL tujuan (50 char)
- **Type**: internal / external
- **Status**: valid / empty

**Example:**
| Text | Href | Type | Status |
|------|------|------|--------|
| Home | /home | internal | valid |
| Google | https://google.com | external | valid |
| Empty Link | # | internal | empty |

#### Tab "Forms"
Detail setiap form beserta input fields:

**Form 1:**
- Action: `/api/submit`
- Method: POST
- Inputs: 5
- Status: complete

**Input Fields:**
| Name | Type |
|------|------|
| email | email |
| password | password |
| remember | checkbox |

## 🎯 Use Cases

### Use Case 1: Test Homepage

**Tujuan:** Cek apakah semua elemen di homepage berfungsi

```
URL: https://yourwebsite.com
Deep Component Test: ✅ ON

Hasil:
✅ 15/15 buttons clickable
✅ 20/20 images loaded
✅ 45/45 links valid
✅ 2/2 forms complete
```

### Use Case 2: Detect Broken Images

**Tujuan:** Find broken images

```
URL: https://yourwebsite.com/products

Hasil:
❌ 3 broken images detected!

Details:
- product-1.jpg (0x0) - broken
- banner.png (0x0) - broken
- icon.svg (0x0) - broken
```

### Use Case 3: Form Validation

**Tujuan:** Check if forms are complete

```
URL: https://yourwebsite.com/contact

Hasil:
⚠️ 1/2 forms incomplete

Form 1: ✅ Complete
- Has action: /api/contact
- Has submit button: Yes

Form 2: ❌ Incomplete
- Has action: No
- Has submit button: No
```

### Use Case 4: Link Checking

**Tujuan:** Find empty or broken links

```
URL: https://yourwebsite.com

Hasil:
⚠️ 5 empty links found!

Empty Links:
- "Click Here" → #
- "Learn More" → #
- "Read More" → #
```

## 📥 Output Files

Setelah test selesai, di folder `artifacts/<run_id>/page_0000/`:

1. **`component_test.json`** - Full detail semua komponen
2. **`screenshot.png`** - Screenshot halaman
3. **`page.html`** - Saved HTML
4. **`result.json`** - Overall test result

## 💡 Tips & Best Practices

### ✅ DO:

1. **Test satu halaman dulu**
   - Mulai dengan Single Page mode
   - Pastikan Deep Component Test = ON

2. **Check hasil detail**
   - Buka expander untuk setiap halaman
   - Review tab Buttons, Images, Links, Forms

3. **Fokus pada yang broken**
   - Cari badge merah/warning
   - Fix broken images/links

4. **Export reports**
   - Download HTML report untuk share
   - Download JSON untuk automation

### ❌ DON'T:

1. **Jangan test terlalu banyak halaman sekaligus**
   - Deep test butuh waktu ~10-15 detik per halaman
   - Untuk crawler mode, batasi max 5-10 pages

2. **Jangan lupa timeout**
   - Increase timeout ke 20-30s untuk halaman besar
   - Slow pages butuh waktu lebih lama

## 🔧 Advanced Options

### Enable Form Submission Test

**⚠️ Experimental!**

Untuk test form submission (fill & submit):
```
Deep Component Test: ✅ ON
Test Forms Submission: ✅ ON  (default OFF)
```

**Note:** Form submission test akan:
- Fill form dengan dummy data
- Submit form (tanpa konfirmasi)
- ⚠️ **Bisa create data di server!**

**Recommendation:** Jangan enable untuk production!

### Combine dengan Crawler

Test multiple pages dengan deep component test:

```
Mode: Crawler Mode
Base URL: https://yourwebsite.com
Max Pages: 5
Deep Component Test: ✅ ON

Hasil:
5 pages tested dengan deep analysis
Total buttons tested: 75
Total images tested: 100
Total links tested: 250
```

## 📊 Interpret Results

### Green Badge (✅ Good)
```
15/15 buttons working ✅
All images loaded ✅
No broken links ✅
```
**Action:** No action needed!

### Yellow Badge (⚠️ Warning)
```
2 images without alt text
5 empty links (#)
```
**Action:** Improve for better accessibility & UX

### Red Badge (❌ Error)
```
3 broken images ❌
2 disabled buttons (should be enabled) ❌
1 form incomplete ❌
```
**Action:** Fix immediately!

## 🎯 Real Example

### Test Google.com

**Input:**
```
URL: https://google.com
Deep Component Test: ✅
```

**Output:**
```
Summary:
✅ Buttons: 2/2 working
✅ Images: 1/1 loaded (Google logo)
✅ Links: 15/15 valid
✅ Forms: 1/1 complete (search form)

Details:
Buttons:
- "Google Search" (clickable, visible, enabled)
- "I'm Feeling Lucky" (clickable, visible, enabled)

Images:
- Google logo (272x92, loaded, has alt)

Forms:
- Search Form (action=/search, method=GET, 1 input)
  Input: q (type=text)
```

## ❓ FAQ

**Q: Berapa lama deep component test?**
A: ~10-15 detik per halaman (tergantung jumlah element)

**Q: Apakah bisa test halaman yang butuh login?**
A: Tidak otomatis. Gunakan YAML scenario untuk login dulu.

**Q: Apakah form benar-benar di-submit?**
A: Tidak, kecuali Anda enable "Test Forms Submission"

**Q: Berapa banyak element yang di-test?**
A: Semua! Tapi output dibatasi 50 link, 20 button untuk performa.

**Q: Apakah bisa test SPA (React/Vue)?**
A: Bisa, tapi perlu wait time lebih lama untuk dynamic content.

## 🚀 Next Steps

1. ✅ Test homepage Anda
2. ✅ Fix broken images/links yang ditemukan
3. ✅ Improve form completeness
4. ✅ Setup regular testing (weekly/monthly)
5. ✅ Export & share reports dengan tim

---

**Happy Testing! 🎉**

Butuh bantuan? Check [README.md](README.md) atau buka issue di GitHub.

