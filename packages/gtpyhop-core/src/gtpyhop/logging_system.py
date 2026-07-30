"""
Structured logging system for GTPyhop 1.3
Replaces stdout printing with configurable structured logging
"""

import time
import threading
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Union
from enum import Enum
from contextlib import contextmanager
import sys
import io

class LogLevel(Enum):
    """Logging levels with numeric values for filtering."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

@dataclass
class LogEntry:
    """Structured log entry with timestamp and context."""
    timestamp: float
    level: LogLevel
    component: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    thread_id: Optional[int] = None

    def __post_init__(self):
        if self.thread_id is None:
            self.thread_id = threading.get_ident()

class LogHandler:
    """Base class for log output handlers."""

    def handle(self, entry: LogEntry) -> None:
        raise NotImplementedError

class StdoutLogHandler(LogHandler):
    """Handler that outputs to stdout (backward compatibility)."""

    def __init__(self, format_string: str = "{component}> {message}"):
        self.format_string = format_string

    def handle(self, entry: LogEntry) -> None:
        formatted = self.format_string.format(
            timestamp=entry.timestamp,
            level=entry.level.name,
            component=entry.component,
            message=entry.message,
            **entry.context
        )
        print(formatted)

class StructuredLogHandler(LogHandler):
    """Handler that collects structured log entries."""

    def __init__(self):
        self.entries: List[LogEntry] = []
        self._lock = threading.Lock()

    def handle(self, entry: LogEntry) -> None:
        with self._lock:
            self.entries.append(entry)

    def get_entries(self, min_level: LogLevel = LogLevel.DEBUG) -> List[LogEntry]:
        with self._lock:
            return [e for e in self.entries if e.level.value >= min_level.value]

    def clear(self) -> None:
        with self._lock:
            self.entries.clear()

    def to_dict_list(self, min_level: LogLevel = LogLevel.INFO) -> List[Dict[str, Any]]:
        """Convert entries to dictionary format for serialization."""
        return [
            {
                "timestamp": entry.timestamp,
                "level": entry.level.name,
                "component": entry.component,
                "message": entry.message,
                "context": entry.context,
                "thread_id": entry.thread_id
            }
            for entry in self.get_entries(min_level)
        ]

class StructuredLogger:
    """Main structured logging interface."""

    def __init__(self, session_id: str, base_time: Optional[float] = None):
        self.session_id = session_id
        self.base_time = base_time or time.time()
        self.handlers: List[LogHandler] = []
        self._lock = threading.Lock()

        # Default structured handler
        self.structured_handler = StructuredLogHandler()
        self.add_handler(self.structured_handler)

    def add_handler(self, handler: LogHandler) -> None:
        """Add a log handler."""
        with self._lock:
            self.handlers.append(handler)

    def remove_handler(self, handler: LogHandler) -> None:
        """Remove a log handler."""
        with self._lock:
            if handler in self.handlers:
                self.handlers.remove(handler)

    def log(self, level: LogLevel, component: str, message: str,
            context: Optional[Dict[str, Any]] = None) -> None:
        """Log a structured entry."""
        entry = LogEntry(
            timestamp=time.time() - self.base_time,
            level=level,
            component=component,
            message=message,
            context=context or {}
        )

        with self._lock:
            for handler in self.handlers:
                try:
                    handler.handle(entry)
                except Exception as e:
                    # Avoid logging failures breaking the system
                    print(f"Log handler error: {e}", file=sys.stderr)

    def debug(self, component: str, message: str, **context) -> None:
        self.log(LogLevel.DEBUG, component, message, context)

    def info(self, component: str, message: str, **context) -> None:
        self.log(LogLevel.INFO, component, message, context)

    def warning(self, component: str, message: str, **context) -> None:
        self.log(LogLevel.WARNING, component, message, context)

    def error(self, component: str, message: str, **context) -> None:
        self.log(LogLevel.ERROR, component, message, context)

    def get_logs(self, min_level: LogLevel = LogLevel.INFO) -> List[Dict[str, Any]]:
        """Get structured logs as dictionary list."""
        return self.structured_handler.to_dict_list(min_level)

    def clear_logs(self) -> None:
        """Clear accumulated logs."""
        self.structured_handler.clear()

    @contextmanager
    def capture_stdout(self):
        """Context manager to capture stdout prints."""
        old_stdout = sys.stdout
        captured_output = io.StringIO()

        try:
            sys.stdout = captured_output
            yield captured_output
        finally:
            sys.stdout = old_stdout

            # Log captured output
            output = captured_output.getvalue()
            if output.strip():
                for line in output.strip().split('\n'):
                    if line.strip():
                        self.info("stdout_capture", line.strip())

# Global logger registry for session management
_session_loggers: Dict[str, StructuredLogger] = {}
_logger_lock = threading.Lock()

def get_logger(session_id: str) -> StructuredLogger:
    """Get or create a logger for a session."""
    with _logger_lock:
        if session_id not in _session_loggers:
            _session_loggers[session_id] = StructuredLogger(session_id)
        return _session_loggers[session_id]

def destroy_logger(session_id: str) -> bool:
    """Destroy a session logger."""
    with _logger_lock:
        return _session_loggers.pop(session_id, None) is not None

# Backward compatibility: Legacy print replacement
class LegacyPrintReplacer:
    """Replaces print statements with structured logging."""

    def __init__(self, logger: StructuredLogger, component: str,
                 min_verbose_level: int = 1):
        self.logger = logger
        self.component = component
        self.min_verbose_level = min_verbose_level

    def print_if_verbose(self, message: str, verbose_level: int,
                        current_verbose: int) -> None:
        """Replace verbose-conditional prints."""
        if current_verbose >= verbose_level:
            if verbose_level >= self.min_verbose_level:
                level = LogLevel.INFO if verbose_level <= 2 else LogLevel.DEBUG
                self.logger.log(level, self.component, message,
                              {"verbose_level": verbose_level})

            # Also print to stdout for backward compatibility
            if current_verbose >= verbose_level:
                print(f"{self.component}> {message}")

# Performance monitoring
@dataclass
class LoggingStats:
    """Statistics for logging performance monitoring."""
    total_entries: int = 0
    entries_by_level: Dict[str, int] = field(default_factory=dict)
    memory_usage_mb: float = 0.0
    avg_log_time_ms: float = 0.0

def get_logging_stats(logger: StructuredLogger) -> LoggingStats:
    """Get performance statistics for a logger."""
    entries = logger.structured_handler.get_entries()

    stats = LoggingStats()
    stats.total_entries = len(entries)

    for entry in entries:
        level_name = entry.level.name
        stats.entries_by_level[level_name] = stats.entries_by_level.get(level_name, 0) + 1

    # Estimate memory usage (rough calculation)
    if entries:
        avg_entry_size = sum(
            len(str(entry.message)) + len(str(entry.context)) + 100  # overhead
            for entry in entries
        ) / len(entries)
        stats.memory_usage_mb = (avg_entry_size * len(entries)) / (1024 * 1024)

    return stats
