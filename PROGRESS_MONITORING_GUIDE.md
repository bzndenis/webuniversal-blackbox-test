# 📊 Real-time Progress Monitoring Guide

## Overview

Fitur **Real-time Progress Monitoring** memberikan feedback langsung selama Load Generator berjalan, menampilkan:

- **Progress Bar**: Persentase completion real-time
- **Live Metrics**: RPS, Success Rate, Active Users, Completed Requests
- **Real-time Charts**: Visualisasi performa selama test berjalan
- **Summary Statistics**: Analisis mendalam hasil test

## 🚀 Features

### 1. Real-time Progress Updates
```
🔄 Running... 45.2% | Active: 15 | RPS: 12.5 | Success: 98.5% | Completed: 1,250
```

### 2. Live Metrics Dashboard
- **Progress**: Persentase completion
- **Active Users**: Jumlah virtual users yang sedang aktif
- **Completed**: Total requests yang berhasil
- **RPS**: Requests per second saat ini
- **Success Rate**: Persentase keberhasilan

### 3. Real-time Performance Charts
- **Overview Chart**: RPS, Success Rate, Active Users, Progress
- **Detailed Metrics**: Multiple charts untuk analisis mendalam
- **Summary Stats**: Timeline dan statistik lengkap

## 📋 Implementation

### Progress Monitor Class
```python
from app.services.progress_monitor import create_progress_monitor, create_streamlit_updater

# Create progress monitor
progress_monitor = create_progress_monitor()

# Create Streamlit updater
streamlit_updater = create_streamlit_updater(progress_bar, status_text, metrics_container)

# Start monitoring
await progress_monitor.start_monitoring(generator, streamlit_updater.update_progress)

# Run load test
result = await generator.run_load_test()

# Stop monitoring
await progress_monitor.stop_monitoring()
```

### Streamlit Integration
```python
# Create UI components
progress_bar = st.progress(0)
status_text = st.empty()
metrics_container = st.container()
chart_container = st.container()

# Create progress monitor
progress_monitor = create_progress_monitor()
streamlit_updater = create_streamlit_updater(progress_bar, status_text, metrics_container)

# Start monitoring with load test
await progress_monitor.start_monitoring(generator, streamlit_updater.update_progress)
```

## 📊 Chart Types

### 1. Overview Chart
- **RPS**: Requests per second over time
- **Success Rate**: Persentase keberhasilan
- **Active Users**: Jumlah users aktif
- **Progress**: Persentase completion

### 2. Detailed Metrics
- **RPS vs Success Rate**: Korelasi performa
- **Active Users vs Progress**: User scaling
- **Completed vs Failed**: Request analysis

### 3. Summary Statistics
- **Total Duration**: Waktu test keseluruhan
- **Peak RPS**: RPS tertinggi yang dicapai
- **Average RPS**: RPS rata-rata
- **Min Success Rate**: Success rate terendah
- **Max Active Users**: Maksimal users aktif

## 🔧 Configuration

### Update Frequency
```python
# Update setiap 0.5 detik untuk performa optimal
if current_time - self.last_update_time < 0.5:
    return
```

### Throttling
- **UI Updates**: Maksimal 2 updates per detik
- **Chart Data**: Disimpan setiap detik
- **Metrics**: Real-time calculation

## 📈 Data Structure

### Progress Data
```python
{
    'timestamp': float,           # Unix timestamp
    'elapsed_time': float,       # Waktu yang sudah berlalu
    'progress_percent': float,   # Persentase completion
    'active_users': int,         # Users aktif
    'completed_requests': int,   # Requests berhasil
    'failed_requests': int,      # Requests gagal
    'success_rate': float,      # Persentase keberhasilan
    'current_rps': float,       # RPS saat ini
    'peak_rps': float,          # RPS tertinggi
    'estimated_completion': float  # Estimasi selesai
}
```

### Chart Data
```python
{
    'Time (s)': int,                    # Waktu dalam detik
    'RPS': float,                       # Requests per second
    'Success Rate (%)': float,          # Persentase keberhasilan
    'Active Users': int,                # Users aktif
    'Progress (%)': float,              # Persentase completion
    'Completed Requests': int,          # Requests berhasil
    'Failed Requests': int              # Requests gagal
}
```

## 🎯 Use Cases

### 1. Load Testing
- Monitor performa aplikasi under load
- Identifikasi bottleneck real-time
- Track success rate dan response time

### 2. Performance Analysis
- Analisis RPS patterns
- Monitor resource usage
- Identifikasi performance degradation

### 3. Capacity Planning
- Test maksimal concurrent users
- Analisis scaling behavior
- Optimasi resource allocation

## 🚨 Monitoring Alerts

### Success Rate Alerts
```python
if data['success_rate'] < 90:
    # Warning: Low success rate
    st.warning(f"⚠️ Success rate rendah: {data['success_rate']:.1f}%")
```

### RPS Alerts
```python
if data['current_rps'] < expected_rps * 0.5:
    # Warning: Low RPS
    st.warning(f"⚠️ RPS rendah: {data['current_rps']:.1f}")
```

### Resource Alerts
```python
if data['active_users'] > max_capacity:
    # Warning: Over capacity
    st.error(f"❌ Over capacity: {data['active_users']} users")
```

## 📊 Example Output

### Console Output
```
📊 Progress: 10.1% | Active: 0 | RPS: 0.0 | Success: 0.0% | Completed: 0
📊 Progress: 20.0% | Active: 5 | RPS: 0.0 | Success: 0.0% | Completed: 0
📊 Progress: 30.0% | Active: 5 | RPS: 0.0 | Success: 0.0% | Completed: 0
📊 Progress: 40.0% | Active: 5 | RPS: 0.7 | Success: 100.0% | Completed: 3
📊 Progress: 50.0% | Active: 5 | RPS: 1.0 | Success: 100.0% | Completed: 5
```

### Summary Statistics
```
📋 Summary Statistics:
  Max RPS: 1.6
  Avg RPS: 1.1
  Min Success Rate: 0.0%
  Max Active Users: 5
  Total Requests: 23
  Successful Requests: 23
  Failed Requests: 0
```

## 🔧 Troubleshooting

### Issue: Progress tidak update
**Solution**: Pastikan `await progress_monitor.start_monitoring()` dipanggil sebelum load test

### Issue: Chart tidak muncul
**Solution**: Install pandas: `pip install pandas`

### Issue: UI update terlalu lambat
**Solution**: Kurangi update frequency atau gunakan throttling

### Issue: Memory usage tinggi
**Solution**: Batasi jumlah data points atau gunakan sampling

## 📚 Best Practices

### 1. Update Frequency
- **Console**: Update setiap detik
- **UI**: Update setiap 0.5 detik
- **Charts**: Update setiap detik

### 2. Data Storage
- **Memory**: Batasi history data
- **Sampling**: Gunakan sampling untuk data besar
- **Cleanup**: Bersihkan data setelah test selesai

### 3. Performance
- **Throttling**: Gunakan throttling untuk UI updates
- **Async**: Gunakan async/await untuk non-blocking
- **Error Handling**: Handle errors gracefully

## 🎯 Advanced Features

### 1. Custom Metrics
```python
# Tambahkan custom metrics
progress_data['custom_metric'] = calculate_custom_metric()
```

### 2. Alert System
```python
# Implementasi alert system
if data['success_rate'] < threshold:
    send_alert("Low success rate detected")
```

### 3. Export Data
```python
# Export progress data
progress_data = progress_monitor.get_progress_history()
export_to_csv(progress_data, 'progress_data.csv')
```

## 📖 Related Documentation

- [Load Generator Guide](LOAD_GENERATOR_GUIDE.md)
- [Stress Testing Guide](STRESS_TEST_GUIDE.md)
- [Performance Optimization](RESOURCE_OPTIMIZATION.md)

## 🚀 Quick Start

1. **Import modules**:
   ```python
   from app.services.progress_monitor import create_progress_monitor, create_streamlit_updater
   ```

2. **Create monitor**:
   ```python
   progress_monitor = create_progress_monitor()
   ```

3. **Start monitoring**:
   ```python
   await progress_monitor.start_monitoring(generator, callback)
   ```

4. **Run load test**:
   ```python
   result = await generator.run_load_test()
   ```

5. **Stop monitoring**:
   ```python
   await progress_monitor.stop_monitoring()
   ```

## ✅ Success Indicators

- ✅ Progress bar update smooth
- ✅ Metrics update real-time
- ✅ Charts display correctly
- ✅ No memory leaks
- ✅ Error handling works
- ✅ Performance optimal

---

**Real-time Progress Monitoring** memberikan visibility penuh selama load test berjalan, memungkinkan analisis performa yang mendalam dan identifikasi masalah secara real-time.
