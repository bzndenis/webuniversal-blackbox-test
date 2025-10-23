# PDF Export Guide

## Overview
Fitur PDF Export memungkinkan pengguna untuk mengunduh laporan testing dalam format PDF yang profesional dan mudah dibaca. Laporan PDF ini dirancang khusus untuk keperluan presentasi dan dokumentasi resmi.

## Fitur Utama

### 1. Laporan Profesional
- **Header yang jelas** dengan informasi run ID, tanggal, dan mode testing
- **Executive Summary** dengan metrik kunci dan status testing
- **Tabel hasil** yang terstruktur dengan color coding
- **Analisis komponen** detail untuk setiap elemen yang ditest
- **Rekomendasi** berdasarkan hasil testing
- **Footer** dengan informasi generator dan timestamp

### 2. Format yang Mudah Dibaca
- **Typography profesional** dengan font Helvetica
- **Color coding** untuk status (Success/Error/Info)
- **Tabel terstruktur** dengan header yang jelas
- **Spacing yang konsisten** untuk readability
- **Page numbering** dan header/footer di setiap halaman

### 3. Dukungan Multiple Test Types
- **Regular Testing**: Crawler, Single Page, YAML Scenario
- **Stress Testing**: Performance metrics dan error analysis
- **Component Testing**: Detail analisis buttons, images, links, forms

## Struktur Laporan PDF

### 1. Header Section
- Title: "BLACK-BOX FUNCTIONAL TESTING REPORT"
- Report ID dan timestamp
- Test mode dan target URL
- Garis pemisah profesional

### 2. Executive Summary
- Ringkasan hasil testing
- Tabel metrik kunci dengan status color coding
- Success rate dan performance indicators

### 3. Test Overview
- Konfigurasi testing (headless, timeout, dll)
- Durasi testing
- Parameter yang digunakan

### 4. Detailed Results
- Tabel hasil per halaman
- Status, load time, error count, screenshots
- Limit 20 halaman pertama (dengan note untuk halaman lainnya)

### 5. Component Analysis (jika tersedia)
- Summary komponen (buttons, images, links, forms)
- Detail analisis per komponen
- Status dan rekomendasi per elemen

### 6. Screenshots & Evidence
- Jumlah screenshot yang diambil
- Lokasi file artifacts

### 7. Recommendations
- Analisis otomatis berdasarkan hasil
- Rekomendasi perbaikan
- Best practices

### 8. Footer
- Informasi generator
- Timestamp
- Support information

## Stress Test PDF Features

### 1. Stress Test Summary
- Concurrent users dan duration
- Success rate dan response time
- Key performance metrics

### 2. Detailed Performance Metrics
- Min/Max/P95/P99 response times
- Configuration parameters
- Error analysis dengan breakdown

### 3. Error Analysis
- Tabel error types dan counts
- Performance bottleneck identification

## Cara Menggunakan

### 1. Melalui UI Streamlit
1. Jalankan testing (Crawler/Single Page/YAML/Stress Test)
2. Setelah testing selesai, scroll ke bagian "📄 Export Reports"
3. Klik tombol "📄 Download PDF"
4. File PDF akan otomatis terunduh

### 2. Programmatic Usage
```python
from app.services.pdf_reporter import PDFReporter

# Create PDF reporter
pdf_reporter = PDFReporter("artifacts_directory")

# Generate PDF report
pdf_path = pdf_reporter.generate_report(run_id, test_results)
```

## Technical Details

### Dependencies
- **reportlab**: Library utama untuk PDF generation
- **weasyprint**: Alternative PDF generator (optional)

### File Structure
```
app/services/pdf_reporter.py    # Main PDF reporter class
requirements.txt                # Updated dengan PDF dependencies
```

### Key Classes
- **PDFReporter**: Main class untuk PDF generation
- **Custom Styles**: Professional styling untuk laporan
- **Table Generation**: Structured data presentation
- **Error Handling**: Graceful fallback jika PDF generation gagal

## Customization

### 1. Styling
Edit `_setup_custom_styles()` method untuk mengubah:
- Font sizes dan colors
- Spacing dan alignment
- Table styling

### 2. Content Sections
Modify individual `_create_*` methods untuk:
- Menambah/mengurangi sections
- Mengubah format data
- Menyesuaikan dengan kebutuhan spesifik

### 3. Page Layout
Adjust `SimpleDocTemplate` parameters:
- Page size (A4, Letter, dll)
- Margins
- Header/footer positioning

## Error Handling

### 1. Graceful Degradation
- Jika PDF generation gagal, UI akan menampilkan warning
- Testing tetap berjalan normal
- User tetap bisa download HTML/CSV/JSON

### 2. Common Issues
- **Missing dependencies**: Install reportlab dan weasyprint
- **Permission issues**: Pastikan write access ke artifacts directory
- **Memory issues**: Untuk laporan besar, consider pagination

### 3. Debugging
- Check logs untuk error details
- Verify file permissions
- Test dengan data sample terlebih dahulu

## Performance Considerations

### 1. File Size
- PDF dengan screenshots bisa besar
- Consider image compression untuk production
- Limit jumlah halaman jika diperlukan

### 2. Generation Time
- PDF generation membutuhkan waktu tambahan
- Progress indicator ditampilkan selama generation
- Consider async generation untuk large reports

### 3. Memory Usage
- ReportLab menggunakan memory untuk rendering
- Monitor memory usage untuk large datasets
- Consider streaming untuk very large reports

## Best Practices

### 1. Content Organization
- Gunakan heading hierarchy yang konsisten
- Group related information
- Provide clear section breaks

### 2. Data Presentation
- Gunakan tabel untuk structured data
- Color coding untuk status indicators
- Limit text per section untuk readability

### 3. Professional Appearance
- Consistent spacing dan alignment
- Professional color scheme
- Clear typography hierarchy

## Future Enhancements

### 1. Advanced Features
- **Charts dan graphs** untuk performance data
- **Interactive elements** (jika menggunakan PDF.js)
- **Custom branding** dengan logo perusahaan

### 2. Integration
- **Email integration** untuk automatic report sending
- **Cloud storage** integration
- **API endpoints** untuk programmatic access

### 3. Customization
- **Template system** untuk different report types
- **User preferences** untuk styling
- **Multi-language** support

## Troubleshooting

### Common Issues dan Solutions

1. **PDF tidak ter-generate**
   - Check dependencies: `pip install reportlab weasyprint`
   - Verify file permissions
   - Check disk space

2. **PDF kosong atau corrupt**
   - Check data structure
   - Verify test results format
   - Check for encoding issues

3. **Performance issues**
   - Reduce data size
   - Optimize image handling
   - Consider pagination

4. **Styling issues**
   - Check font availability
   - Verify color definitions
   - Test dengan different page sizes

## Support

Untuk issues atau pertanyaan terkait PDF export:
1. Check logs untuk error details
2. Verify dependencies installation
3. Test dengan sample data
4. Check file permissions dan disk space

PDF export feature memberikan kemampuan untuk menghasilkan laporan profesional yang siap untuk presentasi dan dokumentasi resmi.
