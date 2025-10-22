"""
Advanced Load Generator untuk stress testing dengan skala enterprise.
Mendukung multiple load generators dan distributed testing seperti JMeter.
"""

import asyncio
import time
import statistics
import psutil
import platform
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class LoadGeneratorScale(Enum):
    """Skala load generator berdasarkan spesifikasi hardware."""
    SMALL = "small"      # 4 vCPU, 8 GB RAM, 1 Gbps
    MEDIUM = "medium"    # 8 vCPU, 16 GB RAM, 10 Gbps
    LARGE = "large"      # 16+ vCPU, 32+ GB RAM, 25+ Gbps

@dataclass
class SystemSpecs:
    """Spesifikasi sistem untuk load generator."""
    cpu_count: int
    memory_gb: float
    platform: str
    architecture: str
    max_recommended_vu: int
    max_recommended_rps: int
    scale: LoadGeneratorScale

@dataclass
class LoadGeneratorConfig:
    """Konfigurasi untuk load generator."""
    target_url: str
    virtual_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10
    ramp_down_seconds: int = 10
    think_time_seconds: float = 1.0
    timeout_seconds: int = 30
    headless: bool = True
    
    # Advanced settings
    max_concurrent_browsers: int = 5
    browser_memory_limit_mb: int = 128
    connection_pool_size: int = 10
    
    # JMeter-like features
    scenario_name: str = "Default Scenario"
    test_plan_name: str = "Load Test Plan"
    thread_groups: List[Dict[str, Any]] = field(default_factory=list)
    
    # Resource monitoring
    enable_resource_monitoring: bool = True
    resource_check_interval: float = 1.0
    max_cpu_usage_percent: float = 80.0
    max_memory_usage_percent: float = 85.0

@dataclass
class LoadTestResult:
    """Hasil dari load test."""
    test_id: str
    start_time: float
    end_time: float
    duration: float
    
    # Performance metrics
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    
    # Response time metrics
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p90_response_time: float
    p95_response_time: float
    p99_response_time: float
    
    # Throughput metrics
    requests_per_second: float
    peak_rps: float
    average_rps: float
    
    # Error analysis
    errors: Dict[str, int]
    error_rate: float
    
    # Resource usage
    peak_cpu_usage: float
    peak_memory_usage: float
    average_cpu_usage: float
    average_memory_usage: float
    
    # Load generator info
    load_generator_scale: LoadGeneratorScale
    system_specs: SystemSpecs

class AdvancedLoadGenerator:
    """Advanced load generator dengan enterprise features."""
    
    def __init__(self, config: LoadGeneratorConfig):
        self.config = config
        self.results: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.system_specs = self._get_system_specs()
        self.resource_monitor = ResourceMonitor() if config.enable_resource_monitoring else None
        
        # Progress tracking
        self.progress_callback = None
        self.current_progress = 0.0
        self.active_users = 0
        self.completed_requests = 0
        self.failed_requests = 0
        self.current_rps = 0.0
        self.peak_rps = 0.0
        self.elapsed_time = 0.0
        
    def _get_system_specs(self) -> SystemSpecs:
        """Deteksi spesifikasi sistem dan tentukan skala load generator."""
        cpu_count = psutil.cpu_count(logical=True)
        memory_gb = psutil.virtual_memory().total / (1024**3)
        platform_name = platform.system()
        architecture = platform.machine()
        
        # Tentukan skala berdasarkan spesifikasi
        if cpu_count >= 16 and memory_gb >= 32:
            scale = LoadGeneratorScale.LARGE
            max_vu = 10000
            max_rps = 25000
        elif cpu_count >= 8 and memory_gb >= 16:
            scale = LoadGeneratorScale.MEDIUM
            max_vu = 5000
            max_rps = 10000
        else:
            scale = LoadGeneratorScale.SMALL
            max_vu = 1000
            max_rps = 1000
            
        return SystemSpecs(
            cpu_count=cpu_count,
            memory_gb=memory_gb,
            platform=platform_name,
            architecture=architecture,
            max_recommended_vu=max_vu,
            max_recommended_rps=max_rps,
            scale=scale
        )
    
    async def run_load_test(self) -> LoadTestResult:
        """Jalankan load test dengan monitoring resource."""
        logger.info(f"🚀 Starting load test: {self.config.scenario_name}")
        logger.info(f"📊 System specs: {self.system_specs.scale.value} scale")
        logger.info(f"👥 Virtual users: {self.config.virtual_users}")
        logger.info(f"⏱️ Duration: {self.config.duration_seconds}s")
        
        # Validasi kapasitas sistem
        if not self._validate_system_capacity():
            raise ValueError("System capacity insufficient for requested load")
        
        self.start_time = time.time()
        
        # Start resource monitoring
        if self.resource_monitor:
            await self.resource_monitor.start_monitoring()
        
        # Jalankan load test
        try:
            await self._execute_load_test()
        finally:
            self.end_time = time.time()
            
            # Stop resource monitoring
            if self.resource_monitor:
                await self.resource_monitor.stop_monitoring()
        
        return self._calculate_results()
    
    def _validate_system_capacity(self) -> bool:
        """Validasi apakah sistem mampu menangani load yang diminta."""
        if self.config.virtual_users > self.system_specs.max_recommended_vu:
            logger.warning(f"⚠️ Requested VU ({self.config.virtual_users}) exceeds recommended ({self.system_specs.max_recommended_vu})")
            return False
        
        # Check current system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > self.config.max_cpu_usage_percent:
            logger.warning(f"⚠️ Current CPU usage ({cpu_percent}%) exceeds limit ({self.config.max_cpu_usage_percent}%)")
            return False
            
        if memory_percent > self.config.max_memory_usage_percent:
            logger.warning(f"⚠️ Current memory usage ({memory_percent}%) exceeds limit ({self.config.max_memory_usage_percent}%)")
            return False
        
        return True
    
    def set_progress_callback(self, callback):
        """Set callback function untuk progress updates."""
        self.progress_callback = callback
    
    async def _update_progress(self):
        """Update progress dan kirim ke callback."""
        if self.progress_callback:
            # Calculate current metrics
            self.elapsed_time = time.time() - self.start_time if self.start_time else 0
            self.current_rps = self.completed_requests / self.elapsed_time if self.elapsed_time > 0 else 0
            self.peak_rps = max(self.peak_rps, self.current_rps)
            
            # Calculate progress percentage
            if self.config.duration_seconds > 0:
                self.current_progress = min(100.0, (self.elapsed_time / self.config.duration_seconds) * 100)
            
            # Prepare progress data
            progress_data = {
                'progress_percent': self.current_progress,
                'elapsed_time': self.elapsed_time,
                'active_users': self.active_users,
                'completed_requests': self.completed_requests,
                'failed_requests': self.failed_requests,
                'success_rate': (self.completed_requests / (self.completed_requests + self.failed_requests) * 100) if (self.completed_requests + self.failed_requests) > 0 else 0,
                'current_rps': self.current_rps,
                'peak_rps': self.peak_rps,
                'estimated_completion': self.config.duration_seconds - self.elapsed_time if self.elapsed_time < self.config.duration_seconds else 0
            }
            
            # Call progress callback
            await self.progress_callback(progress_data)
    
    async def _execute_load_test(self):
        """Eksekusi load test dengan thread groups."""
        # Buat thread groups berdasarkan konfigurasi
        thread_groups = self._create_thread_groups()
        
        # Start progress monitoring task
        progress_task = None
        if self.progress_callback:
            progress_task = asyncio.create_task(self._progress_monitor())
        
        # Jalankan semua thread groups secara bersamaan
        tasks = []
        for group_id, group_config in enumerate(thread_groups):
            task = asyncio.create_task(
                self._execute_thread_group(group_id, group_config)
            )
            tasks.append(task)
        
        # Tunggu semua thread groups selesai
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Stop progress monitoring
        if progress_task:
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass
    
    async def _progress_monitor(self):
        """Monitor progress dan update callback secara berkala."""
        while self.start_time and (time.time() - self.start_time) < self.config.duration_seconds:
            await self._update_progress()
            await asyncio.sleep(1.0)  # Update setiap 1 detik
    
    def _create_thread_groups(self) -> List[Dict[str, Any]]:
        """Buat thread groups berdasarkan konfigurasi."""
        if self.config.thread_groups:
            return self.config.thread_groups
        
        # Default thread group
        return [{
            "name": "Default Thread Group",
            "virtual_users": self.config.virtual_users,
            "ramp_up_seconds": self.config.ramp_up_seconds,
            "duration_seconds": self.config.duration_seconds,
            "ramp_down_seconds": self.config.ramp_down_seconds,
            "think_time_seconds": self.config.think_time_seconds,
            "scenario": "default"
        }]
    
    async def _execute_thread_group(self, group_id: int, group_config: Dict[str, Any]):
        """Eksekusi satu thread group."""
        group_name = group_config.get("name", f"Thread Group {group_id}")
        virtual_users = group_config.get("virtual_users", self.config.virtual_users)
        ramp_up = group_config.get("ramp_up_seconds", self.config.ramp_up_seconds)
        duration = group_config.get("duration_seconds", self.config.duration_seconds)
        ramp_down = group_config.get("ramp_down_seconds", self.config.ramp_down_seconds)
        think_time = group_config.get("think_time_seconds", self.config.think_time_seconds)
        
        logger.info(f"🎭 Executing {group_name}: {virtual_users} VU, {duration}s duration")
        
        # Buat semaphore untuk membatasi concurrent users
        semaphore = asyncio.Semaphore(min(virtual_users, self.config.max_concurrent_browsers))
        
        # Buat tasks untuk semua virtual users
        tasks = []
        for user_id in range(virtual_users):
            task = asyncio.create_task(
                self._simulate_virtual_user(
                    group_id, user_id, semaphore, ramp_up, duration, ramp_down, think_time
                )
            )
            tasks.append(task)
        
        # Jalankan semua virtual users
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _simulate_virtual_user(self, group_id: int, user_id: int, semaphore: asyncio.Semaphore, 
                                   ramp_up: int, duration: int, ramp_down: int, think_time: float):
        """Simulasi satu virtual user."""
        async with semaphore:
            self.active_users += 1
            request_id = 0
            
            try:
                # Ramp up period
                if ramp_up > 0:
                    ramp_delay = (user_id / self.config.virtual_users) * ramp_up
                    await asyncio.sleep(ramp_delay)
                
                # Main execution period
                main_start = time.time()
                while (time.time() - main_start) < duration:
                    # Jalankan request
                    result = await self._execute_request(group_id, user_id, request_id)
                    self.results.append(result)
                    
                    # Update counters
                    if result['success']:
                        self.completed_requests += 1
                    else:
                        self.failed_requests += 1
                    
                    # Think time
                    if think_time > 0:
                        await asyncio.sleep(think_time)
                    
                    # CPU break untuk efisiensi
                    await asyncio.sleep(0.01)
                    
                    request_id += 1
                
                # Ramp down period
                if ramp_down > 0:
                    await asyncio.sleep(ramp_down)
                    
            finally:
                self.active_users -= 1
    
    async def _execute_request(self, group_id: int, user_id: int, request_id: int) -> Dict[str, Any]:
        """Eksekusi satu request dengan optimasi resource."""
        start_time = time.time()
        success = False
        error_message = None
        response_time = 0.0
        status_code = None
        
        try:
            async with async_playwright() as p:
                # Launch browser dengan optimasi resource
                browser = await p.chromium.launch(
                    headless=self.config.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-images',
                        '--disable-javascript',
                        '--memory-pressure-off',
                        f'--max_old_space_size={self.config.browser_memory_limit_mb}'
                    ]
                )
                
                context = await browser.new_context(
                    viewport={'width': 800, 'height': 600},
                    java_script_enabled=False,
                    device_scale_factor=1
                )
                
                page = await context.new_page()
                page.set_default_timeout(self.config.timeout_seconds * 1000)
                
                # Navigate ke target URL
                response = await page.goto(
                    self.config.target_url,
                    wait_until="domcontentloaded",
                    timeout=self.config.timeout_seconds * 1000
                )
                
                if response:
                    status_code = response.status
                
                response_time = time.time() - start_time
                success = True
                
                # Cleanup
                await page.close()
                await context.close()
                await browser.close()
                
        except Exception as e:
            error_message = str(e)
            logger.warning(f"Request failed: {error_message}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'group_id': group_id,
            'user_id': user_id,
            'request_id': request_id,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'success': success,
            'error_message': error_message,
            'response_time': response_time,
            'status_code': status_code
        }
    
    def _calculate_results(self) -> LoadTestResult:
        """Hitung hasil load test."""
        if not self.results:
            return self._create_empty_result()
        
        # Basic metrics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Response time metrics
        response_times = [r['response_time'] for r in self.results if r['success'] and r['response_time'] > 0]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p50_response_time = self._percentile(response_times, 50)
            p90_response_time = self._percentile(response_times, 90)
            p95_response_time = self._percentile(response_times, 95)
            p99_response_time = self._percentile(response_times, 99)
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p50_response_time = p90_response_time = p95_response_time = p99_response_time = 0.0
        
        # Throughput metrics
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        requests_per_second = total_requests / total_duration if total_duration > 0 else 0
        
        # Calculate peak RPS (requests per second in 1-second windows)
        peak_rps = self._calculate_peak_rps()
        
        # Error analysis
        errors = self._analyze_errors()
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Resource usage
        peak_cpu = self.resource_monitor.peak_cpu_usage if self.resource_monitor else 0.0
        peak_memory = self.resource_monitor.peak_memory_usage if self.resource_monitor else 0.0
        avg_cpu = self.resource_monitor.average_cpu_usage if self.resource_monitor else 0.0
        avg_memory = self.resource_monitor.average_memory_usage if self.resource_monitor else 0.0
        
        return LoadTestResult(
            test_id=f"load_test_{int(self.start_time)}",
            start_time=self.start_time or 0,
            end_time=self.end_time or 0,
            duration=total_duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p50_response_time=p50_response_time,
            p90_response_time=p90_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            peak_rps=peak_rps,
            average_rps=requests_per_second,
            errors=errors,
            error_rate=error_rate,
            peak_cpu_usage=peak_cpu,
            peak_memory_usage=peak_memory,
            average_cpu_usage=avg_cpu,
            average_memory_usage=avg_memory,
            load_generator_scale=self.system_specs.scale,
            system_specs=self.system_specs
        )
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Hitung percentile dari data."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _calculate_peak_rps(self) -> float:
        """Hitung peak RPS dalam 1-second windows."""
        if not self.results:
            return 0.0
        
        # Group results by 1-second windows
        windows = {}
        for result in self.results:
            window = int(result['start_time'])
            if window not in windows:
                windows[window] = 0
            windows[window] += 1
        
        return max(windows.values()) if windows else 0.0
    
    def _analyze_errors(self) -> Dict[str, int]:
        """Analisis error types."""
        errors = {}
        for result in self.results:
            if not result['success'] and result['error_message']:
                error_type = self._categorize_error(result['error_message'])
                errors[error_type] = errors.get(error_type, 0) + 1
        return errors
    
    def _categorize_error(self, error_message: str) -> str:
        """Kategorikan error berdasarkan pesan."""
        error_lower = error_message.lower()
        
        if "timeout" in error_lower:
            return "Timeout"
        elif "network" in error_lower or "connection" in error_lower:
            return "Network Error"
        elif "404" in error_message or "not found" in error_lower:
            return "404 Not Found"
        elif "500" in error_message or "server error" in error_lower:
            return "Server Error"
        elif "javascript" in error_lower or "script" in error_lower:
            return "JavaScript Error"
        else:
            return "Other Error"
    
    def _create_empty_result(self) -> LoadTestResult:
        """Buat hasil kosong jika tidak ada data."""
        return LoadTestResult(
            test_id="empty_test",
            start_time=0,
            end_time=0,
            duration=0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            success_rate=0.0,
            avg_response_time=0.0,
            min_response_time=0.0,
            max_response_time=0.0,
            p50_response_time=0.0,
            p90_response_time=0.0,
            p95_response_time=0.0,
            p99_response_time=0.0,
            requests_per_second=0.0,
            peak_rps=0.0,
            average_rps=0.0,
            errors={},
            error_rate=0.0,
            peak_cpu_usage=0.0,
            peak_memory_usage=0.0,
            average_cpu_usage=0.0,
            average_memory_usage=0.0,
            load_generator_scale=self.system_specs.scale,
            system_specs=self.system_specs
        )

class ResourceMonitor:
    """Monitor resource usage selama load test."""
    
    def __init__(self):
        self.monitoring = False
        self.cpu_samples = []
        self.memory_samples = []
        self.monitor_task = None
    
    async def start_monitoring(self):
        """Mulai monitoring resource."""
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_resources())
    
    async def stop_monitoring(self):
        """Stop monitoring resource."""
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_resources(self):
        """Monitor CPU dan memory usage."""
        while self.monitoring:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            self.cpu_samples.append(cpu_percent)
            self.memory_samples.append(memory_percent)
            
            await asyncio.sleep(1.0)
    
    @property
    def peak_cpu_usage(self) -> float:
        """Peak CPU usage."""
        return max(self.cpu_samples) if self.cpu_samples else 0.0
    
    @property
    def peak_memory_usage(self) -> float:
        """Peak memory usage."""
        return max(self.memory_samples) if self.memory_samples else 0.0
    
    @property
    def average_cpu_usage(self) -> float:
        """Average CPU usage."""
        return statistics.mean(self.cpu_samples) if self.cpu_samples else 0.0
    
    @property
    def average_memory_usage(self) -> float:
        """Average memory usage."""
        return statistics.mean(self.memory_samples) if self.memory_samples else 0.0

def create_load_generator_config(
    target_url: str,
    virtual_users: int = 10,
    duration_seconds: int = 60,
    ramp_up_seconds: int = 10,
    ramp_down_seconds: int = 10,
    think_time_seconds: float = 1.0,
    timeout_seconds: int = 30,
    headless: bool = True,
    scenario_name: str = "Default Scenario",
    test_plan_name: str = "Load Test Plan"
) -> LoadGeneratorConfig:
    """
    Factory function untuk membuat konfigurasi load generator.
    
    Args:
        target_url: URL target untuk load test
        virtual_users: Jumlah virtual users
        duration_seconds: Durasi test dalam detik
        ramp_up_seconds: Waktu ramp up dalam detik
        ramp_down_seconds: Waktu ramp down dalam detik
        think_time_seconds: Think time antar request
        timeout_seconds: Timeout per request
        headless: Mode headless browser
        scenario_name: Nama scenario
        test_plan_name: Nama test plan
        
    Returns:
        LoadGeneratorConfig: Konfigurasi load generator
    """
    return LoadGeneratorConfig(
        target_url=target_url,
        virtual_users=virtual_users,
        duration_seconds=duration_seconds,
        ramp_up_seconds=ramp_up_seconds,
        ramp_down_seconds=ramp_down_seconds,
        think_time_seconds=think_time_seconds,
        timeout_seconds=timeout_seconds,
        headless=headless,
        scenario_name=scenario_name,
        test_plan_name=test_plan_name
    )

async def run_load_test(config: LoadGeneratorConfig) -> LoadTestResult:
    """
    Fungsi helper untuk menjalankan load test.
    
    Args:
        config: Konfigurasi load generator
        
    Returns:
        LoadTestResult: Hasil load test
    """
    generator = AdvancedLoadGenerator(config)
    return await generator.run_load_test()
