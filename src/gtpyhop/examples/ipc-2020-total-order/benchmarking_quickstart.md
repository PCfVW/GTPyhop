# GTPyhop Benchmarking Quickstart Guide

## Overview

This guide helps you quickly get started with running GTPyhop benchmarks on planning domains from the IPC 2020 Total Order track. The benchmarking script provides an easy-to-use command-line interface for testing planning performance across different problem instances using **GTPyhop 1.3.0's thread-safe session-based architecture**.

## Prerequisites

Before running benchmarks, ensure you have the required dependencies installed:

```bash
pip install gtpyhop>=1.3.0 psutil
```

**Important**: GTPyhop 1.3.0+ is required for thread-safe session-based planning. Earlier versions will fall back to legacy mode.

## Thread-Safe Sessions Overview

The benchmarking system uses **GTPyhop 1.3.0's thread-safe session-based planning** by default, providing:

- **🔒 Thread Safety**: Multiple benchmarks can run concurrently without interference
- **🎯 Isolated Execution**: Each benchmark runs in its own isolated planning context
- **📊 Better Resource Management**: Per-session configuration and monitoring
- **🚀 Production Ready**: Reliable for concurrent and production environments

For technical details, see [GTPyhop 1.3.0 Thread-Safe Sessions](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md).

## Quick Start

### 1. List Available Domains

See what domains are available for benchmarking:

```bash
python benchmarking.py --list-domains
```

**Expected Output:**
```
Available domains:
  - Blocksworld-GTOHP
  - Childsnack
```

### 2. Run Your First Benchmark

Test the Blocksworld domain with thread-safe sessions (default):

```bash
python benchmarking.py Blocksworld-GTOHP
```

**Expected Output:**
```
Running benchmarks for Blocksworld-GTOHP using Thread-Safe Sessions planning...
```

This will run all 20 Blocksworld problems using isolated planning sessions and display results sorted by execution time.

### 3. Explore Different Options

```bash
# Run with verbose planning output (per-session verbosity)
python benchmarking.py Childsnack --verbose 1

# Sort results by memory usage
python benchmarking.py Blocksworld-GTOHP --sort-by memory

# Check which GTPyhop installation is being used
python benchmarking.py --show-imports

# Use legacy mode (not recommended for production)
python benchmarking.py Blocksworld-GTOHP --legacy-mode
```

## Planning Modes

### Thread-Safe Sessions (Default - Recommended)

**Status Message**: `"Running benchmarks for <domain> using Thread-Safe Sessions planning..."`

- **Benefits**: Thread-safe, isolated execution, production-ready
- **Use Cases**: Production environments, concurrent benchmarking, reliable results
- **Requirements**: GTPyhop 1.3.0+, domain must have `the_domain` object

### Legacy Global Mode

**Status Message**: `"Running benchmarks for <domain> using Legacy Global planning..."`
**Warning**: `"⚠️ WARNING: Using legacy mode. Thread-safe sessions are recommended for production use."`

- **When to Use**: Debugging, compatibility testing, or when domain objects are unavailable
- **Limitations**: Not thread-safe, global state interference possible
- **Activation**: Use `--legacy-mode` flag

## Understanding the Results

The benchmark output shows a detailed table with the following columns:

- **Problem**: Name of the problem instance
- **Status**: ✅ (success) or ❌ (failure)
- **Plan Len**: Number of actions in the solution plan
- **Time (s)**: Execution time in seconds
- **CPU %**: CPU usage percentage during planning
- **Mem Δ (KB)**: Memory change during planning
- **Peak Mem (KB)**: Peak memory usage

### Sample Results

**Blocksworld-GTOHP Performance (Thread-Safe Sessions):**
- **Success Rate**: 95% (19/20 problems solved)
- **Plan Lengths**: 18 to 1,089 actions
- **Execution Times**: 0.002s to 0.083s
- **Memory Usage**: 25MB to 39MB peak

**Childsnack Performance (Thread-Safe Sessions):**
- **Success Rate**: 100% (30/30 problems solved)
- **Plan Lengths**: 50 to 2,500 actions  
- **Execution Times**: 0.006s to 3.496s
- **Memory Usage**: 25MB to 39MB peak

## Command Reference

### Basic Usage
```bash
python benchmarking.py <domain>
```

### Available Options

| Option | Description | Example |
|--------|-------------|---------|
| `--list-domains` | Show available domains | `python benchmarking.py --list-domains` |
| `--verbose <0-3>` | Set planning verbosity level (per-session) | `python benchmarking.py Childsnack --verbose 2` |
| `--sort-by <time\|memory\|name>` | Sort results by criteria | `python benchmarking.py Blocksworld-GTOHP --sort-by memory` |
| `--show-imports` | Display GTPyhop import source | `python benchmarking.py --show-imports` |
| `--legacy-mode` | Use legacy global planning (not recommended) | `python benchmarking.py Blocksworld-GTOHP --legacy-mode` |

### Help and Examples
```bash
python benchmarking.py --help
```

## Concurrent Benchmarking Benefits

**New in V2**: Thread-safe sessions enable safe concurrent execution:

```bash
# Safe to run multiple benchmarks simultaneously
python benchmarking.py Blocksworld-GTOHP &
python benchmarking.py Childsnack &
wait  # Wait for both to complete
```

Each benchmark runs in its own isolated session, preventing interference and ensuring reliable results.

## Domain Information

### Blocksworld-GTOHP
- **Problems**: 20 instances (BW_rand_5 to BW_rand_43)
- **Complexity**: 5 to 43 blocks
- **Domain Type**: Classic blocks world with stacking
- **Average Performance**: ~0.01s per problem
- **Session Support**: ✅ Full thread-safe session support

### Childsnack  
- **Problems**: 30 instances (childsnack_p01 to childsnack_p30)
- **Complexity**: 10 to 500 children to serve
- **Domain Type**: Sandwich making and serving
- **Average Performance**: ~0.2s per problem
- **Session Support**: ✅ Full thread-safe session support

## Troubleshooting

### Common Issues

**"Error: GTPyhop is not available"**
```bash
pip install gtpyhop>=1.3.0 psutil
```

**"Error: Domain 'X' not found"**
- Check available domains with `--list-domains`
- Ensure domain name is spelled correctly (case-sensitive)

**"⚠️ WARNING: Domain object 'the_domain' not found. Falling back to legacy mode."**
- This indicates the domain doesn't have a proper domain object
- The system automatically falls back to legacy mode
- Consider updating the domain implementation for full session support

**"No problems found in domain"**
- Verify domain files are properly installed
- Check that domain packages have required files (__init__.py, domain.py, problems.py)

### Session-Related Issues

**Planning seems slower than expected**
- Ensure you're using thread-safe sessions (default mode)
- Check that GTPyhop 1.3.0+ is installed: `pip show gtpyhop`

**Concurrent benchmarks interfering with each other**
- Verify you're not using `--legacy-mode`
- Thread-safe sessions (default) prevent interference

### Getting Help

1. Use `--help` for command-line options
2. Use `--show-imports` to verify GTPyhop installation and version
3. Use `--list-domains` to see available domains
4. Check domain README files for specific domain information
5. Review [GTPyhop 1.3.0 Thread-Safe Sessions](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md) for technical details

## Performance Tips

1. **Start Small**: Begin with Blocksworld for quick tests
2. **Use Sessions**: Leverage the default thread-safe sessions for reliable results
3. **Monitor Resources**: Use `--sort-by memory` for memory analysis
4. **Concurrent Testing**: Run multiple domains simultaneously for efficiency
5. **Appropriate Verbosity**: Use `--verbose 1` to see planning progress per session

## Next Steps

- Explore individual domain README files for detailed information
- Experiment with concurrent benchmarking using thread-safe sessions
- Compare performance between session and legacy modes
- Use results to analyze planning algorithm efficiency in isolated contexts
- Review [GTPyhop 1.3.0 Thread-Safe Sessions](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md) for advanced session features

---

*For detailed domain information, see the README files in the Blocksworld-GTOHP/ and Childsnack/ directories.*
*For technical details on thread-safe sessions, see [GTPyhop 1.3.0 Thread-Safe Sessions](https://github.com/PCfVW/GTPyhop/blob/pip/docs/thread_safe_sessions.md).*
