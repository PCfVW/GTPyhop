# GTPyhop Structured Logging System

GTPyhop 1.3.0 introduces a comprehensive structured logging system that replaces traditional print statements with configurable, thread-safe logging. This system provides programmatic access to planning logs, statistics, and debugging information.

## 🎯 Why Structured Logging?

**Traditional challenges:**
- Print statements mixed with actual output
- No programmatic access to planning information
- Difficult to filter or analyze planning traces
- Thread safety issues in concurrent scenarios

**Structured logging benefits:**
- **Programmatic access**: Query and analyze logs programmatically
- **Thread isolation**: Each session maintains separate logs
- **Configurable output**: Control verbosity and formatting
- **Performance monitoring**: Built-in statistics and performance metrics
- **Backward compatibility**: Existing print-based output still works

## 🔧 How It Works

The logging system operates in both legacy and session modes:

**Legacy Mode:** Uses global logging with backward-compatible print output
**Session Mode:** Each `PlannerSession` has isolated logging with structured data collection

## 📊 Log Levels and Components

**Available log levels:**
- `DEBUG` (0): Detailed debugging information
- `INFO` (1): General planning information
- `WARNING` (2): Warning messages
- `ERROR` (3): Error conditions

**Common components:**
- `FP`: Messages from `find_plan()`
- `RLL`: Messages from `run_lazy_lookahead()`
- `domain`: Domain-related operations
- `session`: Session management
- `stdout_capture`: Captured print statements

## 💻 Basic Usage Examples

**Import note:** All logging classes and functions are available directly from the main `gtpyhop` module:

```python
import gtpyhop

# Logging classes are available as gtpyhop.LogLevel, gtpyhop.StructuredLogger, etc.
# Or import specific components:
from gtpyhop import LogLevel, StructuredLogger, get_logging_stats
```

### **Session Mode Logging (Recommended)**

```python
import gtpyhop

# Create session with logging
with gtpyhop.PlannerSession(domain=my_domain, verbose=2) as session:
    with session.isolated_execution():
        result = session.find_plan(state, goals)

        # Access structured logs
        logs = session.logger.get_logs()  # Get all INFO+ logs
        debug_logs = session.logger.get_logs(min_level=gtpyhop.LogLevel.DEBUG)

        # Print log summary
        print(f"Generated {len(logs)} log entries")
        for log in logs:
            print(f"[{log['level']}] {log['component']}: {log['message']}")
```

### **Custom Log Handlers**

```python
import gtpyhop

# Create custom logger
logger = gtpyhop.StructuredLogger("my_session")

# Add custom stdout handler with formatting
custom_handler = gtpyhop.StdoutLogHandler("[{level}] {component}: {message}")
logger.add_handler(custom_handler)

# Log custom messages
logger.info("planning", "Starting plan search", state_size=len(state.pos))
logger.debug("search", "Exploring method", method_name="transport_by_truck")
```

### **Programmatic Log Analysis**

```python
# Run planning with logging
with gtpyhop.PlannerSession(domain=logistics_domain, verbose=3) as session:
    with session.isolated_execution():
        result = session.find_plan(initial_state, goals)

        # Analyze logs
        logs = session.logger.get_logs()

        # Count log entries by component
        component_counts = {}
        for log in logs:
            component = log['component']
            component_counts[component] = component_counts.get(component, 0) + 1

        print("Log summary by component:")
        for component, count in component_counts.items():
            print(f"  {component}: {count} entries")

        # Find error logs
        error_logs = [log for log in logs if log['level'] == 'ERROR']
        if error_logs:
            print(f"Found {len(error_logs)} errors:")
            for error in error_logs:
                print(f"  {error['message']}")
```

## 🧵 Thread-Safe Concurrent Logging

Each session maintains isolated logs, making concurrent planning safe:

```python
import threading
import gtpyhop

def concurrent_planner(session_id, domain, state, goals):
    """Each thread gets isolated logging."""
    with gtpyhop.PlannerSession(domain=domain, verbose=2) as session:
        with session.isolated_execution():
            result = session.find_plan(state, goals)

            # Each session has separate logs
            logs = session.logger.get_logs()
            print(f"Session {session_id}: {len(logs)} log entries")

            return result, logs

# Run multiple planners concurrently
threads = []
results = {}

for i in range(3):
    def worker(session_id=i):
        result, logs = concurrent_planner(session_id, domain, state, goals)
        results[session_id] = {"result": result, "logs": logs}

    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Analyze results from each session
for session_id, data in results.items():
    print(f"Session {session_id}: {len(data['logs'])} logs, "
          f"plan length: {len(data['result'].plan) if data['result'].success else 'failed'}")
```

## 📈 Performance Monitoring

The logging system includes built-in performance monitoring:

```python
import gtpyhop

with gtpyhop.PlannerSession(domain=my_domain, verbose=2) as session:
    with session.isolated_execution():
        result = session.find_plan(state, goals)

        # Get logging statistics
        stats = gtpyhop.get_logging_stats(session.logger)

        print(f"Logging Performance:")
        print(f"  Total entries: {stats.total_entries}")
        print(f"  Memory usage: {stats.memory_usage_mb:.2f} MB")
        print(f"  Entries by level: {stats.entries_by_level}")
```

## 🔄 Legacy Mode Compatibility

The logging system maintains backward compatibility with existing code:

```python
# Legacy code continues to work
gtpyhop.verbose = 2
plan = gtpyhop.find_plan(state, goals)  # Prints to stdout as before

# But you can also access logs programmatically
logger = gtpyhop.get_logger("default")  # Get default session logger
logs = logger.get_logs()
print(f"Legacy planning generated {len(logs)} log entries")
```

## 🛠️ Advanced Features

### **Stdout Capture**

Capture and log print statements from legacy code:

```python
logger = gtpyhop.StructuredLogger("capture_session")

with logger.capture_stdout() as captured:
    # Any print statements here are captured and logged
    print("This will be captured")
    gtpyhop.find_plan(state, goals)  # Legacy prints captured

# Captured output is now in structured logs
logs = logger.get_logs()
stdout_logs = [log for log in logs if log['component'] == 'stdout_capture']
```

### **Custom Log Filtering**

```python
# Filter logs by component and level
def filter_planning_logs(logs, component_filter=None, min_level='INFO'):
    filtered = []
    for log in logs:
        if component_filter and log['component'] != component_filter:
            continue
        if log['level'] not in ['DEBUG', 'INFO', 'WARNING', 'ERROR'][
            ['DEBUG', 'INFO', 'WARNING', 'ERROR'].index(min_level):]:
            continue
        filtered.append(log)
    return filtered

# Usage
planning_logs = filter_planning_logs(logs, component_filter='FP', min_level='INFO')
```

## 🎓 Integration with Examples

All migrated examples support structured logging in session mode:

```bash
# Run with high verbosity to see detailed logs
python -m gtpyhop.examples.blocks_htn.examples --session --verbose 3

# The logs are available programmatically when using session mode
```

**Example integration in your code:**

```python
# Import any migrated example domain
from gtpyhop.examples.blocks_htn import the_domain, actions, methods

# Use with structured logging
with gtpyhop.PlannerSession(domain=the_domain, verbose=2) as session:
    with session.isolated_execution():
        result = session.find_plan(initial_state, goals)

        # Access detailed planning logs
        logs = session.logger.get_logs()
        method_calls = [log for log in logs if 'method' in log.get('context', {})]
        print(f"Called {len(method_calls)} methods during planning")
```
