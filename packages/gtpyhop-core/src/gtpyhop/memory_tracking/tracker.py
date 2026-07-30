"""
Memory Tracker - Point-in-time memory measurement using psutil.

This module provides session-based memory tracking by measuring the process's
Resident Set Size (RSS) at specific points in time. It tracks the memory
delta from when a session starts to when it's queried or stopped.

Key Concepts:
-------------
1. RSS (Resident Set Size): The portion of a process's memory that is held
   in RAM. This is what psutil.Process().memory_info().rss returns.

2. Baseline: The memory usage when tracking starts. All measurements are
   relative to this baseline to isolate the session's memory impact.

3. Session Isolation: Each planning session has its own baseline, allowing
   multiple concurrent sessions to be tracked independently.

Limitations:
------------
- Point-in-time measurement: Only captures memory at the moment of query,
  not continuous monitoring. Memory spikes between queries are missed.
- For accurate peak detection, use MemoryMonitor (background thread sampling).

Usage:
------
    tracker = MemoryTracker()
    tracker.start_session_tracking("session_1")

    # ... do memory-intensive work ...

    stats = tracker.get_session_memory("session_1")
    print(f"Current memory: {stats['memory_mb']:.2f} MB")

    final_stats = tracker.stop_session_tracking("session_1")

Thread Safety:
--------------
All methods are thread-safe using a reentrant lock (RLock), allowing
the same thread to acquire the lock multiple times without deadlock.

-- Part of GTPyhop Memory Tracking module
"""

import psutil
import threading
from typing import Dict


class MemoryTracker:
    """
    Memory tracking using psutil for actual measurement.

    This class provides point-in-time memory measurements for planning sessions.
    It tracks memory usage relative to a baseline established when tracking starts.

    Attributes:
        process: psutil.Process instance for the current process
        session_baselines: Maps session_id -> baseline memory (MB) at start
        session_peaks: Maps session_id -> highest observed memory (MB)
        _lock: Thread-safe lock for concurrent access
    """

    def __init__(self):
        """
        Initialize the memory tracker.

        Creates a psutil.Process() instance for the current process.
        This is reused for all memory queries to avoid overhead.
        """
        # Get a handle to the current process for memory queries
        # psutil.Process() with no argument gets the current process
        self.process = psutil.Process()

        # Dictionary mapping session_id -> baseline memory in MB
        # The baseline is the memory usage when tracking started
        self.session_baselines: Dict[str, float] = {}

        # Dictionary mapping session_id -> peak memory in MB
        # Updated each time get_session_memory() is called
        self.session_peaks: Dict[str, float] = {}

        # Reentrant lock for thread safety
        # RLock allows the same thread to acquire multiple times
        self._lock = threading.RLock()

    def start_session_tracking(self, session_id: str) -> bool:
        """
        Start tracking memory for a session.

        Records the current memory as the baseline for this session.
        All subsequent measurements will be relative to this baseline.

        Args:
            session_id: Unique identifier for the planning session

        Returns:
            True if tracking started successfully
            False if session is already being tracked

        Example:
            >>> tracker.start_session_tracking("my_session")
            True
            >>> tracker.start_session_tracking("my_session")  # Already tracking
            False
        """
        with self._lock:
            # Prevent duplicate tracking for the same session
            if session_id in self.session_baselines:
                return False  # Already tracking

            # Get current RSS (Resident Set Size) in megabytes
            # memory_info().rss returns bytes, so divide by 1024^2 for MB
            current_memory = self.process.memory_info().rss / 1024 / 1024  # MB

            # Store baseline - all future measurements are relative to this
            self.session_baselines[session_id] = current_memory

            # Initialize peak to baseline (will be updated as memory grows)
            self.session_peaks[session_id] = current_memory

            return True

    def get_session_memory(self, session_id: str) -> Dict[str, float]:
        """
        Get current memory usage for a session.

        Measures current RSS and calculates:
        - memory_mb: Current memory relative to session baseline
        - peak_memory_mb: Highest memory observed since tracking started

        Args:
            session_id: Unique identifier for the planning session

        Returns:
            Dictionary with:
            - 'memory_mb': Current memory usage relative to baseline
            - 'peak_memory_mb': Peak memory observed (updated on each call)

        Note:
            This method updates the peak if current memory exceeds it.
            However, since this is point-in-time measurement, spikes
            between calls may be missed. Use MemoryMonitor for accurate peaks.
        """
        with self._lock:
            # Return zeros for unknown sessions
            if session_id not in self.session_baselines:
                return {'memory_mb': 0.0, 'peak_memory_mb': 0.0}

            try:
                # Get current memory in MB
                current_memory = self.process.memory_info().rss / 1024 / 1024
                baseline = self.session_baselines[session_id]

                # Calculate memory delta from baseline
                # Use max(0, ...) to handle edge case where memory decreased
                session_memory = max(0, current_memory - baseline)

                # Update peak if current exceeds previous peak
                # Peak is stored as absolute value, convert to relative for return
                peak_memory = max(self.session_peaks[session_id] - baseline, session_memory)
                self.session_peaks[session_id] = peak_memory + baseline

                return {
                    'memory_mb': session_memory,
                    'peak_memory_mb': peak_memory
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Handle edge cases:
                # - NoSuchProcess: Process terminated (shouldn't happen for self)
                # - AccessDenied: Permission issues on some systems
                return {'memory_mb': 0.0, 'peak_memory_mb': 0.0}

    def stop_session_tracking(self, session_id: str) -> Dict[str, float]:
        """
        Stop tracking and return final stats.

        Gets the final memory statistics and cleans up tracking data
        for the session. After this call, the session_id can be reused.

        Args:
            session_id: Unique identifier for the planning session

        Returns:
            Final memory statistics (same format as get_session_memory)

        Example:
            >>> stats = tracker.stop_session_tracking("my_session")
            >>> print(f"Final memory: {stats['memory_mb']:.2f} MB")
            >>> print(f"Peak memory: {stats['peak_memory_mb']:.2f} MB")
        """
        # Get final stats before cleanup
        final_stats = self.get_session_memory(session_id)

        with self._lock:
            # Remove session data to free memory and allow reuse of session_id
            # dict.pop(key, None) returns None if key doesn't exist (no error)
            self.session_baselines.pop(session_id, None)
            self.session_peaks.pop(session_id, None)

        return final_stats
