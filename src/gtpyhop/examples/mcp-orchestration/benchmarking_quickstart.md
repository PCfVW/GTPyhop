# MCP Orchestration Benchmarking - Quick Start Guide

## Overview

The benchmarking script (`benchmarking.py`) is a thin wrapper that delegates to the shared benchmarking infrastructure from `ipc-2020-total-order/`. It automatically discovers and runs domain packages, measuring planning performance and reporting statistics.

## Prerequisites

- **GTPyhop 1.7.0** (or later) installed
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

## Available Examples

| Example | Description | Scenarios | Actions |
|---------|-------------|-----------|---------|
| `bio_opentrons` | PCR workflow automation with dynamic sample scaling across 3 MCP servers | 6 scenarios (4-96 samples) | 55-611 actions |
| `omega_hdq_dna_bacteria_flex_96_channel` | Omega HDQ DNA extraction on Opentrons Flex (4 MCP servers) | 3 scenarios | 89-129 actions |
| `drug_target_discovery` | Drug target discovery pipeline using OpenTargets platform | 3 scenarios | 8 actions |
| `tnf_cancer_modelling` | Multiscale TNF cancer modeling (MaBoSS + PhysiCell) | 1 scenario | 12 actions |
| `cross_server` | Cross-server robot orchestration (pick-and-place) | 2 scenarios | 9-15 actions |

All examples follow the **GTPyhop 1.7.0+ style guide** with unified scenario block format.

## Running the Benchmarking Script

### Basic Usage

```bash
cd src/gtpyhop/examples/mcp-orchestration
python benchmarking.py bio_opentrons
python benchmarking.py omega_hdq_dna_bacteria_flex_96_channel
python benchmarking.py drug_target_discovery
python benchmarking.py tnf_cancer_modelling
python benchmarking.py cross_server
```

### Command-Line Options

```bash
# Run with minimal output (verbosity 0)
python benchmarking.py tnf_cancer_modelling --verbose 0

# Run with detailed output (verbosity 2)
python benchmarking.py tnf_cancer_modelling --verbose 2

# Run with maximum debugging output (verbosity 3)
python benchmarking.py tnf_cancer_modelling --verbose 3

# Run using legacy mode (global state, not recommended)
python benchmarking.py bio_opentrons --legacy-mode

# Combine options
python benchmarking.py bio_opentrons --legacy-mode --verbose 2
```

### Verbosity Levels

- **0**: Silent (only final summary)
- **1**: Normal (default) - shows plan found/not found
- **2**: Detailed - shows task decomposition and method selection
- **3**: Debug - shows all internal planner operations

### Planning Modes

- **session** (default): Uses PlannerSession (thread-safe, recommended for GTPyhop 1.7.0+)
- **legacy**: Uses global state (enabled with `--legacy-mode` flag, not recommended)

## Interpreting Results

### Successful Run Example

```
Imported GTPyhop version 1.7.0
Using GTPyhop from PyPI installation
GTPyhop loaded successfully from: PyPI
Loading domain: tnf_cancer_modelling
Domain tnf_cancer_modelling using GTPyhop from: PyPI
Loaded 1 problems from tnf_cancer_modelling
Found 1 problems in tnf_cancer_modelling

Running benchmarks for tnf_cancer_modelling using Thread-Safe Sessions planning...
Solving scenario_1_multiscale...

=== tnf_cancer_modelling Benchmark Results ===

=== Benchmark Summary ===
Problem               | Status | Plan Len | Time (s) |  CPU % | Mem Δ (KB) | Peak Mem (KB)
------------------------------------------------------------------------------------------
scenario_1_multiscale | ✅      |       12 |    0.001s |    0.0% |      112.0 |       25040.0
```

### Failed Run Example

```
Running benchmarks for example_domain using Thread-Safe Sessions planning...
Solving scenario_1...

=== example_domain Benchmark Results ===

=== Benchmark Summary ===
Problem    | Status | Plan Len | Time (s) |  CPU % | Mem Δ (KB) | Peak Mem (KB)
-------------------------------------------------------------------------------
scenario_1 | ❌      |        - |        - |      - |          - |             -

Note: Planning failed - no plan found
```

## Understanding the Output

### Output Columns

- **Problem** - Name of the scenario being tested
- **Status** - ✅ for success, ❌ for failure
- **Plan Len** - Number of primitive actions in the generated plan
- **Time (s)** - Time taken to find the plan (in seconds)
- **CPU %** - CPU usage percentage during planning
- **Mem Δ (KB)** - Memory change during planning (in kilobytes)
- **Peak Mem (KB)** - Peak memory usage during planning (in kilobytes)

### Success Indicators

- **✅** - Problem ran successfully and found a plan
- **Plan Len** shows the number of actions
- **Time (s)** shows planning duration

### Failure Indicators

- **❌** - Problem failed to find a plan or encountered an error
- Columns show `-` for unavailable metrics
- Error message may appear below the table

## Adding New Examples to the Benchmarking Suite

To add a new MCP orchestration example:

1. **Create a new subdirectory** under `mcp-orchestration/` following the **GTPyhop 1.7.0+ style guide**:
   ```
   mcp-orchestration/
   ├── bio_opentrons/
   ├── your_new_example/        # New example directory
   │   ├── domain.py             # Required: domain creation + actions + methods
   │   ├── problems.py           # Required: defines problems with unified scenario blocks
   │   ├── __init__.py           # Required: exports domain and get_problems()
   │   └── README.md             # Optional but recommended
   └── benchmarking.py
   ```

2. **Required files**:
   - `domain.py` - Must create domain, define all actions and methods following the [domain style guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_domain_style_guide.md)
   - `problems.py` - Must define problems using unified scenario blocks following the [problems style guide](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_problems_style_guide.md)
   - `__init__.py` - Must export `the_domain` and implement `get_problems()` function

3. **Required structure in `problems.py`** (Unified Scenario Block format):
   ```python
   problems = {}

   # BEGIN: Domain: your_domain_name

   # BEGIN: Scenario: scenario_1
   # Configuration
   _param1, _param2 = value1, value2

   # State
   initial_state_scenario_1 = State('scenario_1')
   initial_state_scenario_1.property1 = _param1

   # Problem
   problems['scenario_1'] = (
       initial_state_scenario_1,
       [('m_top_level_method', _param1, _param2)],
       'Description of scenario -> N actions'
   )
   # END: Scenario

   # END: Domain

   def get_problems():
       return problems
   ```

4. **Required structure in `__init__.py`**:
   ```python
   from . import domain
   from . import problems

   the_domain = domain.the_domain

   def get_problems():
       """Return all problem definitions for benchmarking."""
       return problems.get_problems()
   ```

5. **Run the benchmarking script** - It will automatically discover and run your new example:
   ```bash
   python benchmarking.py your_new_example
   ```

## Customizing the Benchmarking Script

### Changing the Top-Level Task

The top-level task is defined in each domain's `problems.py` file within each scenario block. Edit the `# Problem` section:

```python
# BEGIN: Scenario: scenario_1
# Configuration
_param = value

# State
initial_state_scenario_1 = State('scenario_1')
initial_state_scenario_1.property = _param

# Problem
problems['scenario_1'] = (
    initial_state_scenario_1,
    [('m_your_custom_task_name', _param)],  # Change this
    'Description -> N actions'
)
# END: Scenario
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
- `problems.py` with unified scenario blocks

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
from . import domain
from . import problems

the_domain = domain.the_domain

def get_problems():
    """Return all problem definitions for benchmarking."""
    return problems.get_problems()
```

And ensure your `problems.py` has:
```python
problems = {}

# ... scenario blocks ...

def get_problems():
    return problems
```

## Performance Tips

- Use `--verbose 0` for fastest benchmarking (minimal output overhead)
- Thread-safe sessions are used by default (recommended for GTPyhop 1.7.0+)
- Use `--legacy-mode` only if you need global state (slightly faster but not thread-safe)
- For large examples, consider increasing Python's recursion limit if needed

## Next Steps

- Review individual domain README.md files for detailed documentation
- Examine generated plans to understand task decomposition
- Modify problems to test different planning scenarios
- Add new examples following the GTPyhop 1.7.0+ new structure patterns for [domains](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_domain_style_guide.md) and [problems](https://github.com/PCfVW/GTPyhop/blob/pip/docs/gtpyhop_problems_style_guide.md)
- Explore the shared benchmarking infrastructure in `ipc-2020-total-order/benchmarking.py`

