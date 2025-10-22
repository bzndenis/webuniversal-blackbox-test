"""
Service untuk melakukan stress testing pada web application.
Mengukur performa dan stabilitas aplikasi di bawah beban tinggi.
"""

import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import logging

logger = logging.getLogger(__name__)

@dataclass
class StressTestConfig:
    """Konfigurasi untuk stress test."""
    url: str
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10
    think_time_seconds: float = 1.0
    timeout_seconds: int = 30
    headless: bool = True
    actions: List[Dict[str, Any]] = None  # Aksi yang akan dilakukan berulang

@dataclass
class StressTestResult:
    """Hasil dari satu request dalam stress test."""
    user_id: int
    request_id: int
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_message: Optional[str] = None
    response_time: float = 0.0
    status_code: Optional[int] = None

@dataclass
class StressTestSummary:
    """Ringkasan hasil stress test."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    total_duration: float
    errors: Dict[str, int]  # Jenis error dan jumlahnya

class StressTester:
    """Kelas utama untuk menjalankan stress test."""
    
    def __init__(self, config: StressTestConfig):
        self.config = config
        self.results: List[StressTestResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
    async def run_stress_test(self) -> StressTestSummary:
        """
        Menjalankan stress test dengan konfigurasi yang diberikan.
        
        Returns:
            StressTestSummary: Ringkasan hasil stress test
        """
        logger.info(f"Memulai stress test untuk {self.config.url}")
        logger.info(f"Concurrent users: {self.config.concurrent_users}")
        logger.info(f"Duration: {self.config.duration_seconds} seconds")
        
        self.start_time = time.time()
        
        # Buat semaphore untuk membatasi concurrent users
        semaphore = asyncio.Semaphore(self.config.concurrent_users)
        
        # Buat tasks untuk semua users
        tasks = []
        for user_id in range(self.config.concurrent_users):
            task = asyncio.create_task(
                self._simulate_user(user_id, semaphore)
            )
            tasks.append(task)
        
        # Tunggu semua tasks selesai atau timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.duration_seconds
            )
        except asyncio.TimeoutError:
            logger.info("Stress test timeout tercapai")
        
        # Cancel semua tasks yang masih berjalan
        for task in tasks:
            if not task.done():
                task.cancel()
        
        self.end_time = time.time()
        
        return self._calculate_summary()
    
    async def _simulate_user(self, user_id: int, semaphore: asyncio.Semaphore):
        """Simulasi satu user yang melakukan request berulang."""
        async with semaphore:
            request_id = 0
            
            while True:
                # Cek apakah sudah melewati durasi test
                if self.start_time and (time.time() - self.start_time) > self.config.duration_seconds:
                    break
                
                # Ramp up period - tunggu sebelum mulai
                if request_id == 0:
                    ramp_up_delay = (user_id / self.config.concurrent_users) * self.config.ramp_up_seconds
                    await asyncio.sleep(ramp_up_delay)
                
                # Jalankan request
                result = await self._execute_request(user_id, request_id)
                self.results.append(result)
                
                # Think time - simulasi user berpikir sebelum request berikutnya
                if self.config.think_time_seconds > 0:
                    await asyncio.sleep(self.config.think_time_seconds)
                
                # Optimasi: Beri jeda untuk mengurangi beban CPU
                await asyncio.sleep(0.01)  # 10ms delay untuk mengurangi CPU usage
                
                request_id += 1
    
    async def _execute_request(self, user_id: int, request_id: int) -> StressTestResult:
        """Eksekusi satu request dengan optimasi resource."""
        start_time = time.time()
        success = False
        error_message = None
        response_time = 0.0
        status_code = None
        
        try:
            async with async_playwright() as p:
                # Optimasi browser launch dengan resource limits
                browser = await p.chromium.launch(
                    headless=self.config.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-images',  # Disable images untuk menghemat RAM
                        '--disable-javascript',  # Disable JS jika tidak diperlukan
                        '--memory-pressure-off',
                        '--max_old_space_size=128'  # Limit memory usage
                    ]
                )
                
                # Optimasi context dengan resource limits
                context = await browser.new_context(
                    viewport={'width': 800, 'height': 600},  # Smaller viewport
                    device_scale_factor=1,
                    has_touch=False,
                    is_mobile=False,
                    java_script_enabled=False,  # Disable JS untuk menghemat CPU
                    bypass_csp=True
                )
                
                page = await context.new_page()
                
                # Set timeout yang lebih pendek untuk efisiensi
                page.set_default_timeout(min(self.config.timeout_seconds * 1000, 10000))
                
                # Navigate ke URL dengan wait strategy yang lebih efisien
                response = await page.goto(
                    self.config.url,
                    wait_until="domcontentloaded",  # Lebih cepat dari "load"
                    timeout=min(self.config.timeout_seconds * 1000, 10000)
                )
                
                if response:
                    status_code = response.status
                
                # Jalankan aksi tambahan jika ada (dengan optimasi)
                if self.config.actions:
                    await self._execute_actions_optimized(page)
                
                # Ambil response time
                response_time = time.time() - start_time
                success = True
                
                # Cleanup yang lebih agresif
                await page.close()
                await context.close()
                await browser.close()
                
        except Exception as e:
            error_message = str(e)
            logger.warning(f"Request gagal untuk user {user_id}, request {request_id}: {error_message}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        return StressTestResult(
            user_id=user_id,
            request_id=request_id,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success=success,
            error_message=error_message,
            response_time=response_time,
            status_code=status_code
        )
    
    async def _execute_actions_optimized(self, page: Page):
        """Jalankan aksi tambahan dengan optimasi resource."""
        for action in self.config.actions:
            try:
                action_type = action.get("type")
                
                if action_type == "click":
                    selector = action.get("selector")
                    if selector:
                        await page.click(selector, timeout=2000)  # Shorter timeout
                
                elif action_type == "fill":
                    selector = action.get("selector")
                    value = action.get("value", "")
                    if selector:
                        await page.fill(selector, value, timeout=2000)  # Shorter timeout
                
                elif action_type == "wait":
                    seconds = min(action.get("seconds", 1), 2)  # Max 2 seconds
                    await asyncio.sleep(seconds)
                
                elif action_type == "screenshot":
                    # Skip screenshot untuk menghemat resource
                    pass
                
                # Think time yang lebih pendek
                if self.config.think_time_seconds > 0:
                    await asyncio.sleep(min(self.config.think_time_seconds, 0.5))
                    
            except Exception as e:
                logger.warning(f"Gagal menjalankan aksi {action}: {e}")
    
    async def _execute_actions(self, page: Page):
        """Jalankan aksi tambahan pada halaman (legacy method)."""
        await self._execute_actions_optimized(page)
    
    def _calculate_summary(self) -> StressTestSummary:
        """Hitung ringkasan hasil stress test."""
        if not self.results:
            return StressTestSummary(
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                success_rate=0.0,
                avg_response_time=0.0,
                min_response_time=0.0,
                max_response_time=0.0,
                p95_response_time=0.0,
                p99_response_time=0.0,
                requests_per_second=0.0,
                total_duration=0.0,
                errors={}
            )
        
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        total_requests = len(self.results)
        successful_requests = len(successful_results)
        failed_requests = len(failed_results)
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        # Hitung response time metrics
        response_times = [r.response_time for r in successful_results if r.response_time > 0]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = self._percentile(response_times, 95)
            p99_response_time = self._percentile(response_times, 99)
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
            p95_response_time = p99_response_time = 0.0
        
        # Hitung requests per second
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        requests_per_second = total_requests / total_duration if total_duration > 0 else 0
        
        # Hitung error types
        errors = {}
        for result in failed_results:
            if result.error_message:
                error_type = self._categorize_error(result.error_message)
                errors[error_type] = errors.get(error_type, 0) + 1
        
        return StressTestSummary(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            total_duration=total_duration,
            errors=errors
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

def create_stress_test_config(
    url: str,
    concurrent_users: int = 10,
    duration_seconds: int = 60,
    ramp_up_seconds: int = 10,
    think_time_seconds: float = 1.0,
    timeout_seconds: int = 30,
    headless: bool = True,
    actions: Optional[List[Dict[str, Any]]] = None
) -> StressTestConfig:
    """
    Factory function untuk membuat konfigurasi stress test.
    
    Args:
        url: URL yang akan di-test
        concurrent_users: Jumlah user bersamaan
        duration_seconds: Durasi test dalam detik
        ramp_up_seconds: Waktu untuk mencapai full load
        think_time_seconds: Waktu tunggu antara request
        timeout_seconds: Timeout per request
        headless: Mode headless browser
        actions: Daftar aksi tambahan
        
    Returns:
        StressTestConfig: Konfigurasi stress test
    """
    return StressTestConfig(
        url=url,
        concurrent_users=concurrent_users,
        duration_seconds=duration_seconds,
        ramp_up_seconds=ramp_up_seconds,
        think_time_seconds=think_time_seconds,
        timeout_seconds=timeout_seconds,
        headless=headless,
        actions=actions or []
    )

async def run_stress_test(config: StressTestConfig) -> StressTestSummary:
    """
    Fungsi helper untuk menjalankan stress test.
    
    Args:
        config: Konfigurasi stress test
        
    Returns:
        StressTestSummary: Hasil stress test
    """
    tester = StressTester(config)
    return await tester.run_stress_test()
