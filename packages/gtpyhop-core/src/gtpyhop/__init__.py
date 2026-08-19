"""
GTPyhop: A Goal-Task-Network planning system
Version 2.0.0 with
- session-based architecture (1.3),
- structured logging (1.3),
- plan validation (1.4),
- MCP orchestration examples (1.5),
- documentation style guides (1.6),
- enhanced MCP orchestration and consistency updates (1.7),
- accurate memory tracking with background monitoring (1.8),
- iterative DFS planning with full backtracking (1.9)
- cybersecurity attack planning example based on BAMS domain (1.9.5)
- Android: Netrunner run planning example based on the 2012 core set rulebook (1.9.6)
- Trunk Thumper game-AI tutorial collection based on Troy Humphreys' Game AI Pro chapter (1.9.6)
- Colt Express example collection mirroring trunk_thumper's pattern catalog (1.9.7)
- Control Arena adversarial_protocol extended with threat-model variety and [EXPECTED_EFFECT] marker (1.9.7)
- Split into gtpyhop-core, gtpyhop-examples, and the gtpyhop meta-package (2.0)
- PlanTrace execution diagnostics via find_plan(..., trace=True), plus correct
  PlanResult/ExecutionResult truthiness (2.0)

This module provides hierarchical task network (HTN) planning capabilities
with support for both goals and tasks.

Version 1.3 introduces session-based planning for better isolation and
structured logging for improved debugging.

Version 1.4 introduces basic plan validation.

Version 1.5 introduces MCP orchestration examples.

Version 1.6 introduces documentation style guides for actions, methods, and problems.

Version 1.7 introduces enhanced MCP orchestration examples, bug fixes, and comprehensive
documentation consistency updates.

Version 1.8 introduces accurate memory tracking using psutil with background thread
monitoring for peak detection. Memory tracking is opt-in (disabled by default).

Version 1.9 introduces iterative DFS planning with full backtracking via explicit stack.
Activated via set_recursive_planning("iterative_dfs_backtracking") or
PlannerSession(strategy="iterative_dfs_backtracking"). Backward compatible:
existing True/False callers are unaffected.

Version 2.0 splits distribution into three PyPI packages: gtpyhop-core (this package,
the planner only), gtpyhop-examples (the bundled example domains, depends on
gtpyhop-core), and gtpyhop (a meta-package depending on both, for full backward
compatibility with `pip install gtpyhop`). The public API of this package (import
gtpyhop) is unchanged.

Version 2.0 also introduces opt-in execution diagnostics: find_plan(..., trace=True)
populates result.trace with a PlanTrace recording every action-application and
method-refinement attempt (depth, item, status) made during the search -- covering
actions and task/unigoal/multigoal method refinement alike, uniformly across all
three planning strategies. Distinct "malformed_return" / "method_malformed_return"
statuses flag an action or method that violates its return contract (an action must
return State or False; a method must return a list or False/None) -- previously
indistinguishable from a legitimate precondition failure or refinement exhaustion.
result.trace.dead_end reports the first such terminal event, or the point where a
task/unigoal/multigoal exhausted every candidate method without success. Default
False; costs nothing when not requested. PlanResult and ExecutionResult also now
correctly support bool(result) (previously always True regardless of .success).
"""

import os
import pkgutil
import warnings

# Let `gtpyhop` span every directory of that name on sys.path, so that
# `gtpyhop.examples` (shipped by the separate gtpyhop-examples distribution)
# is importable alongside this package.
#
# Installed wheels do not need this: both distributions unpack into the same
# site-packages/gtpyhop/ directory, and the merge happens on disk. An EDITABLE
# install does, because each distribution only adds its own src/ to sys.path,
# and this package's __init__.py makes `gtpyhop` a regular package -- which the
# import system resolves in full, discarding gtpyhop-examples' namespace
# portion. Before this line, a developer working from a checkout got
# ModuleNotFoundError: No module named 'gtpyhop.examples', which broke the
# documented `python -m doctest .../problems.py` workflow for every bundled
# example and the `from gtpyhop.examples.X import ...` line inside them.
__path__ = pkgutil.extend_path(__path__, __name__)

# Version information
__version__ = "2.0.2"
__author__ = "Dana Nau, Eric Jacopin"
__license__ = "Clear BSD License"
__description__ = "A Goal-Task-Network planning package written in Python"

# Control import-time behavior via environment variables
_GTPYHOP_QUIET = os.getenv("GTPYHOP_QUIET", "false").lower() == "true"
_GTPYHOP_NO_DEFAULTS = os.getenv("GTPYHOP_NO_DEFAULTS", "false").lower() == "true"
_GTPYHOP_WARN_GLOBALS = os.getenv("GTPYHOP_WARN_GLOBALS", "false").lower() == "true"


def _legacy_owns_colliding_files(dist):
    """
    Does this pre-2.0 `gtpyhop` distribution actually own files that collide
    with gtpyhop-core's?

    A version number alone does not answer that. An *editable* pre-2.0
    install -- `pip install -e .` from a dev checkout, which is how anyone
    working on GTPyhop itself had it -- installs no `gtpyhop/` package
    directory at all: just a `.pth` file pointing at the source tree, plus
    its own dist-info. Nothing can collide, so refusing to import would be a
    false alarm, and the "uninstall everything and reinstall" advice would
    describe a problem the user does not have.

    Returns True only when the distribution still owns at least one real
    `gtpyhop/*.py` file on disk. `dist.files` lists what RECORD *claims*;
    each candidate is checked for existence too, so a stale entry left by a
    half-removed install does not resurrect the false alarm.
    """
    try:
        files = dist.files
    except Exception:  # pragma: no cover - defensive
        files = None
    if files is None:
        # RECORD missing or unreadable, so ownership cannot be determined:
        # fall back to the editable marker. An editable install is the
        # known-benign case; anything else is treated as a possible
        # collision, since being wrong in that direction merely asks the
        # user to check, while the opposite lets silently overwritten files
        # cause confusing failures later.
        #
        # Note `files is None`, not `not files`: an EMPTY list is a readable
        # RECORD that lists nothing, which is a definitive "owns no files"
        # and must fall through to the scan below rather than be treated as
        # undeterminable.
        return not _is_editable_install(dist)

    for path in files:
        parts = getattr(path, "parts", ())
        if len(parts) < 2 or parts[0] != "gtpyhop" or not str(path).endswith(".py"):
            continue
        try:
            if os.path.exists(str(dist.locate_file(path))):
                return True
        except Exception:  # pragma: no cover - defensive
            continue
    return False


def _is_editable_install(dist):
    """True if this distribution was installed with `pip install -e`."""
    try:
        raw = dist.read_text("direct_url.json")
        if not raw:
            return False
        import json
        return bool(json.loads(raw).get("dir_info", {}).get("editable"))
    except Exception:  # pragma: no cover - defensive
        return False


def _check_legacy_gtpyhop_conflict():
    """
    Before 2.0, `gtpyhop` was a single self-contained distribution that
    shipped gtpyhop/__init__.py, main.py, etc. directly. Since 2.0, those
    files are owned by gtpyhop-core, and a pre-2.0 `gtpyhop` install has no
    dependency relationship with it -- so if both end up installed in the
    same environment, pip has no way to know they collide on the same
    site-packages/gtpyhop/ paths, and whichever installed last silently
    overwrote the other's files. Detect that inconsistent state and fail
    loudly instead of letting it cause confusing downstream errors.

    The collision, not the version number, is what matters: see
    _legacy_owns_colliding_files. An old *editable* install owns no
    colliding files, so it is left alone rather than blocking every import
    with a message describing a file collision that does not exist.
    """
    try:
        from importlib.metadata import distribution, PackageNotFoundError
    except ImportError:  # pragma: no cover - Python 3.8+ always has this
        return
    try:
        legacy = distribution("gtpyhop")
    except PackageNotFoundError:
        return
    legacy_version = legacy.version
    try:
        legacy_major = int(legacy_version.split(".")[0])
    except (ValueError, IndexError):  # pragma: no cover - malformed version
        return
    if legacy_major >= 2:
        return
    if not _legacy_owns_colliding_files(legacy):
        # Metadata for a pre-2.0 gtpyhop, but no colliding files: an
        # editable or already-removed install. Nothing is broken.
        return
    raise ImportError(
        f"Both a pre-2.0 'gtpyhop' distribution (version {legacy_version}) "
        "and 'gtpyhop-core' are installed in this environment, and the older "
        "one still owns files under site-packages/gtpyhop/. They collide "
        "there, since pre-2.0 'gtpyhop' predates the gtpyhop-core / "
        "gtpyhop-examples / gtpyhop split and has no dependency relationship "
        "with gtpyhop-core, so whichever was installed last silently "
        "overwrote the other's files. Run: "
        "pip uninstall gtpyhop gtpyhop-core gtpyhop-examples, then "
        "reinstall exactly one of 'gtpyhop' (full bundle), 'gtpyhop-core' "
        "(planner only), or 'gtpyhop-examples' (examples, pulls in "
        "gtpyhop-core automatically)."
    )


_check_legacy_gtpyhop_conflict()

# Import core functionality
from .main import (
    # === VALIDATION API (New in 1.4) ===
    validate_plan_from_goal,

    # === SESSION-BASED API (New in 1.3) ===
    PlannerSession,
    PlanResult,
    ExecutionResult,
    PlanningTimeoutError,

    # === EXECUTION DIAGNOSTICS (New in 2.0) ===
    PlanTrace,
    TraceEvent,

    get_session,
    create_session,
    destroy_session,
    list_sessions,

    # === RESOURCE MANAGEMENT (New in 1.3) ===
    ResourceManager,

    # === PERSISTENCE (New in 1.3) ===
    SESSION_SCHEMA_VERSION,
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
    # verify_goals itself is deliberately NOT re-exported: rebinding a package
    # attribute would not reach the planner, so `gtpyhop.verify_goals = False`
    # would look like it worked while doing nothing. Use these instead.
    set_verify_goals,
    get_verify_goals,
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

    # Execution diagnostics (New in 2.0)
    "PlanTrace", "TraceEvent",

    # Resource management (New in 1.3)
    "ResourceManager",

    # Persistence (New in 1.3; SESSION_SCHEMA_VERSION new in 2.0.2)
    "SESSION_SCHEMA_VERSION",
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
    "set_verify_goals", "get_verify_goals",
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