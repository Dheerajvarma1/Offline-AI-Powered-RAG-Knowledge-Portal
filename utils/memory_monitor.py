"""Memory monitoring utilities for 8GB RAM optimization."""
import psutil
import os
import gc
from typing import Optional


class MemoryMonitor:
    """Monitor and manage system memory usage."""
    
    def __init__(self, max_memory_mb: int = 6000):
        self.max_memory_mb = max_memory_mb
        self.process = psutil.Process(os.getpid())
    
    def get_memory_usage(self) -> dict:
        """Get current memory usage statistics."""
        system_memory = psutil.virtual_memory()
        process_memory = self.process.memory_info()
        
        return {
            'system_total_gb': system_memory.total / (1024 ** 3),
            'system_available_gb': system_memory.available / (1024 ** 3),
            'system_used_percent': system_memory.percent,
            'process_memory_mb': process_memory.rss / (1024 ** 2),
            'process_memory_percent': self.process.memory_percent()
        }
    
    def check_memory_available(self) -> bool:
        """Check if enough memory is available."""
        usage = self.get_memory_usage()
        available_mb = usage['system_available_gb'] * 1024
        return available_mb > (self.max_memory_mb * 0.1)  # Keep 10% buffer
    
    def force_gc(self):
        """Force garbage collection to free memory."""
        gc.collect()
    
    def get_memory_status(self) -> str:
        """Get human-readable memory status."""
        usage = self.get_memory_usage()
        return (
            f"System: {usage['system_used_percent']:.1f}% used "
            f"({usage['system_available_gb']:.2f} GB available) | "
            f"Process: {usage['process_memory_mb']:.1f} MB"
        )



