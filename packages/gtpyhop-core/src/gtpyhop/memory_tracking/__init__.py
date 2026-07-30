"""Memory tracking using battle-tested psutil library."""

from typing import Dict

try:
    import psutil
    MEMORY_TRACKING_AVAILABLE = True
except ImportError:
    MEMORY_TRACKING_AVAILABLE = False

if MEMORY_TRACKING_AVAILABLE:
    from .tracker import MemoryTracker
    from .monitor import MemoryMonitor
else:
    # Graceful fallback to placeholder when psutil is not available
    class MemoryTracker:
        """Placeholder MemoryTracker when psutil is unavailable."""
        def start_session_tracking(self, session_id: str) -> bool:
            return False
        def get_session_memory(self, session_id: str) -> Dict[str, float]:
            return {'memory_mb': 0.0, 'peak_memory_mb': 0.0}
        def stop_session_tracking(self, session_id: str) -> Dict[str, float]:
            return {'memory_mb': 0.0, 'peak_memory_mb': 0.0}

    MemoryMonitor = None

__all__ = ['MemoryTracker', 'MemoryMonitor', 'MEMORY_TRACKING_AVAILABLE']