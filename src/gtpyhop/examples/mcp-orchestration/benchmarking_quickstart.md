# MCP Orchestration Benchmarking - Quick Start Guide

## Overview

The benchmarking script (`benchmarking.py`) is a thin wrapper that delegates to the shared benchmarking infrastructure from `ipc-2020-total-order/`. It automatically discovers and runs domain packages, measuring planning performance and reporting statistics.

## Prerequisites

- **GTPyhop 1.4.0** (or later) installed
- **psutil** package (for resource tracking)
- Python 3.8 or later

### Installing Dependencies

```bash
pip install gtpyhop psutil
```

Or for local development:
```bash
cd C:\Users\Eric JACOPIN\Documents\Code\Source\GTPyhop
pip install -e .
pip install psutil
```

## Running the Benchmarking Script

### Basic Usage

```bash
cd C:\Users\Eric JACOPIN\Documents\Code\Source\GTPyhop\src\gtpyhop\examples\mcp-orchestration
python benchmarking.py tnf_cancer_modelling
```

### Command-Line Options

```bash
# Run with minimal output (verbosity 0)
python benchmarking.py tnf_cancer_modelling --verbose 0

# Run with detailed output (verbosity 2)
python benchmarking.py tnf_cancer_modelling --verbose 2

# Run with maximum debugging output (verbosity 3)
python benchmarking.py tnf_cancer_modelling --verbose 3

# Run using PlannerSession (thread-safe mode, GTPyhop 1.4.0+)
python benchmarking.py tnf_cancer_modelling --mode session

# Combine options
python benchmarking.py tnf_cancer_modelling --mode session --verbose 2

# Run all problems in the domain
python benchmarking.py tnf_cancer_modelling --all-problems
```

### Verbosity Levels

- **0**: Silent (only final summary)
- **1**: Normal (default) - shows plan found/not found
- **2**: Detailed - shows task decomposition and method selection
- **3**: Debug - shows all internal planner operations

### Planning Modes

- **legacy**: Uses global state (default, faster)
- **session**: Uses PlannerSession (thread-safe, recommended for GTPyhop 1.4.0+)

## Interpreting Results

### Successful Run Example

```
================================================================================
BENCHMARKING: tnf_cancer_modelling
================================================================================
Mode: session
Verbosity: 1
Domain: tnf_cancer_modelling
Problems: 1
================================================================================

Running problem: scenario_1
  ✓ scenario_1: SUCCESS - 12 actions in 0.023s

================================================================================
SUMMARY
================================================================================
Total problems: 1
Successful: 1
Failed: 0

Successful problems:
  Total planning time: 0.023s
  Average planning time: 0.023s
  Total actions: 12
  Average actions per plan: 12.0
================================================================================
```

### Failed Run Example

```
Running problem: scenario_1
  ✗ scenario_1: FAILED - No plan found

================================================================================
SUMMARY
================================================================================
Total problems: 1
Successful: 0
Failed: 1

Failed problems:
  - scenario_1: No plan found
================================================================================
```

## Understanding the Output

### Success Indicators

- **✓** - Problem ran successfully and found a plan
- **Plan length** - Number of primitive actions in the generated plan
- **Planning time** - Time taken to find the plan (in seconds)

### Failure Indicators

- **✗** - Problem failed to find a plan or encountered an error
- **Error message** - Description of what went wrong

### Summary Statistics

- **Total problems** - Number of problems discovered and run
- **Successful** - Number of problems that found a plan
- **Failed** - Number of problems that failed
- **Total planning time** - Sum of all planning times
- **Average planning time** - Mean planning time across successful problems
- **Total actions** - Sum of all plan lengths
- **Average actions per plan** - Mean plan length across successful problems

## Adding New Examples to the Benchmarking Suite

To add a new MCP orchestration example:

1. **Create a new subdirectory** under `mcp-orchestration/` following the **GTPyhop 1.4.0 new structure**:
   ```
   mcp-orchestration/
   ├── tnf_cancer_modelling/
   ├── your_new_example/        # New example directory
   │   ├── domain.py             # Required: domain creation + actions + methods
   │   ├── problems.py           # Required: defines initial_state_* problems
   │   ├── __init__.py           # Required: exports domain and get_problems()
   │   └── README.md             # Optional but recommended
   └── benchmarking.py
   ```

2. **Required files**:
   - `domain.py` - Must create domain, define all actions and methods, and declare them
   - `problems.py` - Must define initial states with `initial_state_` prefix (e.g., `initial_state_scenario_1`)
   - `__init__.py` - Must export `the_domain` and implement `get_problems()` function

3. **Required structure in `__init__.py`**:
   ```python
   from . import domain
   from . import problems

   the_domain = domain.the_domain

   def get_problems():
       """Return all state/task pairs for this domain."""
       problem_dict = {}
       for attr_name in dir(problems):
           if attr_name.startswith('initial_state_'):
               problem_id = attr_name.replace('initial_state_', '')
               state = getattr(problems, attr_name)
               task = [('your_top_level_task',)]  # e.g., ('m_multiscale_tnf_cancer_modeling',)
               problem_dict[problem_id] = (state, task)
       return problem_dict
   ```

4. **Run the benchmarking script** - It will automatically discover and run your new example:
   ```bash
   python benchmarking.py your_new_example
   ```

## Customizing the Benchmarking Script

### Changing the Top-Level Task

The top-level task is defined in each domain's `__init__.py` file in the `get_problems()` function. Edit your domain's `__init__.py`:

```python
def get_problems():
    """Return all state/task pairs for this domain."""
    problem_dict = {}
    for attr_name in dir(problems):
        if attr_name.startswith('initial_state_'):
            problem_id = attr_name.replace('initial_state_', '')
            state = getattr(problems, attr_name)
            task = [('your_custom_task_name',)]  # Change this
            problem_dict[problem_id] = (state, task)
    return problem_dict
```

### Using the Shared Benchmarking Infrastructure

The `mcp-orchestration/benchmarking.py` is a thin wrapper that imports from `ipc-2020-total-order/benchmarking.py`. To customize benchmarking behavior, you can:

1. **Modify the shared infrastructure** at `ipc-2020-total-order/benchmarking.py` (affects all domains)
2. **Create a custom wrapper** specific to your needs in `mcp-orchestration/`

## Troubleshooting

### "Error: psutil module is required"

**Solution**: Install psutil:
```bash
pip install psutil
```

### "Could not import gtpyhop"

**Solution**: Install GTPyhop:
```bash
pip install gtpyhop
```

### "No module named 'your_domain_name'"

**Solution**: Ensure your domain directory has:
- `__init__.py` with proper exports
- `domain.py` with domain creation
- `problems.py` with initial states

### "No plan found"

**Possible causes**:
- Initial state doesn't satisfy preconditions
- Methods or actions have bugs
- Task decomposition is incorrect

**Debug steps**:
1. Run with `--verbose 3` to see detailed planner output
2. Check that initial states have all required properties
3. Verify method preconditions match action effects
4. Test domain loading: `python -c "from your_domain import the_domain; print(the_domain)"`

### "AttributeError: 'module' object has no attribute 'get_problems'"

**Solution**: Ensure your `__init__.py` implements the `get_problems()` function:
```python
def get_problems():
    """Return all state/task pairs for this domain."""
    problem_dict = {}
    for attr_name in dir(problems):
        if attr_name.startswith('initial_state_'):
            problem_id = attr_name.replace('initial_state_', '')
            state = getattr(problems, attr_name)
            task = [('your_top_level_task',)]
            problem_dict[problem_id] = (state, task)
    return problem_dict
```

## Performance Tips

- Use `--verbose 0` for fastest benchmarking (no output overhead)
- Use `--mode session` for thread-safe execution (recommended for GTPyhop 1.4.0+)
- Use `--mode legacy` for slightly faster execution (global state, not thread-safe)
- For large examples, consider increasing Python's recursion limit if needed

## Next Steps

- Review individual domain README.md files for detailed documentation
- Examine generated plans to understand task decomposition
- Modify problems to test different planning scenarios
- Add new domains following the GTPyhop 1.4.0 new structure pattern
- Explore the shared benchmarking infrastructure in `ipc-2020-total-order/benchmarking.py`

