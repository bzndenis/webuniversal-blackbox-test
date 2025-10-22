"""
Real-time progress monitoring untuk Load Generator.
Menyediakan real-time updates dan charts selama load test berjalan.
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

# Import streamlit untuk UI updates
try:
    import streamlit as st
except ImportError:
    st = None

class ProgressMonitor:
    """Monitor progress real-time untuk load test."""
    
    def __init__(self):
        self.progress_data: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
    async def start_monitoring(self, generator, update_callback: Optional[Callable] = None):
        """Mulai monitoring progress."""
        self.start_time = time.time()
        self.is_monitoring = True
        self.update_callback = update_callback
        
        # Start monitoring task
        self.monitor_task = asyncio.create_task(self._monitor_loop(generator))
        
    async def stop_monitoring(self):
        """Stop monitoring progress."""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await asyncio.wait_for(self.monitor_task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
    
    async def _monitor_loop(self, generator):
        """Loop monitoring progress."""
        while self.is_monitoring:
            try:
                # Get current progress data
                current_time = time.time()
                elapsed_time = current_time - self.start_time if self.start_time else 0
                
                # Calculate progress percentage
                progress_percent = 0.0
                if generator.config.duration_seconds > 0:
                    progress_percent = min(100.0, (elapsed_time / generator.config.duration_seconds) * 100)
                
                # Stop monitoring if test is complete
                if progress_percent >= 100.0 or elapsed_time >= generator.config.duration_seconds:
                    self.is_monitoring = False
                    break
                
                # Additional safety: stop if test has been running too long
                if elapsed_time > generator.config.duration_seconds + 5:  # 5 seconds buffer
                    self.is_monitoring = False
                    break
                
                # Get current metrics
                current_rps = generator.completed_requests / elapsed_time if elapsed_time > 0 else 0
                success_rate = (generator.completed_requests / (generator.completed_requests + generator.failed_requests) * 100) if (generator.completed_requests + generator.failed_requests) > 0 else 0
                
                # Create progress data
                progress_data = {
                    'timestamp': current_time,
                    'elapsed_time': elapsed_time,
                    'progress_percent': progress_percent,
                    'active_users': generator.active_users,
                    'completed_requests': generator.completed_requests,
                    'failed_requests': generator.failed_requests,
                    'success_rate': success_rate,
                    'current_rps': current_rps,
                    'peak_rps': generator.peak_rps,
                    'estimated_completion': generator.config.duration_seconds - elapsed_time if elapsed_time < generator.config.duration_seconds else 0
                }
                
                # Add to history
                self.progress_data.append(progress_data)
                
                # Call update callback if provided
                if self.update_callback:
                    await self.update_callback(progress_data)
                
                # Update every second
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in progress monitoring: {e}")
                await asyncio.sleep(1.0)
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """Get latest progress data."""
        return self.progress_data[-1] if self.progress_data else None
    
    def get_progress_history(self) -> List[Dict[str, Any]]:
        """Get all progress data history."""
        return self.progress_data
    
    def get_chart_data(self) -> List[Dict[str, Any]]:
        """Get data formatted for charts."""
        chart_data = []
        for i, data in enumerate(self.progress_data):
            chart_data.append({
                'Time (s)': i,
                'RPS': data['current_rps'],
                'Success Rate (%)': data['success_rate'],
                'Active Users': data['active_users'],
                'Progress (%)': data['progress_percent']
            })
        return chart_data
    
    def get_detailed_chart_data(self) -> List[Dict[str, Any]]:
        """Get detailed chart data with more metrics."""
        chart_data = []
        for i, data in enumerate(self.progress_data):
            chart_data.append({
                'Time (s)': i,
                'RPS': data['current_rps'],
                'Success Rate (%)': data['success_rate'],
                'Active Users': data['active_users'],
                'Progress (%)': data['progress_percent'],
                'Completed Requests': data['completed_requests'],
                'Failed Requests': data['failed_requests'],
                'Peak RPS': data['peak_rps'],
                'Elapsed Time': data['elapsed_time']
            })
        return chart_data
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from progress data."""
        if not self.progress_data:
            return {}
        
        latest = self.progress_data[-1]
        max_rps = max(data['current_rps'] for data in self.progress_data)
        avg_rps = sum(data['current_rps'] for data in self.progress_data) / len(self.progress_data)
        min_success_rate = min(data['success_rate'] for data in self.progress_data)
        max_active_users = max(data['active_users'] for data in self.progress_data)
        
        return {
            'total_duration': latest['elapsed_time'],
            'final_progress': latest['progress_percent'],
            'max_rps': max_rps,
            'avg_rps': avg_rps,
            'min_success_rate': min_success_rate,
            'max_active_users': max_active_users,
            'total_requests': latest['completed_requests'] + latest['failed_requests'],
            'successful_requests': latest['completed_requests'],
            'failed_requests': latest['failed_requests']
        }

class StreamlitProgressUpdater:
    """Streamlit-specific progress updater."""
    
    def __init__(self, progress_bar, status_text, metrics_container):
        self.progress_bar = progress_bar
        self.status_text = status_text
        self.metrics_container = metrics_container
        self.chart_data = []
        self.last_update_time = 0
        
    async def update_progress(self, data: Dict[str, Any]):
        """Update Streamlit UI dengan progress data."""
        try:
            # Throttle updates to avoid overwhelming Streamlit
            current_time = time.time()
            if current_time - self.last_update_time < 0.5:  # Update max every 0.5 seconds
                return
            self.last_update_time = current_time
            
            # Update progress bar
            progress_value = min(1.0, max(0.0, data['progress_percent'] / 100))
            self.progress_bar.progress(progress_value)
            
            # Update status text with more detailed info
            status_msg = f"🔄 Running... {data['progress_percent']:.1f}% | "
            status_msg += f"Active: {data['active_users']} | "
            status_msg += f"RPS: {data['current_rps']:.1f} | "
            status_msg += f"Success: {data['success_rate']:.1f}% | "
            status_msg += f"Completed: {data['completed_requests']:,}"
            self.status_text.text(status_msg)
            
            # Store chart data for later visualization (no UI updates here)
            self.chart_data.append({
                'Time (s)': len(self.chart_data),
                'RPS': data['current_rps'],
                'Success Rate (%)': data['success_rate'],
                'Active Users': data['active_users'],
                'Progress (%)': data['progress_percent'],
                'Completed Requests': data['completed_requests']
            })
            
        except Exception as e:
            logger.error(f"Error updating Streamlit progress: {e}")
            # Fallback to simple text update
            try:
                self.status_text.text(f"🔄 Running... {data.get('progress_percent', 0):.1f}%")
            except:
                pass

def create_progress_monitor() -> ProgressMonitor:
    """Factory function untuk membuat progress monitor."""
    return ProgressMonitor()

def create_streamlit_updater(progress_bar, status_text, metrics_container) -> StreamlitProgressUpdater:
    """Factory function untuk membuat Streamlit updater."""
    return StreamlitProgressUpdater(progress_bar, status_text, metrics_container)
