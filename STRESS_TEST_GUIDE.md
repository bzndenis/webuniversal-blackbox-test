# 🚀 Stress Test Guide

Panduan lengkap untuk menggunakan fitur stress test pada Black-Box Testing Tool.

## 📋 Daftar Isi

- [Pengenalan](#pengenalan)
- [Konfigurasi Stress Test](#konfigurasi-stress-test)
- [Parameter Stress Test](#parameter-stress-test)
- [Custom Actions](#custom-actions)
- [Hasil dan Analisis](#hasil-dan-analisis)
- [Best Practices](#best-practices)
- [Contoh Penggunaan](#contoh-penggunaan)
- [Troubleshooting](#troubleshooting)

## Pengenalan

Stress test adalah fitur untuk menguji performa dan stabilitas web application di bawah beban tinggi. Fitur ini mensimulasikan multiple user yang mengakses aplikasi secara bersamaan untuk mengukur:

- **Response Time**: Waktu respons aplikasi
- **Throughput**: Jumlah request per detik
- **Error Rate**: Persentase error yang terjadi
- **Stability**: Stabilitas aplikasi di bawah beban

## Konfigurasi Stress Test

### 1. Mode Selection
Pilih **"Stress Test"** dari dropdown Test Mode di sidebar.

### 2. Basic Configuration

#### Target URL
- **URL yang akan di-stress test**
- Contoh: `https://example.com`, `https://api.example.com/endpoint`

#### Concurrent Users
- **Jumlah user bersamaan** (1-100)
- Default: 10 users
- Rekomendasi: Mulai dengan 5-10 users, tingkatkan secara bertahap

#### Duration (seconds)
- **Durasi test** (10-3600 detik)
- Default: 60 detik
- Rekomendasi: 30-120 detik untuk test awal

#### Ramp Up (seconds)
- **Waktu untuk mencapai full load** (0-300 detik)
- Default: 10 detik
- Rekomendasi: 10-20% dari total durasi

#### Think Time (seconds)
- **Waktu tunggu antara request** (0-10 detik)
- Default: 1.0 detik
- Rekomendasi: 0.5-2.0 detik untuk simulasi realistis

## Parameter Stress Test

### Advanced Options

#### Request Timeout (seconds)
- **Timeout per request** (5-120 detik)
- Default: 30 detik
- Rekomendasi: 10-30 detik

#### Custom Actions (JSON)
Aksi tambahan yang akan dilakukan pada setiap request:

```json
[
  {
    "type": "click",
    "selector": "button.submit"
  },
  {
    "type": "fill",
    "selector": "input[name='email']",
    "value": "test@example.com"
  },
  {
    "type": "wait",
    "seconds": 1
  }
]
```

### Jenis Aksi yang Didukung

#### 1. Click Action
```json
{
  "type": "click",
  "selector": "button, .btn, #submit"
}
```

#### 2. Fill Action
```json
{
  "type": "fill",
  "selector": "input[name='username']",
  "value": "testuser"
}
```

#### 3. Wait Action
```json
{
  "type": "wait",
  "seconds": 2
}
```

#### 4. Screenshot Action
```json
{
  "type": "screenshot"
}
```

## Hasil dan Analisis

### Key Metrics

#### 1. Success Rate
- **Persentase request yang berhasil**
- Target: >95% untuk aplikasi production
- Warning: <80% menunjukkan masalah serius

#### 2. Response Time Analysis
- **Average**: Rata-rata response time
- **Min/Max**: Response time terendah/tertinggi
- **95th Percentile**: 95% request selesai dalam waktu ini
- **99th Percentile**: 99% request selesai dalam waktu ini

#### 3. Throughput
- **Requests per Second (RPS)**
- Mengukur kapasitas aplikasi
- Rekomendasi: Monitor RPS vs Response Time

#### 4. Error Analysis
- **Timeout**: Request timeout
- **Network Error**: Masalah koneksi
- **Server Error**: Error 5xx
- **Client Error**: Error 4xx

### Performance Chart
Grafik performa yang menunjukkan:
- Requests per second over time
- Response time trends
- Error patterns

## Best Practices

### 1. Test Planning

#### Start Small
```
Concurrent Users: 5
Duration: 30 seconds
Ramp Up: 5 seconds
```

#### Gradual Increase
```
Step 1: 5 users, 30s
Step 2: 10 users, 60s
Step 3: 20 users, 120s
Step 4: 50 users, 300s
```

### 2. Environment Considerations

#### Test Environment
- Gunakan environment yang mirip dengan production
- Pastikan database dan services tersedia
- Monitor resource usage (CPU, Memory, Network)

#### Production Testing
- **HATI-HATI**: Jangan test production tanpa persetujuan
- Gunakan waktu maintenance window
- Monitor impact pada user real

### 3. Monitoring

#### System Metrics
- CPU usage
- Memory consumption
- Network bandwidth
- Database connections

#### Application Metrics
- Response time percentiles
- Error rates
- Throughput capacity
- Resource utilization

### 4. Test Scenarios

#### Load Testing
- **Tujuan**: Mengukur performa normal
- **Load**: Expected user load
- **Duration**: 5-15 menit

#### Stress Testing
- **Tujuan**: Mencari breaking point
- **Load**: Beyond normal capacity
- **Duration**: 10-30 menit

#### Spike Testing
- **Tujuan**: Test sudden load increase
- **Pattern**: Sudden spike in users
- **Duration**: Short bursts

## Contoh Penggunaan

### 1. Basic Website Test
```python
config = create_stress_test_config(
    url="https://example.com",
    concurrent_users=10,
    duration_seconds=60,
    ramp_up_seconds=10,
    think_time_seconds=1.0
)
```

### 2. API Endpoint Test
```python
config = create_stress_test_config(
    url="https://api.example.com/users",
    concurrent_users=20,
    duration_seconds=120,
    ramp_up_seconds=20,
    think_time_seconds=0.5
)
```

### 3. Form Submission Test
```python
actions = [
    {"type": "fill", "selector": "input[name='email']", "value": "test@example.com"},
    {"type": "fill", "selector": "input[name='password']", "value": "password123"},
    {"type": "click", "selector": "button[type='submit']"},
    {"type": "wait", "seconds": 2}
]

config = create_stress_test_config(
    url="https://example.com/login",
    concurrent_users=5,
    duration_seconds=60,
    actions=actions
)
```

### 4. E-commerce Test
```python
actions = [
    {"type": "click", "selector": ".product-card"},
    {"type": "click", "selector": ".add-to-cart"},
    {"type": "wait", "seconds": 1},
    {"type": "click", "selector": ".checkout-btn"}
]

config = create_stress_test_config(
    url="https://shop.example.com",
    concurrent_users=15,
    duration_seconds=180,
    actions=actions
)
```

## Troubleshooting

### Common Issues

#### 1. High Error Rate
**Penyebab:**
- Server overload
- Database connection limits
- Network issues
- Application bugs

**Solusi:**
- Kurangi concurrent users
- Periksa server resources
- Check database connections
- Review application logs

#### 2. Slow Response Time
**Penyebab:**
- Database queries slow
- External API calls
- Resource constraints
- Network latency

**Solusi:**
- Optimize database queries
- Cache frequently accessed data
- Use CDN for static content
- Monitor external dependencies

#### 3. Timeout Errors
**Penyebab:**
- Request timeout terlalu pendek
- Server processing time lama
- Network issues

**Solusi:**
- Increase timeout value
- Optimize application performance
- Check network connectivity

#### 4. Memory Issues
**Penyebab:**
- Too many concurrent users
- Memory leaks in application
- Insufficient server memory

**Solusi:**
- Reduce concurrent users
- Monitor memory usage
- Optimize application code
- Increase server memory

### Performance Optimization

#### 1. Database Optimization
- Index optimization
- Query optimization
- Connection pooling
- Caching strategies

#### 2. Application Optimization
- Code profiling
- Memory management
- Async processing
- Load balancing

#### 3. Infrastructure Optimization
- Server scaling
- CDN implementation
- Database scaling
- Network optimization

## Monitoring dan Alerting

### Key Metrics to Monitor

#### 1. Response Time
- Average response time
- 95th percentile
- 99th percentile
- Max response time

#### 2. Throughput
- Requests per second
- Successful requests
- Failed requests
- Error rate

#### 3. System Resources
- CPU usage
- Memory usage
- Network bandwidth
- Disk I/O

#### 4. Application Health
- Database connections
- Cache hit rate
- External API calls
- Error logs

### Alerting Thresholds

#### Warning Levels
- Response time > 2 seconds
- Error rate > 5%
- CPU usage > 80%
- Memory usage > 90%

#### Critical Levels
- Response time > 5 seconds
- Error rate > 20%
- CPU usage > 95%
- Memory usage > 95%

## Kesimpulan

Stress test adalah tool penting untuk:
- Mengukur performa aplikasi
- Mengidentifikasi bottleneck
- Memvalidasi capacity planning
- Memastikan stabilitas sistem

Gunakan stress test secara bertahap dan monitor hasilnya untuk mendapatkan insight yang berguna tentang performa aplikasi Anda.

---

**Catatan**: Selalu test di environment yang tepat dan dapatkan persetujuan sebelum melakukan stress test pada production environment.
