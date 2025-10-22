# 🚀 Load Generator Guide - Enterprise Load Testing

## 📋 Daftar Isi

- [Pengenalan](#pengenalan)
- [System Scale Detection](#system-scale-detection)
- [Load Generator Configuration](#load-generator-configuration)
- [Enterprise Features](#enterprise-features)
- [Performance Metrics](#performance-metrics)
- [Resource Monitoring](#resource-monitoring)
- [Best Practices](#best-practices)
- [Contoh Penggunaan](#contoh-penggunaan)

## Pengenalan

Load Generator adalah fitur enterprise untuk melakukan load testing yang scalable seperti JMeter. Fitur ini mendukung:

- **Multiple Load Generators**: Distributed testing across multiple instances
- **Thread Groups**: Multiple concurrent test scenarios
- **Resource Monitoring**: Real-time CPU dan memory tracking
- **Enterprise Scale**: Support hingga 10,000+ virtual users
- **Performance Analytics**: Detailed response time dan throughput analysis

## System Scale Detection

### Automatic Scale Detection

Load Generator secara otomatis mendeteksi kapasitas sistem dan menyesuaikan rekomendasi:

#### **Small Scale** (4 vCPU, 8 GB RAM)
- **Max Virtual Users**: 1,000 VU
- **Max RPS**: 1,000 requests/second
- **Recommended**: 10-100 VU untuk testing

#### **Medium Scale** (8 vCPU, 16 GB RAM)
- **Max Virtual Users**: 5,000 VU
- **Max RPS**: 10,000 requests/second
- **Recommended**: 50-500 VU untuk testing

#### **Large Scale** (16+ vCPU, 32+ GB RAM)
- **Max Virtual Users**: 10,000+ VU
- **Max RPS**: 25,000+ requests/second
- **Recommended**: 100-1,000 VU untuk testing

### System Requirements

| Scale | CPU | RAM | Network | Max VU | Max RPS |
|-------|-----|-----|---------|--------|---------|
| **Small** | 4 vCPU | 8 GB | 1 Gbps | 1,000 | 1,000 |
| **Medium** | 8 vCPU | 16 GB | 10 Gbps | 5,000 | 10,000 |
| **Large** | 16+ vCPU | 32+ GB | 25+ Gbps | 10,000+ | 25,000+ |

## Load Generator Configuration

### Basic Configuration

#### Target URL
- **URL yang akan di-load test**
- Support HTTP/HTTPS protocols
- Contoh: `https://api.example.com/endpoint`

#### Virtual Users
- **Jumlah virtual users bersamaan**
- Range: 1 - 10,000+ (tergantung sistem)
- Rekomendasi: Mulai dengan 10-50 VU

#### Duration
- **Durasi test dalam detik**
- Range: 10 - 3,600 detik
- Rekomendasi: 30-120 detik untuk test awal

#### Ramp Up/Down
- **Ramp Up**: Waktu untuk mencapai full load
- **Ramp Down**: Waktu untuk mengurangi load
- Rekomendasi: 10-20% dari total durasi

#### Think Time
- **Waktu tunggu antara request**
- Range: 0.0 - 10.0 detik
- Rekomendasi: 1-3 detik untuk realistic load

### Advanced Configuration

#### Scenario Management
- **Scenario Name**: Nama scenario untuk identifikasi
- **Test Plan Name**: Nama test plan
- **Thread Groups**: Multiple concurrent scenarios

#### Resource Limits
- **Max Concurrent Browsers**: 1-20 browsers
- **Browser Memory Limit**: 64-512 MB per browser
- **Connection Pool Size**: 10-100 connections

#### Resource Monitoring
- **Enable Resource Monitoring**: Real-time CPU/memory tracking
- **Max CPU Usage**: 50-95% threshold
- **Max Memory Usage**: 50-95% threshold

## Enterprise Features

### 1. Thread Groups

Load Generator mendukung multiple thread groups seperti JMeter:

```python
thread_groups = [
    {
        "name": "Login Users",
        "virtual_users": 100,
        "ramp_up_seconds": 10,
        "duration_seconds": 60,
        "scenario": "login_flow"
    },
    {
        "name": "Browse Users", 
        "virtual_users": 200,
        "ramp_up_seconds": 15,
        "duration_seconds": 60,
        "scenario": "browse_flow"
    }
]
```

### 2. Resource Monitoring

Real-time monitoring selama load test:

- **CPU Usage**: Peak dan average CPU usage
- **Memory Usage**: Peak dan average memory usage
- **Resource Alerts**: Warning saat resource usage tinggi
- **Performance Impact**: Correlation antara resource dan performance

### 3. Performance Analytics

#### Response Time Analysis
- **Min/Max Response Time**: Response time terendah/tertinggi
- **Average Response Time**: Rata-rata response time
- **Percentiles**: P50, P90, P95, P99 response times
- **Response Time Distribution**: Histogram response times

#### Throughput Analysis
- **Requests per Second (RPS)**: Throughput rate
- **Peak RPS**: Maximum throughput achieved
- **Average RPS**: Average throughput over time
- **Throughput Trends**: RPS over time analysis

#### Error Analysis
- **Error Rate**: Percentage of failed requests
- **Error Types**: Categorized error analysis
- **Error Trends**: Error rate over time
- **Error Impact**: Correlation dengan performance

### 4. System Information

#### Load Generator Scale
- **Automatic Detection**: System scale detection
- **Capacity Planning**: Resource capacity analysis
- **Performance Baseline**: System performance baseline

#### Hardware Specs
- **CPU Cores**: Number of CPU cores
- **Memory**: Total system memory
- **Platform**: Operating system info
- **Architecture**: System architecture

## Performance Metrics

### Key Performance Indicators (KPIs)

#### 1. Success Rate
- **Target**: >95% untuk production
- **Warning**: <90% menunjukkan masalah
- **Critical**: <80% menunjukkan masalah serius

#### 2. Response Time
- **Target**: <2 detik untuk web applications
- **Warning**: >5 detik menunjukkan masalah
- **Critical**: >10 detik menunjukkan masalah serius

#### 3. Throughput
- **Target**: Sesuai dengan expected load
- **Warning**: <50% dari expected throughput
- **Critical**: <25% dari expected throughput

#### 4. Resource Usage
- **CPU**: <80% untuk optimal performance
- **Memory**: <85% untuk optimal performance
- **Network**: Sesuai dengan bandwidth capacity

### Performance Benchmarks

#### Web Applications
- **Response Time**: <2 detik
- **Success Rate**: >95%
- **Throughput**: Sesuai dengan expected load
- **Resource Usage**: <80% CPU, <85% Memory

#### API Endpoints
- **Response Time**: <1 detik
- **Success Rate**: >99%
- **Throughput**: Sesuai dengan expected load
- **Resource Usage**: <70% CPU, <80% Memory

#### Database Applications
- **Response Time**: <3 detik
- **Success Rate**: >95%
- **Throughput**: Sesuai dengan expected load
- **Resource Usage**: <75% CPU, <85% Memory

## Resource Monitoring

### Real-time Monitoring

#### CPU Monitoring
- **Peak CPU Usage**: Maximum CPU usage during test
- **Average CPU Usage**: Average CPU usage over time
- **CPU Trends**: CPU usage over time
- **CPU Alerts**: Warning saat CPU usage tinggi

#### Memory Monitoring
- **Peak Memory Usage**: Maximum memory usage during test
- **Average Memory Usage**: Average memory usage over time
- **Memory Trends**: Memory usage over time
- **Memory Alerts**: Warning saat memory usage tinggi

#### Network Monitoring
- **Bandwidth Usage**: Network bandwidth utilization
- **Connection Count**: Number of active connections
- **Network Latency**: Network latency measurements
- **Packet Loss**: Network packet loss rate

### Resource Optimization

#### Browser Optimization
- **Memory Limits**: 64-512 MB per browser
- **Concurrent Limits**: 1-20 browsers bersamaan
- **Resource Cleanup**: Aggressive cleanup setelah test
- **Connection Pooling**: Reuse connections untuk efisiensi

#### System Optimization
- **CPU Affinity**: Bind processes ke specific CPUs
- **Memory Management**: Optimize memory allocation
- **Network Optimization**: Optimize network settings
- **I/O Optimization**: Optimize disk I/O operations

## Best Practices

### 1. Test Planning

#### Start Small
```
Virtual Users: 10-50
Duration: 30-60 seconds
Ramp Up: 10-20 seconds
Think Time: 1-3 seconds
```

#### Gradual Increase
```
Step 1: 10 VU, 30s
Step 2: 50 VU, 60s
Step 3: 100 VU, 120s
Step 4: 500 VU, 300s
```

#### Production Testing
```
Virtual Users: 100-1000
Duration: 300-1800 seconds
Ramp Up: 60-300 seconds
Think Time: 1-2 seconds
```

### 2. Resource Management

#### System Resources
- **Monitor CPU Usage**: Keep <80% untuk optimal performance
- **Monitor Memory Usage**: Keep <85% untuk optimal performance
- **Monitor Network**: Ensure sufficient bandwidth
- **Monitor Disk I/O**: Optimize disk operations

#### Load Generator Resources
- **Browser Limits**: Limit concurrent browsers
- **Memory Limits**: Set memory limits per browser
- **Connection Limits**: Limit concurrent connections
- **Timeout Settings**: Set appropriate timeouts

### 3. Test Scenarios

#### Load Testing
- **Tujuan**: Mengukur performa normal
- **Load**: Expected user load
- **Duration**: 5-15 menit
- **Metrics**: Response time, throughput, success rate

#### Stress Testing
- **Tujuan**: Mencari breaking point
- **Load**: Beyond normal capacity
- **Duration**: 10-30 menit
- **Metrics**: Breaking point, error rate, resource usage

#### Spike Testing
- **Tujuan**: Test sudden load increase
- **Pattern**: Sudden spike in users
- **Duration**: Short bursts
- **Metrics**: Recovery time, error rate, performance impact

### 4. Monitoring and Alerting

#### Key Metrics to Monitor
- **Response Time**: Average, P95, P99
- **Throughput**: RPS, peak RPS
- **Error Rate**: Success rate, error types
- **Resource Usage**: CPU, memory, network

#### Alert Thresholds
- **Response Time**: >5 detik
- **Error Rate**: >5%
- **CPU Usage**: >80%
- **Memory Usage**: >85%

## Contoh Penggunaan

### 1. Basic Load Test

```python
config = create_load_generator_config(
    target_url="https://api.example.com/users",
    virtual_users=50,
    duration_seconds=60,
    ramp_up_seconds=10,
    think_time_seconds=1.0
)
```

### 2. High Load Test

```python
config = create_load_generator_config(
    target_url="https://api.example.com/endpoint",
    virtual_users=500,
    duration_seconds=300,
    ramp_up_seconds=60,
    think_time_seconds=0.5
)
```

### 3. Enterprise Load Test

```python
config = create_load_generator_config(
    target_url="https://api.example.com/endpoint",
    virtual_users=1000,
    duration_seconds=600,
    ramp_up_seconds=120,
    think_time_seconds=1.0,
    scenario_name="Enterprise Load Test",
    test_plan_name="Production Load Test"
)

# Set advanced options
config.max_concurrent_browsers = 10
config.browser_memory_limit_mb = 256
config.enable_resource_monitoring = True
config.max_cpu_usage_percent = 80
config.max_memory_usage_percent = 85
```

### 4. Multiple Thread Groups

```python
config = create_load_generator_config(
    target_url="https://api.example.com/endpoint",
    virtual_users=100,
    duration_seconds=120
)

# Add thread groups
config.thread_groups = [
    {
        "name": "Login Users",
        "virtual_users": 50,
        "ramp_up_seconds": 10,
        "duration_seconds": 120,
        "scenario": "login_flow"
    },
    {
        "name": "Browse Users",
        "virtual_users": 50,
        "ramp_up_seconds": 15,
        "duration_seconds": 120,
        "scenario": "browse_flow"
    }
]
```

## Performance Comparison

### Load Generator vs Stress Test

| Feature | Load Generator | Stress Test |
|---------|----------------|-------------|
| **Scale** | Enterprise (1K-10K VU) | Basic (1-100 VU) |
| **Thread Groups** | ✅ Multiple | ❌ Single |
| **Resource Monitoring** | ✅ Advanced | ❌ Basic |
| **Performance Analytics** | ✅ Detailed | ❌ Basic |
| **System Detection** | ✅ Automatic | ❌ Manual |
| **Enterprise Features** | ✅ Full | ❌ Limited |

### Performance Capabilities

| System Scale | Max VU | Max RPS | Recommended VU |
|-------------|---------|---------|----------------|
| **Small** | 1,000 | 1,000 | 10-100 |
| **Medium** | 5,000 | 10,000 | 50-500 |
| **Large** | 10,000+ | 25,000+ | 100-1,000 |

## Troubleshooting

### Common Issues

#### 1. High Resource Usage
**Penyebab:**
- Too many virtual users
- Insufficient system resources
- Inefficient browser configuration

**Solusi:**
- Reduce virtual users
- Increase system resources
- Optimize browser settings
- Enable resource monitoring

#### 2. Low Throughput
**Penyebab:**
- High think time
- Network limitations
- Server bottlenecks
- Browser limitations

**Solusi:**
- Reduce think time
- Check network bandwidth
- Optimize server configuration
- Increase concurrent browsers

#### 3. High Error Rate
**Penyebab:**
- Server overload
- Network issues
- Timeout settings
- Application bugs

**Solusi:**
- Reduce load
- Check network connectivity
- Increase timeout settings
- Review application logs

### Performance Optimization

#### 1. System Optimization
- **CPU**: Use high-performance CPUs
- **Memory**: Ensure sufficient RAM
- **Network**: Use high-bandwidth connections
- **Storage**: Use SSD storage

#### 2. Load Generator Optimization
- **Browser Limits**: Optimize concurrent browsers
- **Memory Limits**: Set appropriate memory limits
- **Connection Pooling**: Reuse connections
- **Resource Monitoring**: Enable monitoring

#### 3. Application Optimization
- **Database**: Optimize database queries
- **Caching**: Implement caching strategies
- **Load Balancing**: Use load balancers
- **CDN**: Use content delivery networks

## Kesimpulan

Load Generator adalah solusi enterprise untuk load testing yang:

- **Scalable**: Support hingga 10,000+ virtual users
- **Professional**: Enterprise-grade features seperti JMeter
- **Intelligent**: Automatic system scale detection
- **Comprehensive**: Detailed performance analytics
- **Resource-Aware**: Real-time resource monitoring

Fitur ini ideal untuk:
- **Enterprise Applications**: Large-scale load testing
- **Performance Testing**: Comprehensive performance analysis
- **Capacity Planning**: Resource capacity planning
- **Production Testing**: Production-like load testing

Load Generator memberikan kemampuan load testing yang setara dengan tools enterprise seperti JMeter, dengan interface yang user-friendly dan integrasi yang seamless dengan Black-Box Testing Tool.
