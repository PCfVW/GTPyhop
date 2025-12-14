# GTPyhop 1.7.0+ Problems Style Guide

## How to Write Problem Files (Initial States and Goal Tasks) for GTPyhop 1.7.0+ (LibCST-Compatible Format)

**Version**: 2.1.0
**Target Audience**: Domain developers writing GTPyhop 1.7.0+ problem files
**Purpose**: Enable automated extraction of scenarios with configuration variables and problem metadata using Meta's LibCST tool for database ingestion

---

## Table of Contents

1. [Introduction and Purpose](#1-introduction-and-purpose)
2. [File Structure Overview](#2-file-structure-overview)
3. [Unified Scenario Block Structure](#3-unified-scenario-block-structure)
4. [Naming Conventions](#4-naming-conventions)
5. [Documentation Requirements](#5-documentation-requirements)
6. [Comment Marker Conventions for LibCST](#6-comment-marker-conventions-for-libcst)
7. [Configuration Variables](#7-configuration-variables)
8. [Complete Working Examples](#8-complete-working-examples)
9. [Common Patterns](#9-common-patterns)
10. [Anti-patterns](#10-anti-patterns)
11. [Validation Checklist](#11-validation-checklist)
12. [BNF Grammar Specification](#12-bnf-grammar-specification)

---

## 1. Introduction and Purpose

This style guide defines **mandatory conventions** for writing GTPyhop 1.7.0+ problem files (`problems.py`). Following these conventions enables:

1. **Automated parsing** using Meta's LibCST tool
2. **Database ingestion** of scenarios with configuration variables
3. **AI assistant integration** via MCP (Model Context Protocol) tools
4. **Consistency** across domain implementations
5. **Validation** of problem file correctness before runtime

### What's New in Version 2.0.0

This version introduces the **Unified Scenario Block** pattern which:
- Combines initial state definition and problem registration in one block
- Supports **configuration variables** for parameterized scenarios
- Uses `problems['key']` subscript assignment instead of a separate dictionary section
- Enables direct extraction of self-contained scenario units

### Scope

This guide covers:
- **Problem Files**: Files defining initial states and goal tasks for planning
- **Unified Scenario Blocks**: Self-contained blocks with configuration, state, and problem definition
- **Configuration Variables**: Parameterized values that can be varied per scenario

### Reference Files

This guide is derived from analysis of:
- `drug_target_discovery/problems.py` (3 scenarios)
- `mock_servers/problems.py` (6 scenarios)
- `omega_hdq_dna_bacteria_flex_96_channel/problems.py` (3 scenarios)

---

## 2. File Structure Overview

### 2.1 Required File Sections

A compliant `problems.py` file MUST contain these sections in order:

| Section | Purpose | Required |
|---------|---------|----------|
| **Module Docstring** | File description with generation date | ✅ Yes |
| **Imports** | GTPyhop and standard library imports | ✅ Yes |
| **Helper Functions** | Factory functions for state creation (if needed) | ⚠️ Optional |
| **Problems Dictionary Init** | `problems = {}` declaration | ✅ Yes |
| **Unified Scenario Blocks** | Domain and Scenario markers with embedded `problems['key']` | ✅ Yes |
| **get_problems() Function** | Returns problems dictionary for benchmarking | ✅ Yes |

### 2.2 File Organization Template

```python
"""
Problem definitions for the [Domain Name] example.
-- Generated YYYY-MM-DD

This file defines initial states for [workflow description].
The workflow demonstrates coordination between [N] MCP servers:
  - Server 1 (name): Description
  - Server 2 (name): Description
  ...
"""

import sys
import os

# Secure GTPyhop import strategy
try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    # Fallback to local development
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        import gtpyhop
        from gtpyhop import State
    except ImportError as e:
        print(f"Error: Could not import gtpyhop: {e}")
        print("Please install gtpyhop using: pip install gtpyhop")
        sys.exit(1)


# ============================================================================
# HELPER FUNCTION (optional)
# ============================================================================

def h_create_base_state(name: str) -> State:
    """Create a base state with common properties."""
    state = State(name)
    # ... initialize common properties ...
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: domain_name

# BEGIN: Scenario: scenario_1
# Configuration
_param1, _param2 = 4, 25

# State
initial_state_scenario_1 = h_create_base_state('scenario_1')
initial_state_scenario_1.param1 = _param1
initial_state_scenario_1.param2 = _param2

# Problem
problems['scenario_1'] = (
    initial_state_scenario_1,
    [('m_top_level_method', _param1, _param2)],
    f'Description: {_param1} units, {_param2} cycles -> N actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2
# Configuration
_param1, _param2 = 8, 30

# State
initial_state_scenario_2 = h_create_base_state('scenario_2')
initial_state_scenario_2.param1 = _param1
initial_state_scenario_2.param2 = _param2

# Problem
problems['scenario_2'] = (
    initial_state_scenario_2,
    [('m_top_level_method', _param1, _param2)],
    f'Description: {_param1} units, {_param2} cycles -> N actions'
)
# END: Scenario

# END: Domain


def get_problems():
    """
    Return all problem definitions for benchmarking.

    Returns:
        Dictionary mapping problem IDs to (state, tasks, description) tuples.
    """
    return problems
```

---

## 3. Unified Scenario Block Structure

### 3.1 Block Components

Each unified scenario block MUST contain these components in order:

| Component | Description | Example |
|-----------|-------------|---------|
| **BEGIN Marker** | Scenario extraction marker | `# BEGIN: Scenario: scenario_name` |
| **Configuration** | Optional config variables section | `_samples, _cycles = 4, 25` |
| **State Section** | State creation and property assignment | `initial_state = h_create_state('name')` |
| **Problem Section** | Subscript assignment to problems dict | `problems['key'] = (state, tasks, desc)` |
| **END Marker** | Closes the scenario block | `# END: Scenario` |

### 3.2 Configuration Variables

Configuration variables are prefixed with underscore (`_`) and defined at the top of each scenario block:

```python
# Single value
_num_samples = 4

# Multiple values via tuple unpacking
_samples, _cycles = 4, 25

# Complex configuration
_disease_name = "breast cancer"
_target_count = 5
```

### 3.3 Problem Subscript Assignment

Each scenario registers itself in the `problems` dictionary using subscript assignment:

```python
problems['scenario_key'] = (
    initial_state_object,           # State object
    [('m_method_name', _arg1, _arg2)],  # Goal task list (can reference config vars)
    f'Description: {_arg1} units'    # Description (can use f-string with config vars)
)
```

---

## 4. Naming Conventions

### 4.1 Configuration Variable Names

**Pattern**: `_lowercase_with_underscores`

| Convention | Example |
|------------|---------|
| Leading underscore | `_samples`, `_cycles` |
| Descriptive name | `_num_washes`, `_disease_name` |

**Examples**:
- `_samples = 4`
- `_samples, _cycles = 4, 25`
- `_disease_name = "breast cancer"`

### 4.2 Scenario Variable Names

**Pattern**: `initial_state_scenario_N` or `initial_state_scenario_N_descriptor`

| Component | Convention | Example |
|-----------|------------|---------|
| Prefix | `initial_state_` | `initial_state_` |
| Scenario Number | `scenario_N` | `scenario_1`, `scenario_2` |
| Descriptor | `_descriptor` (optional) | `_standard`, `_dry_run` |

**Examples**:
- `initial_state_scenario_1`
- `initial_state_scenario_1_standard`
- `initial_state_scenario_2_dry_run`

### 4.3 State Name Strings

**Pattern**: `scenario_N` or `scenario_N_descriptor`

**Examples**:
- `'scenario_1'`
- `'scenario_1_standard'`
- `'scenario_2_dry_run'`

### 4.4 Problem Dictionary Keys

**Pattern**: `scenario_N` or `scenario_N_descriptor` (matches state name)

**Examples**:
- `'scenario_1'`
- `'scenario_1_standard'`
- `'scenario_2_dry_run'`

---

## 5. Documentation Requirements

### 5.1 Module Docstring Requirements

| Element | Required | Description |
|---------|----------|-------------|
| **Title** | ✅ Yes | "Problem definitions for the [Domain] example." |
| **Generation Date** | ✅ Yes | "-- Generated YYYY-MM-DD" |
| **Description** | ✅ Yes | Brief workflow description |
| **Server List** | ⚠️ If applicable | MCP servers involved |
| **Scenario List** | ✅ Yes | All scenarios with expected plan lengths |

### 5.2 Scenario Documentation

Each scenario MUST include:

1. **BEGIN/END Scenario Markers** for LibCST extraction
2. **Configuration variables** section (if parameterized)
3. **Expected plan length** in the problem description

---

## 6. Comment Marker Conventions for LibCST

### 6.1 Domain Markers

```python
# BEGIN: Domain: domain_name
# ... all scenarios ...
# END: Domain
```

### 6.2 Unified Scenario Markers (Version 2.0)

```python
# BEGIN: Scenario: scenario_name
# Configuration
_param1, _param2 = 4, 25

# State
initial_state_scenario_N = h_create_state('scenario_name')
initial_state_scenario_N.property = _param1

# Problem
problems['scenario_name'] = (
    initial_state_scenario_N,
    [('m_method', _param1, _param2)],
    f'Description: {_param1} units -> N actions'
)
# END: Scenario
```

### 6.3 Marker Syntax Rules

| Rule | Description |
|------|-------------|
| **Exact format** | `# BEGIN: Scenario: ` and `# END: Scenario` |
| **Scenario name** | Must match problems dict key and State constructor argument |
| **Domain name** | Must match directory name exactly |
| **No nesting** | Scenario blocks cannot be nested within each other |
| **Order** | Configuration → State → Problem within each block |

---

## 7. Configuration Variables

### 7.1 Purpose

Configuration variables enable:
- **Parameterized scenarios** with different values
- **Variable substitution** in task lists
- **F-string interpolation** in descriptions
- **Direct extraction** by LibCST parsers

### 7.2 Syntax Rules

| Rule | Description |
|------|-------------|
| **Naming** | Must start with underscore: `_name` |
| **Scope** | Local to the scenario block |
| **Types** | int, float, str, tuple (basic Python types) |
| **Assignment** | Simple assignment or tuple unpacking |

### 7.3 Examples

```python
# Single variable
_num_samples = 4

# Tuple unpacking
_samples, _cycles = 4, 25

# String value
_disease = "breast cancer"

# Usage in task list (as variable reference)
[('m_run_pcr', _samples, _cycles)]

# Usage in description (as f-string)
f'PCR: {_samples} samples, {_cycles} cycles'
```

---

## 8. Complete Working Examples

### 8.1 Simple Problem File (1 scenario)

```python
"""
Problem definitions for the TNF Cancer Modeling example.
-- Generated 2025-12-09

This file defines initial states for the multiscale TNF cancer modeling workflow.
"""

import sys
import os

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State

# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: tnf_cancer_modelling

# BEGIN: Scenario: scenario_1_multiscale
# Configuration
_gene_list = ["TNF", "TNFR1", "NFKB1"]

# State
initial_state_scenario_1 = State('scenario_1_multiscale')
initial_state_scenario_1.tnf_gene_list = _gene_list
initial_state_scenario_1.omnipath_available = True

# Problem
problems['scenario_1_multiscale'] = (
    initial_state_scenario_1,
    [('m_run_multiscale_workflow',)],
    'Multiscale TNF cancer modeling workflow'
)
# END: Scenario

# END: Domain


def get_problems():
    """Return all problem definitions for benchmarking."""
    return problems
```

### 8.2 Multi-Scenario Problem File with Configuration Variables

```python
"""
Problem definitions for the PCR Workflow example.
-- Generated 2025-12-09

Scenarios:
  - scenario_1: 4 samples, 25 cycles -> 55 actions
  - scenario_2: 8 samples, 30 cycles -> 79 actions
"""

import sys
import os

try:
    import gtpyhop
    from gtpyhop import State
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    import gtpyhop
    from gtpyhop import State


def h_create_base_state(name: str) -> State:
    """Helper: Create base PCR state."""
    state = State(name)
    state.deck_slots = {}
    state.pipette_ready = {'left': False, 'right': False}
    return state


# ============================================================================
# SCENARIOS
# ============================================================================

problems = {}

# BEGIN: Domain: pcr_workflow

# BEGIN: Scenario: scenario_1
# Configuration
_samples, _cycles = 4, 25

# State
initial_state_scenario_1 = h_create_base_state('scenario_1')
initial_state_scenario_1.num_samples = _samples
initial_state_scenario_1.num_cycles = _cycles

# Problem
problems['scenario_1'] = (
    initial_state_scenario_1,
    [('m_initialize_and_run_pcr', _samples, _cycles)],
    f'PCR: {_samples} samples, {_cycles} cycles -> 55 actions'
)
# END: Scenario

# BEGIN: Scenario: scenario_2
# Configuration
_samples, _cycles = 8, 30

# State
initial_state_scenario_2 = h_create_base_state('scenario_2')
initial_state_scenario_2.num_samples = _samples
initial_state_scenario_2.num_cycles = _cycles

# Problem
problems['scenario_2'] = (
    initial_state_scenario_2,
    [('m_initialize_and_run_pcr', _samples, _cycles)],
    f'PCR: {_samples} samples, {_cycles} cycles -> 79 actions'
)
# END: Scenario

# END: Domain


def get_problems():
    """Return all problem definitions for benchmarking."""
    return problems
```

---

## 9. Common Patterns

### 9.1 Factory Function Pattern

Use helper functions (prefixed with `h_`) when scenarios share common base properties:

```python
def h_create_base_state(name: str) -> State:
    state = State(name)
    # Common initialization
    return state

# BEGIN: Scenario: scenario_1
initial_state_scenario_1 = h_create_base_state('scenario_1')
initial_state_scenario_1.variant_property = 'value_1'
problems['scenario_1'] = (initial_state_scenario_1, [...], 'Description')
# END: Scenario
```

### 9.2 Configuration Variable Pattern

Use configuration variables for parameterized scenarios:

```python
# BEGIN: Scenario: scenario_1_standard
# Configuration
_dry_run = False
_num_washes = 3

# State
initial_state_scenario_1 = h_create_base_state('scenario_1_standard')
initial_state_scenario_1.dry_run = _dry_run
initial_state_scenario_1.num_washes = _num_washes

# Problem
problems['scenario_1_standard'] = (
    initial_state_scenario_1,
    [('m_extraction', _num_washes)],
    f'Standard extraction: {_num_washes} washes'
)
# END: Scenario
```

---

## 10. Anti-patterns

### 10.1 Missing Scenario Markers

```python
# ❌ INCORRECT - No BEGIN/END markers
initial_state_scenario_1 = State('test')
initial_state_scenario_1.value = 1
problems['test'] = (initial_state_scenario_1, [...], 'Desc')

# ✅ CORRECT - Proper scenario markers
# BEGIN: Scenario: test
initial_state_scenario_1 = State('test')
initial_state_scenario_1.value = 1
problems['test'] = (initial_state_scenario_1, [...], 'Desc')
# END: Scenario
```

### 10.2 Inconsistent Naming

```python
# ❌ INCORRECT - Inconsistent patterns
state1 = State('first')
second_state = State('second')

# ✅ CORRECT - Consistent pattern
initial_state_scenario_1 = State('scenario_1')
initial_state_scenario_2 = State('scenario_2')
```

### 10.3 Incorrect problems Dictionary Format

```python
# ❌ INCORRECT - Missing description
problems['scenario_1'] = (initial_state_scenario_1, [('task',)])

# ✅ CORRECT - (state, tasks, description)
problems['scenario_1'] = (initial_state_scenario_1, [('task',)], 'Description')
```

### 10.4 Separate problems Dictionary (Old Style)

```python
# ❌ OLD STYLE - Separate dictionary definition
# BEGIN: Initial State: test
initial_state = State('test')
# END: Initial State

problems = {
    'test': (initial_state, [...], 'Desc')
}

# ✅ NEW STYLE - Subscript assignment within scenario block
problems = {}

# BEGIN: Scenario: test
initial_state = State('test')
problems['test'] = (initial_state, [...], 'Desc')
# END: Scenario
```

---

## 11. Validation Checklist

### 11.1 File Structure
- [ ] Module docstring with generation date present
- [ ] GTPyhop import with fallback strategy
- [ ] `problems = {}` declaration before domain block
- [ ] `get_problems()` function defined at end

### 11.2 Domain Markers
- [ ] `# BEGIN: Domain: domain_name` present
- [ ] `# END: Domain` present (after all scenarios)
- [ ] Domain name matches directory name

### 11.3 Each Scenario Block
- [ ] `# BEGIN: Scenario: scenario_name` present
- [ ] Configuration variables section (if parameterized)
- [ ] State creation with `h_` helper or direct `State()`
- [ ] `problems['key'] = (state, tasks, description)` subscript assignment
- [ ] `# END: Scenario` present
- [ ] Scenario name matches problems key and State name

---

## 12. BNF Grammar Specification

### 12.1 Problem File Grammar (EBNF)

```ebnf
problem_file        = docstring imports [helper_functions] problems_init
                      domain_block get_problems_func ;

docstring           = '"""' file_description gen_date workflow_desc '"""' ;
gen_date            = "-- Generated" DATE NEWLINE ;

problems_init       = "problems" "=" "{" "}" ;

domain_block        = domain_begin {scenario_block} domain_end ;
domain_begin        = "# BEGIN: Domain:" domain_name NEWLINE ;
domain_end          = "# END: Domain" NEWLINE ;

scenario_block      = scenario_begin [config_section] state_section
                      problem_section scenario_end ;
scenario_begin      = "# BEGIN: Scenario:" scenario_name NEWLINE ;
scenario_end        = "# END: Scenario" NEWLINE ;

config_section      = "# Configuration" NEWLINE {config_assignment} ;
config_assignment   = config_var "=" expression NEWLINE
                    | config_vars "=" expressions NEWLINE ;
config_var          = "_" IDENTIFIER ;
config_vars         = config_var {"," config_var} ;

state_section       = "# State" NEWLINE state_creation {property_assignment} ;
state_creation      = state_var "=" helper_call | state_var "=" "State" "(" STRING ")" ;
property_assignment = state_var "." IDENTIFIER "=" expression NEWLINE ;

problem_section     = "# Problem" NEWLINE subscript_assignment ;
subscript_assignment = "problems" "[" STRING "]" "=" problem_tuple ;
problem_tuple       = "(" state_var "," task_list "," description ")" ;
task_list           = "[" {task_tuple ","} "]" ;
task_tuple          = "(" STRING {"," expression} ")" ;
```

### 12.2 Marker Grammar

```ebnf
domain_marker       = "# BEGIN: Domain:" SPACE domain_name
                    | "# END: Domain" ;

scenario_marker     = "# BEGIN: Scenario:" SPACE scenario_name
                    | "# END: Scenario" ;
```

---

*Document Version: 2.0.0*
*Generated: 2025-12-09*
*Based on: Unified Scenario Block structure (Alternative D)*
