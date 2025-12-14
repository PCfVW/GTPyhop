"""
GTPyhop: A Goal-Task-Network planning system
Version 1.7.0 with
- session-based architecture (1.3),
- structured logging (1.3),
- plan validation (1.4),
- MCP orchestration examples (1.5),
- documentation style guides (1.6),
- enhanced MCP orchestration and consistency updates (1.7)

This module provides hierarchical task network (HTN) planning capabilities
with support for both goals and tasks.

Version 1.3 introduces session-based planning for better isolation and
structured logging for improved debugging.

Version 1.4 introduces basic plan validation.

Version 1.5 introduces MCP orchestration examples.

Version 1.6 introduces documentation style guides for actions, methods, and problems.

Version 1.7 introduces enhanced MCP orchestration examples, bug fixes, and comprehensive
documentation consistency updates.
"""

import os
import warnings

# Version information
__version__ = "1.7.0"
__author__ = "Dana Nau, Eric Jacopin"
__license__ = "Clear BSD License"
__description__ = "A Goal-Task-Network planning package written in Python"

# Control import-time behavior via environment variables
_GTPYHOP_QUIET = os.getenv("GTPYHOP_QUIET", "false").lower() == "true"
_GTPYHOP_NO_DEFAULTS = os.getenv("GTPYHOP_NO_DEFAULTS", "false").lower() == "true"
_GTPYHOP_WARN_GLOBALS = os.getenv("GTPYHOP_WARN_GLOBALS", "false").lower() == "true"

# Import core functionality
from .main import (
    # === VALIDATION API (New in 1.4) ===
    validate_plan_from_goal,

    # === SESSION-BASED API (New in 1.3) ===
    PlannerSession,
    PlanResult,
    ExecutionResult,
    PlanningTimeoutError,
    get_session,
    create_session,
    destroy_session,
    list_sessions,

    # === RESOURCE MANAGEMENT (New in 1.3) ===
    ResourceManager,

    # === PERSISTENCE (New in 1.3) ===
    SessionPersistenceError,
    SessionSerializer,
    restore_session,
    restore_all_sessions,
    set_persistence_directory,
    get_persistence_directory,

    # === CORE CLASSES ===
    Domain,
    State,
    Multigoal,

    # === TRADITIONAL PLANNING API (Preserved) ===
    find_plan,
    run_lazy_lookahead,
    pyhop,  # Alias for find_plan

    # === DOMAIN MANAGEMENT ===
    current_domain,
    set_current_domain,
    get_current_domain,
    print_domain,
    print_domain_names,
    find_domain_by_name,
    is_domain_created,

    # === KNOWLEDGE DECLARATION ===
    declare_actions,
    declare_operators,  # Alias for declare_actions
    declare_commands,
    declare_task_methods,
    declare_methods,    # Alias for declare_task_methods
    declare_unigoal_methods,
    declare_multigoal_methods,

    # === DISPLAY AND DEBUGGING ===
    print_actions,
    print_operators,
    print_commands,
    print_methods,
    print_state,
    print_multigoal,
    get_type,

    # === GOAL UTILITIES ===
    m_split_multigoal,

    # === CONFIGURATION ===
    verbose,
    set_verbose_level,
    get_verbose_level,
    set_recursive_planning,
    get_recursive_planning,
    reset_planning_strategy,
)

# Import structured logging system (with graceful fallback)
try:
    from .logging_system import (
        LogLevel,
        LogEntry,
        StructuredLogger,
        StdoutLogHandler,
        StructuredLogHandler,
        get_logger,
        destroy_logger,
        get_logging_stats,
        LoggingStats,
    )
    _STRUCTURED_LOGGING_AVAILABLE = True
except ImportError:
    # Graceful fallback if logging system not available
    _STRUCTURED_LOGGING_AVAILABLE = False
    LogLevel = None
    LogEntry = None
    StructuredLogger = None
    StdoutLogHandler = None
    StructuredLogHandler = None
    get_logger = None
    destroy_logger = None
    get_logging_stats = None
    LoggingStats = None

# === BACKWARD COMPATIBILITY WARNINGS ===
if _GTPYHOP_WARN_GLOBALS:
    # Wrap global state functions with deprecation warnings
    _original_find_plan = find_plan
    _original_run_lazy_lookahead = run_lazy_lookahead

    def _warn_global_usage(func_name: str):
        warnings.warn(
            f"{func_name} uses global state. Consider using PlannerSession "
            f"for better isolation. Set GTPYHOP_WARN_GLOBALS=false to disable.",
            DeprecationWarning,
            stacklevel=3
        )

    def find_plan(*args, **kwargs):
        _warn_global_usage("find_plan")
        return _original_find_plan(*args, **kwargs)

    def run_lazy_lookahead(*args, **kwargs):
        _warn_global_usage("run_lazy_lookahead")
        return _original_run_lazy_lookahead(*args, **kwargs)

# === IMPORT-TIME INITIALIZATION ===
if not _GTPYHOP_QUIET:
    print(f"\nImported GTPyhop version {__version__}")
    print("Messages from find_plan will be prefixed with 'FP>'.")
    print("Messages from run_lazy_lookahead will be prefixed with 'RLL>'.")
    if _STRUCTURED_LOGGING_AVAILABLE:
        print("Using session-based architecture with structured logging.")
    else:
        print("Using session-based architecture (structured logging not available).")

# Set default planning strategy (unless disabled)
if not _GTPYHOP_NO_DEFAULTS:
    set_recursive_planning(False)  # Default to iterative planning

# === PUBLIC API DEFINITION ===
__all__ = [
    # Version and metadata
    "__version__", "__author__", "__license__", "__description__",

    # Validation API (New in 1.4)
    "validate_plan_from_goal",

    # Session-based API (New in 1.3)
    "PlannerSession", "PlanResult", "ExecutionResult", "PlanningTimeoutError",
    "get_session", "create_session", "destroy_session", "list_sessions",

    # Resource management (New in 1.3)
    "ResourceManager",

    # Persistence (New in 1.3)
    "SessionPersistenceError", "SessionSerializer",
    "restore_session", "restore_all_sessions",
    "set_persistence_directory", "get_persistence_directory",

    # Core classes
    "Domain", "State", "Multigoal",

    # Traditional planning API
    "find_plan", "run_lazy_lookahead", "pyhop",

    # Domain management
    "current_domain", "set_current_domain", "get_current_domain",
    "print_domain", "print_domain_names", "find_domain_by_name", "is_domain_created",

    # Knowledge declaration
    "declare_actions", "declare_operators", "declare_commands",
    "declare_task_methods", "declare_methods",
    "declare_unigoal_methods", "declare_multigoal_methods",

    # Display and debugging
    "print_actions", "print_operators", "print_commands", "print_methods",
    "print_state", "print_multigoal", "get_type",

    # Goal utilities
    "m_split_multigoal",

    # Configuration
    "verbose", "set_verbose_level", "get_verbose_level",
    "set_recursive_planning", "get_recursive_planning", "reset_planning_strategy",
]

# Add structured logging to __all__ if available
if _STRUCTURED_LOGGING_AVAILABLE:
    __all__.extend([
        "LogLevel", "LogEntry", "StructuredLogger",
        "StdoutLogHandler", "StructuredLogHandler",
        "get_logger", "destroy_logger", "get_logging_stats", "LoggingStats",
    ])

# === COMPATIBILITY CHECKS ===
def _check_python_version():
    """Ensure Python version compatibility."""
    import sys
    if sys.version_info < (3, 8):
        warnings.warn(
            "GTPyhop 1.3 is tested with Python 3.8+. "
            "Earlier versions may work but are not officially supported.",
            RuntimeWarning
        )

_check_python_version()